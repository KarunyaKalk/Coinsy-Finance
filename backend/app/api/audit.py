from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import AuditLogResponse, BlockAlertTriggerRequest
from app.services.audit_service import get_audit_logs, handle_scraper_block, log_audit_event

router = APIRouter(prefix="/audit", tags=["Module 8: Audit Log Activity Feed"])


@router.get("", response_model=List[AuditLogResponse])
def fetch_audit_logs(
    user_id: int = Query(..., description="User ID"),
    action_type: Optional[str] = Query("all", description="Filter by action type (all, scrape_run, resume_generation, ats_score, application_submission, email_sent, captcha_blocked)"),
    status_filter: Optional[str] = Query("all", description="Filter by status (all, success, warning, failed, blocked)"),
    limit: int = Query(50, description="Max logs to return"),
    db: Session = Depends(get_db)
):
    """
    Returns filterable audit activity log events for transparent tracking of agent actions.
    """
    return get_audit_logs(db=db, user_id=user_id, action_type=action_type, status=status_filter, limit=limit)


@router.post("/trigger-block-alert")
def trigger_block_alert(
    req: BlockAlertTriggerRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Simulates / triggers graceful failure handling for a CAPTCHA or platform block without aggressive retries.
    """
    return handle_scraper_block(db=db, user_id=user_id, platform=req.platform, error_msg=req.error_message)
