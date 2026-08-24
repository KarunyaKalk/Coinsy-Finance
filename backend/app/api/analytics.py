from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import (
    SpendAggregationResponse,
    PeriodComparisonResponse,
    SpendSummaryResponse,
    DailyHeatmapItem,
    CashFlowResponse,
    MoneyRecapResponse,
)
from app.services.spend_analytics import (
    get_spend_aggregation,
    get_period_comparison,
    generate_spend_summary,
)
from app.services.budget_service import (
    get_daily_spend_heatmap,
    get_cash_flow_analytics,
)
from app.services.personality_service import generate_monthly_recap

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/spend", response_model=SpendAggregationResponse)
def get_spend_analytics(
    timeframe: str = Query("monthly", description="Timeframe aggregation: 'weekly', 'monthly', or 'yearly'"),
    user_id: Optional[int] = Query(None, description="Optional filter by user ID"),
    start_date: Optional[date] = Query(None, description="Optional start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Optional end date filter (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated spend by category and timeframe (weekly, monthly, or yearly) using Pandas.
    """
    try:
        return get_spend_aggregation(
            db=db,
            timeframe=timeframe,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/comparison", response_model=PeriodComparisonResponse)
def get_spend_comparison(
    period: str = Query("mom", description="Comparison period: 'mom' (Month-over-Month) or 'wow' (Week-over-Week)"),
    user_id: Optional[int] = Query(None, description="Optional filter by user ID"),
    target_date: Optional[date] = Query(None, description="Optional reference date (YYYY-MM-DD). Defaults to current date."),
    db: Session = Depends(get_db)
):
    """
    Returns Month-over-Month (MoM) or Week-over-Week (WoW) spend comparison metrics per category and overall.
    """
    try:
        return get_period_comparison(
            db=db,
            period_type=period,
            user_id=user_id,
            target_date=target_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/summary", response_model=SpendSummaryResponse)
def get_spend_text_summary(
    period: str = Query("mom", description="Comparison period: 'mom' (Month-over-Month) or 'wow' (Week-over-Week)"),
    user_id: Optional[int] = Query(None, description="Optional filter by user ID"),
    target_date: Optional[date] = Query(None, description="Optional reference date (YYYY-MM-DD). Defaults to current date."),
    db: Session = Depends(get_db)
):
    """
    Generates a natural-language text summary of notable spend changes using Claude LLM
    (with automatic rule fallback if LLM is unavailable).
    """
    try:
        return generate_spend_summary(
            db=db,
            period_type=period,
            user_id=user_id,
            target_date=target_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/heatmap", response_model=List[DailyHeatmapItem])
def get_daily_heatmap(
    user_id: int = Query(..., description="User ID for daily spend intensity heatmap"),
    days_back: int = Query(90, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Returns daily spend intensity level (0-4) data for calendar heatmaps.
    """
    return get_daily_spend_heatmap(db=db, user_id=user_id, days_back=days_back)


@router.get("/cashflow", response_model=CashFlowResponse)
def get_cashflow_analytics(
    user_id: int = Query(..., description="User ID for cash flow analytics"),
    timeframe: str = Query("monthly", description="'monthly' or 'yearly'"),
    db: Session = Depends(get_db)
):
    """
    Returns Income vs Expense vs Savings analytics over time.
    """
    return get_cash_flow_analytics(db=db, user_id=user_id, timeframe=timeframe)


@router.get("/recap", response_model=MoneyRecapResponse)
def get_monthly_recap_endpoint(
    user_id: int = Query(..., description="User ID for monthly recap"),
    month: Optional[int] = Query(None, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year (YYYY)"),
    db: Session = Depends(get_db)
):
    """
    Generates Spotify-Wrapped style shareable monthly money recap summary data.
    """
    return generate_monthly_recap(db=db, user_id=user_id, month=month, year=year)


