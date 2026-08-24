import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import Budget, Category, Transaction, CoinsyMessage
from app.models.schemas import (
    BudgetCreate,
    BudgetResponse,
    DailyHeatmapItem,
    CashFlowItem,
    CashFlowResponse,
    CoinsyWidgetResponse,
)

logger = logging.getLogger(__name__)


def _get_month_date_range(year: int, month: int) -> tuple[date, date]:
    start_d = date(year, month, 1)
    if month == 12:
        end_d = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_d = date(year, month + 1, 1) - timedelta(days=1)
    return start_d, end_d


def get_user_budgets(
    db: Session,
    user_id: int,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> List[BudgetResponse]:
    ref_d = date.today()
    target_month = month or ref_d.month
    target_year = year or ref_d.year

    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == user_id, Budget.month == target_month, Budget.year == target_year)
        .all()
    )

    if not budgets:
        return []

    start_d, end_d = _get_month_date_range(target_year, target_month)

    # Compute category spend for the month
    spend_records = (
        db.query(Transaction.category_id, Transaction.amount)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "debit",
            Transaction.date >= start_d,
            Transaction.date <= end_d
        )
        .all()
    )

    spent_by_cat: Dict[int, float] = {}
    for r in spend_records:
        if r.category_id:
            spent_by_cat[r.category_id] = spent_by_cat.get(r.category_id, 0.0) + float(r.amount)

    result = []
    for b in budgets:
        cat = db.query(Category).filter(Category.id == b.category_id).first()
        cat_name = cat.name if cat else "Uncategorized"

        curr_spent = round(spent_by_cat.get(b.category_id, 0.0), 2)
        pct_used = round((curr_spent / b.amount_limit) * 100, 2) if b.amount_limit > 0 else 0.0

        if pct_used >= 100.0:
            status = "exceeded"
        elif pct_used >= 80.0:
            status = "warning"
        else:
            status = "normal"

        result.append(
            BudgetResponse(
                id=b.id,
                user_id=b.user_id,
                category_id=b.category_id,
                category_name=cat_name,
                amount_limit=round(float(b.amount_limit), 2),
                current_spent=curr_spent,
                percentage_used=pct_used,
                status=status,
                month=b.month,
                year=b.year,
                created_at=b.created_at or datetime.utcnow()
            )
        )

    result.sort(key=lambda x: x.percentage_used, reverse=True)
    return result


def set_category_budget(
    db: Session,
    user_id: int,
    budget_in: BudgetCreate
) -> BudgetResponse:
    target_month = budget_in.month
    target_year = budget_in.year

    category = db.query(Category).filter(Category.id == budget_in.category_id).first()
    category_name = category.name if category else "Uncategorized"

    budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.category_id == budget_in.category_id,
            Budget.month == target_month,
            Budget.year == target_year
        )
        .first()
    )

    if budget:
        budget.amount_limit = budget_in.amount_limit
    else:
        budget = Budget(
            user_id=user_id,
            category_id=budget_in.category_id,
            amount_limit=budget_in.amount_limit,
            month=target_month,
            year=target_year
        )
        db.add(budget)

    db.commit()
    db.refresh(budget)

    # Compute spend & status
    start_d, end_d = _get_month_date_range(target_year, target_month)
    spend_records = (
        db.query(Transaction.amount)
        .filter(
            Transaction.user_id == user_id,
            Transaction.category_id == budget_in.category_id,
            Transaction.type == "debit",
            Transaction.date >= start_d,
            Transaction.date <= end_d
        )
        .all()
    )
    curr_spent = round(sum(float(r.amount) for r in spend_records), 2)
    limit = round(float(budget.amount_limit), 2)
    pct_used = round((curr_spent / limit) * 100, 2) if limit > 0 else 0.0

    if pct_used >= 100.0:
        b_status = "exceeded"
        alert_msg = f"Alert: You have exceeded your monthly {category_name} budget! Spent ${curr_spent:.2f} of ${limit:.2f} limit ({pct_used:.1f}%)."
        mood = "concerned"
    elif pct_used >= 80.0:
        b_status = "warning"
        alert_msg = f"Warning: You have reached {pct_used:.1f}% of your monthly {category_name} budget (${curr_spent:.2f} / ${limit:.2f})."
        mood = "concerned"
    else:
        b_status = "normal"
        alert_msg = f"Budget set: ${limit:.2f} limit for {category_name}. Current spend: ${curr_spent:.2f}."
        mood = "happy"

    # Store notification event in CoinsyMessage for the Coinsy mascot widget
    coinsy_msg = CoinsyMessage(
        user_id=user_id,
        role="coinsy",
        message=alert_msg,
        mascot_mood=mood,
        created_at=datetime.utcnow()
    )
    db.add(coinsy_msg)
    db.commit()

    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        category_name=category_name,
        amount_limit=limit,
        current_spent=curr_spent,
        percentage_used=pct_used,
        status=b_status,
        month=budget.month,
        year=budget.year,
        created_at=budget.created_at or datetime.utcnow()
    )


