import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

import anthropic
from app.core.config import settings
from app.db.models import Transaction, Category, User, Insight
from app.models.schemas import (
    CategoryPrediction,
    PredictionResponse,
    DailyTipResponse,
    BatchJobResponse,
)

logger = logging.getLogger(__name__)


def generate_spend_prediction(
    db: Session,
    user_id: int,
    months_window: int = 6
) -> PredictionResponse:
    """
    Forecasts next month's spend per category using linear trend regression / moving average
    over the last 3-6 months, generates a 1-line LLM explanation, and saves the insight into DB.
    """
    ref_date = date.today()
    start_lookback = ref_date - timedelta(days=months_window * 31)

    records = (
        db.query(
            Transaction.date,
            Transaction.amount,
            Category.name.label("category_name")
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "debit",
            Transaction.date >= start_lookback
        )
        .all()
    )

    # Next month label
    if ref_date.month == 12:
        forecast_year = ref_date.year + 1
        forecast_month_num = 1
    else:
        forecast_year = ref_date.year
        forecast_month_num = ref_date.month + 1

    forecast_month = f"{forecast_year}-{str(forecast_month_num).zfill(2)}"

    if not records:
        empty_explanation = f"No historical spend data available to forecast predictions for {forecast_month}."
        res = PredictionResponse(
            user_id=user_id,
            forecast_month=forecast_month,
            total_predicted_spend=0.0,
            explanation=empty_explanation,
            category_predictions=[],
            created_at=datetime.utcnow(),
            is_llm_generated=False
        )
        _save_insight_to_db(
            db, user_id, "prediction", f"Spend Forecast: {forecast_month}", empty_explanation, res.model_dump_json()
        )
        return res

    df = pd.DataFrame(
        [
            {
                "date": r.date,
                "amount": float(r.amount),
                "category_name": r.category_name or "Uncategorized"
            }
            for r in records
        ]
    )
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")

    # Monthly spend per category matrix
    monthly_cat = df.groupby(["month", "category_name"])["amount"].sum().unstack(fill_value=0.0)

    category_predictions: List[CategoryPrediction] = []
    total_predicted = 0.0

    all_months = sorted(monthly_cat.index.tolist())
    n_months = len(all_months)

    for cat in monthly_cat.columns:
        series = monthly_cat[cat].values
        avg_spend = round(float(np.mean(series)), 2)

        if n_months >= 2 and np.sum(series) > 0:
            # Linear trend fit (y = a*x + b)
            x = np.arange(n_months)
            poly = np.polyfit(x, series, 1)
            slope, intercept = poly[0], poly[1]

            pred_val = float(slope * n_months + intercept)
            pred_val = round(max(0.0, pred_val), 2)

            if slope > (0.05 * (avg_spend or 1.0)):
                trend_dir = "upward"
            elif slope < (-0.05 * (avg_spend or 1.0)):
                trend_dir = "downward"
            else:
                trend_dir = "stable"

            pct_change = round(((pred_val - avg_spend) / avg_spend) * 100, 2) if avg_spend > 0 else None
        else:
            pred_val = avg_spend
            trend_dir = "stable"
            pct_change = 0.0

        total_predicted += pred_val
        category_predictions.append(
            CategoryPrediction(
                category_name=cat,
                predicted_spend=pred_val,
                avg_monthly_spend=avg_spend,
                trend_direction=trend_dir,
                percentage_change=pct_change
            )
        )

    category_predictions.sort(key=lambda x: x.predicted_spend, reverse=True)
    total_predicted = round(total_predicted, 2)

    # Generate 1-line LLM explanation
    is_llm = False
    cat_summary_lines = [
        f"{cp.category_name}: predicted ${cp.predicted_spend:.2f} (avg ${cp.avg_monthly_spend:.2f}, {cp.trend_direction} trend)"
        for cp in category_predictions[:3]
    ]
    cat_summary_text = "; ".join(cat_summary_lines)

    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip() != "":
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            prompt = (
                f"You are Coinsy, a personal finance AI. Write EXACTLY ONE concise sentence explaining next month's spending forecast.\n"
                f"- Forecast Month: {forecast_month}\n"
                f"- Total Predicted Spend: ${total_predicted:.2f}\n"
                f"- Category Trends: {cat_summary_text}\n\n"
                f"Output ONLY one clear sentence (no bullet points, no titles)."
            )
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            explanation = response.content[0].text.strip().replace("\n", " ")
            is_llm = True
        except Exception as e:
            logger.error(f"Error generating LLM prediction explanation: {e}")
            explanation = _fallback_prediction_explanation(forecast_month, total_predicted, category_predictions)
    else:
        explanation = _fallback_prediction_explanation(forecast_month, total_predicted, category_predictions)

    response_obj = PredictionResponse(
        user_id=user_id,
        forecast_month=forecast_month,
        total_predicted_spend=total_predicted,
        explanation=explanation,
        category_predictions=category_predictions,
        created_at=datetime.utcnow(),
        is_llm_generated=is_llm
    )

    _save_insight_to_db(
        db, user_id, "prediction", f"Spend Forecast: {forecast_month}", explanation, response_obj.model_dump_json()
    )
    return response_obj


