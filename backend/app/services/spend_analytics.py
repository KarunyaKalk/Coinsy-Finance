import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from sqlalchemy.orm import Session

import anthropic
from app.core.config import settings
from app.db.models import Transaction, Category
from app.models.schemas import (
    CategorySpend,
    TimePeriodSpendBreakdown,
    SpendAggregationResponse,
    CategoryComparison,
    PeriodComparisonResponse,
    SpendSummaryResponse,
)

logger = logging.getLogger(__name__)


def _load_transactions_dataframe(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> pd.DataFrame:
    """
    Loads debit transactions from DB into a Pandas DataFrame.
    """
    query = (
        db.query(
            Transaction.id,
            Transaction.date,
            Transaction.amount,
            Transaction.type,
            Transaction.user_id,
            Category.name.label("category_name")
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(Transaction.type == "debit")
    )

    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    if start_date is not None:
        query = query.filter(Transaction.date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.date <= end_date)

    records = query.all()

    if not records:
        return pd.DataFrame(columns=["id", "date", "amount", "type", "user_id", "category_name"])

    df = pd.DataFrame(
        [
            {
                "id": r.id,
                "date": r.date,
                "amount": float(r.amount),
                "type": r.type,
                "user_id": r.user_id,
                "category_name": r.category_name or "Uncategorized",
            }
            for r in records
        ]
    )

    df["date"] = pd.to_datetime(df["date"])
    return df


def get_spend_aggregation(
    db: Session,
    timeframe: str = "monthly",  # weekly | monthly | yearly
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> SpendAggregationResponse:
    """
    Aggregates spend by timeframe (weekly, monthly, yearly) and category using Pandas.
    """
    df = _load_transactions_dataframe(db, user_id=user_id, start_date=start_date, end_date=end_date)

    timeframe = timeframe.lower()
    if timeframe not in ["weekly", "monthly", "yearly"]:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Must be 'weekly', 'monthly', or 'yearly'.")

    if df.empty:
        return SpendAggregationResponse(
            timeframe=timeframe,
            total_spend=0.0,
            category_totals=[],
            periods=[]
        )

    # Compute timeframe period label using Pandas dt formatting
    if timeframe == "weekly":
        # ISO week: YYYY-Www
        df["period"] = (
            df["date"].dt.isocalendar().year.astype(str)
            + "-W"
            + df["date"].dt.isocalendar().week.astype(str).str.zfill(2)
        )
    elif timeframe == "monthly":
        df["period"] = df["date"].dt.strftime("%Y-%m")
    else:  # yearly
        df["period"] = df["date"].dt.strftime("%Y")

    total_spend = round(float(df["amount"].sum()), 2)

    # Category totals overall
    cat_grouped = df.groupby("category_name")["amount"].sum().reset_index()
    category_totals = []
    for _, row in cat_grouped.iterrows():
        cat_amount = round(float(row["amount"]), 2)
        pct = round((cat_amount / total_spend) * 100, 2) if total_spend > 0 else 0.0
        category_totals.append(
            CategorySpend(
                category_name=row["category_name"],
                total_spend=cat_amount,
                percentage_of_total=pct
            )
        )
    category_totals.sort(key=lambda x: x.total_spend, reverse=True)

    # Breakdown by period and category
    period_cat_grouped = df.groupby(["period", "category_name"])["amount"].sum().reset_index()
    period_totals_map = df.groupby("period")["amount"].sum().to_dict()

    periods_list = []
    unique_periods = sorted(df["period"].unique())

    for period_str in unique_periods:
        period_total = round(float(period_totals_map.get(period_str, 0.0)), 2)
        period_df = period_cat_grouped[period_cat_grouped["period"] == period_str]

        period_categories = []
        for _, row in period_df.iterrows():
            c_amount = round(float(row["amount"]), 2)
            c_pct = round((c_amount / period_total) * 100, 2) if period_total > 0 else 0.0
            period_categories.append(
                CategorySpend(
                    category_name=row["category_name"],
                    total_spend=c_amount,
                    percentage_of_total=c_pct
                )
            )
        period_categories.sort(key=lambda x: x.total_spend, reverse=True)

        periods_list.append(
            TimePeriodSpendBreakdown(
                period=period_str,
                total_spend=period_total,
                categories=period_categories
            )
        )

    return SpendAggregationResponse(
        timeframe=timeframe,
        total_spend=total_spend,
        category_totals=category_totals,
        periods=periods_list
    )


def _get_target_and_prior_dates(
    period_type: str,
    target_date_input: Optional[date] = None
) -> Tuple[date, date, date, date, str, str]:
    """
    Returns (target_start, target_end, prior_start, prior_end, target_label, prior_label)
    """
    ref_date = target_date_input or date.today()

    if period_type == "mom":
        # Target month
        target_year = ref_date.year
        target_month = ref_date.month
        target_start = date(target_year, target_month, 1)

        # Target end date (last day of month)
        if target_month == 12:
            next_month_start = date(target_year + 1, 1, 1)
        else:
            next_month_start = date(target_year, target_month + 1, 1)
        target_end = next_month_start - timedelta(days=1)

        # Prior month
        if target_month == 1:
            prior_year = target_year - 1
            prior_month = 12
        else:
            prior_year = target_year
            prior_month = target_month - 1

        prior_start = date(prior_year, prior_month, 1)
        prior_end = target_start - timedelta(days=1)

        target_label = target_start.strftime("%Y-%m")
        prior_label = prior_start.strftime("%Y-%m")

    elif period_type == "wow":
        # Target week: Monday to Sunday containing ref_date
        target_start = ref_date - timedelta(days=ref_date.weekday())  # Monday
        target_end = target_start + timedelta(days=6)  # Sunday

        prior_start = target_start - timedelta(days=7)
        prior_end = target_start - timedelta(days=1)

        iso_target = target_start.isocalendar()
        iso_prior = prior_start.isocalendar()

        target_label = f"{iso_target.year}-W{str(iso_target.week).zfill(2)}"
        prior_label = f"{iso_prior.year}-W{str(iso_prior.week).zfill(2)}"

    else:
        raise ValueError(f"Invalid period_type '{period_type}'. Must be 'mom' or 'wow'.")

    return target_start, target_end, prior_start, prior_end, target_label, prior_label


def get_period_comparison(
    db: Session,
    period_type: str = "mom",  # mom | wow
    user_id: Optional[int] = None,
    target_date: Optional[date] = None
) -> PeriodComparisonResponse:
    """
    Computes Month-over-Month (MoM) or Week-over-Week (WoW) spend comparison using Pandas.
    """
    t_start, t_end, p_start, p_end, t_label, p_label = _get_target_and_prior_dates(
        period_type.lower(), target_date
    )

    df = _load_transactions_dataframe(db, user_id=user_id, start_date=p_start, end_date=t_end)

    if df.empty:
        return PeriodComparisonResponse(
            period_type=period_type.lower(),
            target_period=t_label,
            prior_period=p_label,
            total_current_spend=0.0,
            total_prior_spend=0.0,
            total_change_amount=0.0,
            total_percentage_change=0.0,
            trend="unchanged",
            categories=[]
        )

    # Classify period using Pandas
    def assign_period(dt):
        d = dt.date()
        if t_start <= d <= t_end:
            return "target"
        elif p_start <= d <= p_end:
            return "prior"
        return "other"

    df["period_bucket"] = df["date"].apply(assign_period)

    target_df = df[df["period_bucket"] == "target"]
    prior_df = df[df["period_bucket"] == "prior"]

    target_cat_spend = target_df.groupby("category_name")["amount"].sum().to_dict() if not target_df.empty else {}
    prior_cat_spend = prior_df.groupby("category_name")["amount"].sum().to_dict() if not prior_df.empty else {}

    all_categories = sorted(list(set(target_cat_spend.keys()).union(set(prior_cat_spend.keys()))))

    categories_comp = []
    total_curr = 0.0
    total_prior = 0.0

    for cat in all_categories:
        curr_val = round(float(target_cat_spend.get(cat, 0.0)), 2)
        prior_val = round(float(prior_cat_spend.get(cat, 0.0)), 2)

        total_curr += curr_val
        total_prior += prior_val

        change_amt = round(curr_val - prior_val, 2)

        if prior_val > 0:
            pct_change = round((change_amt / prior_val) * 100, 2)
        elif curr_val > 0:
            pct_change = None  # New category spend
        else:
            pct_change = 0.0

        if prior_val == 0 and curr_val > 0:
            trend = "new"
        elif change_amt > 0:
            trend = "increased"
        elif change_amt < 0:
            trend = "decreased"
        else:
            trend = "unchanged"

        categories_comp.append(
            CategoryComparison(
                category_name=cat,
                current_spend=curr_val,
                prior_spend=prior_val,
                change_amount=change_amt,
                percentage_change=pct_change,
                trend=trend
            )
        )

    categories_comp.sort(key=lambda x: abs(x.change_amount), reverse=True)

    total_curr = round(total_curr, 2)
    total_prior = round(total_prior, 2)
    total_diff = round(total_curr - total_prior, 2)

    if total_prior > 0:
        total_pct = round((total_diff / total_prior) * 100, 2)
    elif total_curr > 0:
        total_pct = None
    else:
        total_pct = 0.0

    if total_prior == 0 and total_curr > 0:
        total_trend = "new"
    elif total_diff > 0:
        total_trend = "increased"
    elif total_diff < 0:
        total_trend = "decreased"
    else:
        total_trend = "unchanged"

    return PeriodComparisonResponse(
        period_type=period_type.lower(),
        target_period=t_label,
        prior_period=p_label,
        total_current_spend=total_curr,
        total_prior_spend=total_prior,
        total_change_amount=total_diff,
        total_percentage_change=total_pct,
        trend=total_trend,
        categories=categories_comp
    )


def generate_spend_summary(
    db: Session,
    period_type: str = "mom",
    user_id: Optional[int] = None,
    target_date: Optional[date] = None
) -> SpendSummaryResponse:
    """
    Generates a natural-language text summary of spend changes using Claude LLM,
    with a deterministic fallback generator if LLM is unavailable or fails.
    """
    comp = get_period_comparison(db, period_type=period_type, user_id=user_id, target_date=target_date)

    period_name = "Month-over-Month" if comp.period_type == "mom" else "Week-over-Week"

    # Construct context for LLM prompt
    category_highlights = []
    for c in comp.categories:
        pct_str = f"{c.percentage_change:+.1f}%" if c.percentage_change is not None else "new spend"
        category_highlights.append(
            f"- {c.category_name}: Current ${c.current_spend:.2f} vs Prior ${c.prior_spend:.2f} (Change: ${c.change_amount:+.2f}, {pct_str}, Trend: {c.trend})"
        )

    cat_text = "\n".join(category_highlights) if category_highlights else "No transactions recorded in this period."

    # Try Anthropic Claude LLM call if key is present
    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip() != "":
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            prompt = (
                f"You are Coinsy, an intelligent and friendly personal finance AI mascot. "
                f"Generate a short, engaging natural-language summary (2-4 sentences) summarizing the user's spending changes for {period_name}.\n\n"
                f"Period Details:\n"
                f"- Target Period ({comp.target_period}) Total Spend: ${comp.total_current_spend:.2f}\n"
                f"- Prior Period ({comp.prior_period}) Total Spend: ${comp.total_prior_spend:.2f}\n"
                f"- Overall Change: ${comp.total_change_amount:+.2f} ({comp.total_percentage_change}%)\n"
                f"- Overall Trend: {comp.trend}\n\n"
                f"Category Breakdown:\n{cat_text}\n\n"
                f"Focus on the most notable category changes (e.g. spend going up or down significantly). "
                f"Keep it concise, clear, and encouraging without formatting headers."
            )

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            llm_summary = response.content[0].text.strip()

            return SpendSummaryResponse(
                summary=llm_summary,
                period_type=comp.period_type,
                target_period=comp.target_period,
                prior_period=comp.prior_period,
                is_llm_generated=True
            )
        except Exception as e:
            logger.error(f"Error generating LLM spend summary: {e}. Using rule-based fallback summary.")

    # Rule/template-based fallback generator
    if comp.total_current_spend == 0 and comp.total_prior_spend == 0:
        fallback_summary = (
            f"No spend data recorded for {comp.target_period} or {comp.prior_period}."
        )
    else:
        direction = "increased" if comp.total_change_amount > 0 else ("decreased" if comp.total_change_amount < 0 else "remained flat")
        abs_change = abs(comp.total_change_amount)
        pct_part = f" ({comp.total_percentage_change:+.1f}%)" if comp.total_percentage_change is not None else ""

        increases = [c for c in comp.categories if c.change_amount > 0]
        decreases = [c for c in comp.categories if c.change_amount < 0]

        top_up_str = ""
        if increases:
            top_up = increases[0]
            top_up_str = f" The largest spending increase was in {top_up.category_name} (+${top_up.change_amount:.2f})."

        top_down_str = ""
        if decreases:
            top_down = decreases[0]
            top_down_str = f" Meanwhile, spending in {top_down.category_name} dropped by ${abs(top_down.change_amount):.2f}."

        fallback_summary = (
            f"In {comp.target_period}, your total spend was ${comp.total_current_spend:.2f}, which {direction} by "
            f"${abs_change:.2f}{pct_part} compared to {comp.prior_period}.${top_up_str}{top_down_str}"
        )

    return SpendSummaryResponse(
        summary=fallback_summary,
        period_type=comp.period_type,
        target_period=comp.target_period,
        prior_period=comp.prior_period,
        is_llm_generated=False
    )
