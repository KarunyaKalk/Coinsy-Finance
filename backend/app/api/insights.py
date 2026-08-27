from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rate_limiter import verify_llm_rate_limit
from app.models.schemas import (
    PredictionResponse,
    DailyTipResponse,
    BatchJobResponse,
    AskCoinsyRequest,
    AskCoinsyResponse,
)
from app.services.insights_service import (
    get_latest_prediction,
    get_latest_daily_tip,
    run_batch_insights_job,
    ask_coinsy_companion,
)



router = APIRouter(prefix="/insights", tags=["Insights & Predictions"])


@router.get("/prediction", response_model=PredictionResponse)
def get_prediction_endpoint(
    user_id: int = Query(..., description="User ID for spend forecast prediction"),
    force_refresh: bool = Query(False, description="If True, re-calculates prediction instead of serving pre-computed DB insight"),
    db: Session = Depends(get_db)
):
    """
    Returns pre-computed next month's spend prediction per category with a 1-line LLM explanation.
    Pre-computed in background batch jobs for instant response.
    """
    try:
        return get_latest_prediction(db=db, user_id=user_id, force_refresh=force_refresh)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating spend prediction: {str(e)}"
        )


@router.get("/daily-tip", response_model=DailyTipResponse)
def get_daily_tip_endpoint(
    user_id: int = Query(..., description="User ID for daily personal tip"),
    force_refresh: bool = Query(False, description="If True, re-calculates daily tip instead of serving pre-computed DB insight"),
    db: Session = Depends(get_db)
):
    """
    Returns pre-computed specific, non-generic daily tip based on last 30 days of transactions.
    Pre-computed in background batch jobs for instant response.
    """
    try:
        return get_latest_daily_tip(db=db, user_id=user_id, force_refresh=force_refresh)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating daily tip: {str(e)}"
        )


@router.post("/run-batch", response_model=BatchJobResponse)
def trigger_batch_insights_job(
    user_id: Optional[int] = Query(None, description="Optional user ID to restrict batch run"),
    db: Session = Depends(get_db)
):
    """
    Triggers batch job execution to pre-compute predictions and daily tips for users and persist in DB.
    """
    try:
        return run_batch_insights_job(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running batch insights job: {str(e)}"
        )


@router.post("/ask", response_model=AskCoinsyResponse, dependencies=[Depends(verify_llm_rate_limit)])
def ask_coinsy_endpoint(
    req: AskCoinsyRequest,
    db: Session = Depends(get_db)
):

    """
    Interactive companion chat endpoint for Ask Coinsy feature.
    Prompts Claude LLM with companion mascot system prompt and financial context.
    """
    try:
        return ask_coinsy_companion(
            db=db,
            user_id=req.user_id,
            user_message=req.message,
            roast_mode=req.roast_mode
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error chatting with Coinsy: {str(e)}"
        )