def _fallback_prediction_explanation(
    forecast_month: str,
    total_predicted: float,
    category_preds: List[CategoryPrediction]
) -> str:
    if not category_preds:
        return f"Total spend for {forecast_month} is projected at ${total_predicted:.2f} based on historical trends."

    top_cp = category_preds[0]
    trend_phrase = "an upward trend" if top_cp.trend_direction == "upward" else ("a downward trend" if top_cp.trend_direction == "downward" else "stable spending")
    return (
        f"Spend for {forecast_month} is projected at ${total_predicted:.2f}, "
        f"driven by {trend_phrase} in {top_cp.category_name} (${top_cp.predicted_spend:.2f})."
    )


def generate_daily_tip(db: Session, user_id: int) -> DailyTipResponse:
    """
    Summarizes the last 30 days of transactions and generates one short, specific, non-generic tip.
    Saves insight into DB.
    """
    cutoff_date = date.today() - timedelta(days=30)

    records = (
        db.query(
            Transaction.date,
            Transaction.amount,
            Transaction.description,
            Transaction.merchant_name,
            Category.name.label("category_name")
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "debit",
            Transaction.date >= cutoff_date
        )
        .all()
    )

    if not records:
        tip_text = "No transactions recorded in the last 30 days. Log your daily expenses to receive customized personal finance tips!"
        res = DailyTipResponse(
            user_id=user_id,
            tip=tip_text,
            total_30d_spend=0.0,
            top_category=None,
            created_at=datetime.utcnow(),
            is_llm_generated=False
        )
        _save_insight_to_db(db, user_id, "daily_tip", "Daily Spending Tip", tip_text, res.model_dump_json())
        return res

    df = pd.DataFrame(
        [
            {
                "amount": float(r.amount),
                "description": r.description or "",
                "merchant": r.merchant_name or "",
                "category": r.category_name or "Uncategorized"
            }
            for r in records
        ]
    )

    total_spend = round(float(df["amount"].sum()), 2)
    tx_count = len(df)

    cat_grouped = df.groupby("category")["amount"].agg(["sum", "count"]).reset_index()
    cat_grouped.sort_values(by="sum", ascending=False, inplace=True)

    top_cat = cat_grouped.iloc[0]["category"]
    top_cat_amt = round(float(cat_grouped.iloc[0]["sum"]), 2)
    top_cat_count = int(cat_grouped.iloc[0]["count"])

    # Merchant frequency analysis
    df["vendor"] = df["merchant"].replace("", np.nan).fillna(df["description"])
    vendor_counts = df["vendor"].value_counts()
    top_vendor = vendor_counts.index[0] if not vendor_counts.empty else top_cat
    top_vendor_count = int(vendor_counts.iloc[0]) if not vendor_counts.empty else 1

    is_llm = False

    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip() != "":
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            prompt = (
                f"You are Coinsy, an expert personal finance mascot. "
                f"Analyze the user's spending data over the last 30 days:\n"
                f"- Total Spend: ${total_spend:.2f} across {tx_count} transactions\n"
                f"- Top Spending Category: '{top_cat}' (${top_cat_amt:.2f}, {top_cat_count} transactions)\n"
                f"- Frequent Merchant/Description: '{top_vendor}' ({top_vendor_count} visits/orders)\n\n"
                f"Write EXACTLY ONE short, specific, non-generic daily financial tip (1-2 sentences). "
                f"CRITICAL: Reference specific numbers, category names, or merchant names from their data above. "
                f"DO NOT give generic advice like 'create a budget' or 'save money'."
            )
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            tip_text = response.content[0].text.strip().replace("\n", " ")
            is_llm = True
        except Exception as e:
            logger.error(f"Error generating LLM daily tip: {e}")
            tip_text = _fallback_daily_tip(top_cat, top_cat_amt, top_cat_count, top_vendor, top_vendor_count)
    else:
        tip_text = _fallback_daily_tip(top_cat, top_cat_amt, top_cat_count, top_vendor, top_vendor_count)

    response_obj = DailyTipResponse(
        user_id=user_id,
        tip=tip_text,
        total_30d_spend=total_spend,
        top_category=top_cat,
        created_at=datetime.utcnow(),
        is_llm_generated=is_llm
    )

    _save_insight_to_db(db, user_id, "daily_tip", "Daily Spending Tip", tip_text, response_obj.model_dump_json())
    return response_obj