def delete_budget(db: Session, user_id: int, budget_id: int) -> bool:
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()
    if not budget:
        return False
    db.delete(budget)
    db.commit()
    return True


def get_daily_spend_heatmap(
    db: Session,
    user_id: int,
    days_back: int = 90
) -> List[DailyHeatmapItem]:
    """
    Generates a list of daily spend intensity items for calendar heatmaps.
    """
    start_d = date.today() - timedelta(days=days_back)
    end_d = date.today()

    records = (
        db.query(Transaction.date, Transaction.amount)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "debit",
            Transaction.date >= start_d,
            Transaction.date <= end_d
        )
        .all()
    )

    # Initialize all dates in range with 0 spend
    date_map: Dict[str, Dict[str, Any]] = {}
    curr = start_d
    while curr <= end_d:
        date_str = curr.strftime("%Y-%m-%d")
        date_map[date_str] = {"total_spend": 0.0, "count": 0}
        curr += timedelta(days=1)

    for r in records:
        d_str = r.date.strftime("%Y-%m-%d")
        if d_str in date_map:
            date_map[d_str]["total_spend"] += float(r.amount)
            date_map[d_str]["count"] += 1

    max_spend = max((item["total_spend"] for item in date_map.values()), default=0.0)

    heatmap_items: List[DailyHeatmapItem] = []
    for d_str in sorted(date_map.keys()):
        tot = round(date_map[d_str]["total_spend"], 2)
        cnt = date_map[d_str]["count"]

        if tot == 0:
            level = 0
        elif max_spend == 0 or tot <= 0.25 * max_spend:
            level = 1
        elif tot <= 0.50 * max_spend:
            level = 2
        elif tot <= 0.75 * max_spend:
            level = 3
        else:
            level = 4

        heatmap_items.append(
            DailyHeatmapItem(
                date=d_str,
                total_spend=tot,
                transaction_count=cnt,
                intensity_level=level
            )
        )

    return heatmap_items


def get_cash_flow_analytics(
    db: Session,
    user_id: int,
    timeframe: str = "monthly"  # monthly | yearly
) -> CashFlowResponse:
    """
    Computes income vs expense vs savings over time.
    """
    records = (
        db.query(Transaction.date, Transaction.amount, Transaction.type)
        .filter(Transaction.user_id == user_id)
        .all()
    )

    if not records:
        return CashFlowResponse(
            timeframe=timeframe,
            periods=[],
            total_income=0.0,
            total_expense=0.0,
            total_savings=0.0,
            avg_savings_rate=0.0
        )

    df = pd.DataFrame(
        [
            {
                "date": r.date,
                "amount": float(r.amount),
                "type": r.type
            }
            for r in records
        ]
    )
    df["date"] = pd.to_datetime(df["date"])

    if timeframe == "yearly":
        df["period"] = df["date"].dt.strftime("%Y")
    else:
        df["period"] = df["date"].dt.strftime("%Y-%m")

    periods_data: List[CashFlowItem] = []
    unique_periods = sorted(df["period"].unique())

    total_inc = 0.0
    total_exp = 0.0

    for p_str in unique_periods:
        p_df = df[df["period"] == p_str]
        inc = round(float(p_df[p_df["type"] == "credit"]["amount"].sum()), 2)
        exp = round(float(p_df[p_df["type"] == "debit"]["amount"].sum()), 2)
        sav = round(inc - exp, 2)
        rate = round((sav / inc) * 100, 2) if inc > 0 else 0.0

        total_inc += inc
        total_exp += exp

        periods_data.append(
            CashFlowItem(
                period=p_str,
                income=inc,
                expense=exp,
                savings=sav,
                savings_rate=rate
            )
        )

    total_inc = round(total_inc, 2)
    total_exp = round(total_exp, 2)
    total_sav = round(total_inc - total_exp, 2)
    avg_rate = round((total_sav / total_inc) * 100, 2) if total_inc > 0 else 0.0

    return CashFlowResponse(
        timeframe=timeframe,
        periods=periods_data,
        total_income=total_inc,
        total_expense=total_exp,
        total_savings=total_sav,
        avg_savings_rate=avg_rate
    )


def get_coinsy_widget_status(db: Session, user_id: int) -> CoinsyWidgetResponse:
    """
    Fetches latest Coinsy mascot notification message & mood for the Coinsy widget.
    """
    msg = (
        db.query(CoinsyMessage)
        .filter(CoinsyMessage.user_id == user_id)
        .order_by(CoinsyMessage.created_at.desc())
        .first()
    )

    if msg:
        return CoinsyWidgetResponse(
            user_id=user_id,
            message=msg.message,
            mascot_mood=msg.mascot_mood or "happy",
            created_at=msg.created_at or datetime.utcnow()
        )

    return CoinsyWidgetResponse(
        user_id=user_id,
        message="Hi! I'm Coinsy, your AI personal finance mascot. Track your monthly budgets and stay on top of your goals!",
        mascot_mood="happy",
        created_at=datetime.utcnow()
    )
