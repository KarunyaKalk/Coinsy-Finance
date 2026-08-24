import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.db.models import UserSettings
from app.models.schemas import UserSettingsUpdate, UserSettingsResponse

logger = logging.getLogger(__name__)

DEFAULT_PLATFORMS = {
    "linkedin": True,
    "indeed": True,
    "glassdoor": False,
    "wellfound": True,
    "ziprecruiter": False
}


def get_user_settings(db: Session, user_id: int) -> UserSettingsResponse:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(
            user_id=user_id,
            scan_frequency="6h",
            ats_threshold=75.0,
            daily_app_cap=15,
            daily_email_cap=5,
            active_platforms_json=json.dumps(DEFAULT_PLATFORMS),
            platform_credentials_json=json.dumps({}),
            telegram_webhook_url=None,
            email_notification_address=None,
            updated_at=datetime.utcnow()
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    active_platforms = json.loads(settings.active_platforms_json) if settings.active_platforms_json else DEFAULT_PLATFORMS
    platform_creds = json.loads(settings.platform_credentials_json) if settings.platform_credentials_json else {}

    return UserSettingsResponse(
        user_id=settings.user_id,
        scan_frequency=settings.scan_frequency,
        ats_threshold=settings.ats_threshold,
        daily_app_cap=settings.daily_app_cap,
        daily_email_cap=settings.daily_email_cap,
        active_platforms=active_platforms,
        platform_credentials=platform_creds,
        telegram_webhook_url=settings.telegram_webhook_url,
        email_notification_address=settings.email_notification_address,
        updated_at=settings.updated_at
    )


def update_user_settings(db: Session, user_id: int, update_in: UserSettingsUpdate) -> UserSettingsResponse:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        get_user_settings(db, user_id)
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    if update_in.scan_frequency is not None:
        settings.scan_frequency = update_in.scan_frequency
    if update_in.ats_threshold is not None:
        settings.ats_threshold = update_in.ats_threshold
    if update_in.daily_app_cap is not None:
        settings.daily_app_cap = update_in.daily_app_cap
    if update_in.daily_email_cap is not None:
        settings.daily_email_cap = update_in.daily_email_cap
    if update_in.active_platforms is not None:
        settings.active_platforms_json = json.dumps(update_in.active_platforms)
    if update_in.platform_credentials is not None:
        settings.platform_credentials_json = json.dumps(update_in.platform_credentials)
    if update_in.telegram_webhook_url is not None:
        settings.telegram_webhook_url = update_in.telegram_webhook_url
    if update_in.email_notification_address is not None:
        settings.email_notification_address = update_in.email_notification_address

    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)

    return get_user_settings(db, user_id)