def _fallback_daily_tip(
    top_cat: str,
    top_cat_amt: float,
    top_cat_count: int,
    top_vendor: str,
    top_vendor_count: int
) -> str:
    if top_vendor_count > 3 and top_vendor:
        suggested_limit = round((top_cat_amt * 0.75), 2)
        return (
            f"You spent ${top_cat_amt:.2f} on {top_cat} across {top_cat_count} transactions (including {top_vendor_count} orders at {top_vendor}) "
            f"in the last 30 days—capping {top_cat} at ${suggested_limit:.2f} next month could save you ~${(top_cat_amt - suggested_limit):.2f}!"
        )

    suggested_limit = round(top_cat_amt * 0.8, 2)
    return (
        f"Your highest spending category in the past 30 days was {top_cat} (${top_cat_amt:.2f} across {top_cat_count} transactions); "
        f"trimming this category by 20% could save you ${top_cat_amt - suggested_limit:.2f} next month."
    )


def _save_insight_to_db(
    db: Session,
    user_id: int,
    insight_type: str,
    title: str,
    content: str,
    metadata_json: str
):
    """
    Saves or updates pre-computed insight in SQLite DB.
    """
    try:
        existing = (
            db.query(Insight)
            .filter(Insight.user_id == user_id, Insight.type == insight_type)
            .order_by(Insight.created_at.desc())
            .first()
        )
        if existing:
            existing.title = title
            existing.content = content
            existing.metadata_json = metadata_json
            existing.created_at = datetime.utcnow()
        else:
            new_insight = Insight(
                user_id=user_id,
                type=insight_type,
                title=title,
                content=content,
                metadata_json=metadata_json,
                created_at=datetime.utcnow()
            )
            db.add(new_insight)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save insight to DB: {e}")


def get_latest_prediction(db: Session, user_id: int, force_refresh: bool = False) -> PredictionResponse:
    """
    Fetches pre-computed spend prediction from DB, or triggers generation if missing/forced.
    """
    if not force_refresh:
        insight = (
            db.query(Insight)
            .filter(Insight.user_id == user_id, Insight.type == "prediction")
            .order_by(Insight.created_at.desc())
            .first()
        )
        if insight and insight.metadata_json:
            try:
                data = json.loads(insight.metadata_json)
                return PredictionResponse(**data)
            except Exception as e:
                logger.warning(f"Could not parse stored prediction insight JSON: {e}")

    return generate_spend_prediction(db, user_id=user_id)


def get_latest_daily_tip(db: Session, user_id: int, force_refresh: bool = False) -> DailyTipResponse:
    """
    Fetches pre-computed daily tip from DB, or triggers generation if missing/forced.
    """
    if not force_refresh:
        insight = (
            db.query(Insight)
            .filter(Insight.user_id == user_id, Insight.type == "daily_tip")
            .order_by(Insight.created_at.desc())
            .first()
        )
        if insight and insight.metadata_json:
            try:
                data = json.loads(insight.metadata_json)
                return DailyTipResponse(**data)
            except Exception as e:
                logger.warning(f"Could not parse stored daily tip insight JSON: {e}")

    return generate_daily_tip(db, user_id=user_id)


def run_batch_insights_job(db: Session, user_id: Optional[int] = None) -> BatchJobResponse:
    """
    Batch job execution: iterates active users, computes spend prediction & daily tip,
    and persists pre-computed insights to DB.
    """
    if user_id is not None:
        user_ids = [user_id]
    else:
        users = db.query(User.id).all()
        user_ids = [u.id for u in users]

    processed = 0
    for uid in user_ids:
        try:
            generate_spend_prediction(db, user_id=uid)
            generate_daily_tip(db, user_id=uid)
            processed += 1
        except Exception as e:
            logger.error(f"Error processing batch insights for user {uid}: {e}")

    return BatchJobResponse(
        status="success",
        users_processed=processed,
        timestamp=datetime.utcnow()
    )
