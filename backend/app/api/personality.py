from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import (
    PersonalityResponse,
    DailyTipResponse,
)
from app.services.personality_service import (
    get_personality_status,
    generate_personality_tip,
)

router = APIRouter(prefix="/personality", tags=["Personality Layer"])


@router.get("", response_model=PersonalityResponse)
def get_personality(
    user_id: int = Query(..., description="User ID for personality status"),
    roast_mode: bool = Query(False, description="Whether roast mode is enabled"),
    db: Session = Depends(get_db)
):
    """
    Returns budget streak counter, money mood (thriving/calm/stressed), and mood description.
    """
    return get_personality_status(db=db, user_id=user_id, roast_mode=roast_mode)


@router.get("/tip", response_model=DailyTipResponse)
def get_personality_daily_tip(
    user_id: int = Query(..., description="User ID for daily tip"),
    roast_mode: bool = Query(False, description="Enable Roast Mode for witty/humorous LLM tips"),
    db: Session = Depends(get_db)
):
    """
    Generates a daily tip with optional Roast Mode toggle (humorous sarcastic LLM roasts).
    """
    return generate_personality_tip(db=db, user_id=user_id, roast_mode=roast_mode)
