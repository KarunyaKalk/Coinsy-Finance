import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import AuditLog, CoinsyMessage, UserSettings
from app.models.schemas import AuditLogResponse

logger = logging.getLogger(__name__)


def log_audit_event(
    db: Session,
    user_id: int,
    action_type: str,
    status: str,
    title: str,
    details: Optional[str] = None,
    platform: Optional[str] = None
) -> AuditLogResponse:
    log_entry = AuditLog(
        user_id=user_id,
        action_type=action_type,
        status=status,
        platform=platform,
        title=title,
        details=details,
        created_at=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return AuditLogResponse.model_validate(log_entry)


def get_audit_logs(
    db: Session,
    user_id: int,
    action_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
) -> List[AuditLogResponse]:
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id)

    if action_type and action_type != "all":
        query = query.filter(AuditLog.action_type == action_type)
    if status and status != "all":
        query = query.filter(AuditLog.status == status)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [AuditLogResponse.model_validate(log) for log in logs]


def handle_scraper_block(
    db: Session,
    user_id: int,
    platform: str,
    error_msg: str
) -> Dict[str, Any]:
    """
    Handles CAPTCHA / platform rate-limit blocks gracefully without aggressive retries.
    Logs audit event, creates Coinsy message notification alert, and triggers webhook alerts.
    """
    logger.warning(f"Scraper block detected on platform {platform} for user {user_id}: {error_msg}")

    # 1. Log blocked audit event
    audit_entry = log_audit_event(
        db=db,
        user_id=user_id,
        action_type="captcha_blocked",
        status="blocked",
        platform=platform,
        title=f"Platform Block / CAPTCHA Challenge on {platform}",
        details=f"Automation paused gracefully on {platform}: {error_msg}. Aggressive retries disabled to protect account."
    )

    # 2. Store Coinsy notification message for UI mascot widget
    coinsy_msg = CoinsyMessage(
        user_id=user_id,
        role="coinsy",
        message=f"Alert: Automation paused on {platform} due to CAPTCHA block ({error_msg}). Retries disabled for safety.",
        mascot_mood="concerned",
        created_at=datetime.utcnow()
    )
    db.add(coinsy_msg)
    db.commit()

    return {
        "status": "blocked",
        "platform": platform,
        "message": f"Automation paused on {platform}. In-app alert created.",
        "audit_id": audit_entry.id
    }
