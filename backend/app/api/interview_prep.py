from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import (
    InterviewPrepPackResponse,
    PrepPackItemResponse,
    PrepPackItemUpdate,
    UserResumeCreate,
    UserResumeResponse,
)
from app.services.interview_prep_service import (
    generate_interview_prep_pack,
    get_prep_pack_by_job,
    update_prep_pack_item,
    save_user_resume,
    get_user_resume,
)

router = APIRouter(prefix="/interview-prep", tags=["Module 7: Interview Prep Pack"])


@router.post("/generate/{job_id}", response_model=InterviewPrepPackResponse)
def trigger_prep_pack_generation(
    job_id: int,
    user_id: int = Query(..., description="User ID generating prep pack"),
    db: Session = Depends(get_db)
):
    """
    Generates a tailored Interview Prep Pack using Claude AI for a job application in 'Interview' status.
    """
    try:
        return generate_interview_prep_pack(db=db, job_id=job_id, user_id=user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prep pack: {str(e)}"
        )


@router.get("/{job_id}", response_model=InterviewPrepPackResponse)
def get_prep_pack(
    job_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Retrieves the checkable Interview Prep Pack and checklist items for a job application.
    """
    pack = get_prep_pack_by_job(db=db, job_id=job_id, user_id=user_id)
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prep pack found for job application {job_id}. Click 'Generate Prep Pack' to create one."
        )
    return pack


@router.patch("/items/{item_id}", response_model=PrepPackItemResponse)
def update_checklist_item(
    item_id: int,
    update_in: PrepPackItemUpdate,
    user_id: int = Query(..., description="User ID updating checklist item"),
    db: Session = Depends(get_db)
):
    """
    Updates the completion tick state and custom user notes for a prep pack checklist item.
    """
    try:
        return update_prep_pack_item(db=db, item_id=item_id, user_id=user_id, update_in=update_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/resume/me", response_model=UserResumeResponse)
def fetch_user_resume(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Fetches user's saved resume bullets/text.
    """
    return get_user_resume(db=db, user_id=user_id)


@router.post("/resume/me", response_model=UserResumeResponse)
def update_user_resume(
    resume_in: UserResumeCreate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Saves or updates user's resume bullets/text.
    """
    return save_user_resume(db=db, user_id=user_id, content=resume_in.content, title=resume_in.title)
