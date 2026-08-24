from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import UserSettingsUpdate, UserSettingsResponse
from app.services.settings_service import get_user_settings, update_user_settings

router = APIRouter(prefix="/settings", tags=["Module 8: Central Settings"])


@router.get("", response_model=UserSettingsResponse)
def get_settings(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Fetches user automation parameters, caps, platform toggles, and notification webhooks.
    """
    return get_user_settings(db=db, user_id=user_id)


@router.put("", response_model=UserSettingsResponse)
def update_settings(
    settings_in: UserSettingsUpdate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Updates central settings, platform active/inactive toggles, credentials, and webhooks.
    """
    return update_user_settings(db=db, user_id=user_id, update_in=settings_in)
