from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import JobApplication, InterviewPrepPack
from app.models.schemas import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
)

router = APIRouter(prefix="/jobs", tags=["Job Applications Tracker"])


@router.get("", response_model=List[JobApplicationResponse])
def list_jobs(
    user_id: int = Query(..., description="User ID for job applications list"),
    status_filter: Optional[str] = Query(None, description="Optional filter by status (Applied, Interview, Offered, Rejected)"),
    db: Session = Depends(get_db)
):
    query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
    if status_filter:
        query = query.filter(JobApplication.status == status_filter)

    jobs = query.order_by(JobApplication.created_at.desc()).all()

    # Determine prep pack existence
    prep_job_ids = set(
        r[0] for r in db.query(InterviewPrepPack.job_id).filter(InterviewPrepPack.user_id == user_id).all()
    )

    results = []
    for j in jobs:
        resp = JobApplicationResponse.model_validate(j)
        resp.has_prep_pack = j.id in prep_job_ids
        results.append(resp)

    return results


@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobApplicationCreate,
    user_id: int = Query(..., description="User ID creating the job application"),
    db: Session = Depends(get_db)
):
    job = JobApplication(
        user_id=user_id,
        company_name=job_in.company_name,
        job_title=job_in.job_title,
        job_description=job_in.job_description,
        status=job_in.status,
        location=job_in.location,
        salary_range=job_in.salary_range
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    resp = JobApplicationResponse.model_validate(job)
    resp.has_prep_pack = False
    return resp


@router.get("/{job_id}", response_model=JobApplicationResponse)
def get_job(
    job_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    job = db.query(JobApplication).filter(JobApplication.id == job_id, JobApplication.user_id == user_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Application with id {job_id} not found."
        )

    has_prep = db.query(InterviewPrepPack).filter(InterviewPrepPack.job_id == job_id).first() is not None
    resp = JobApplicationResponse.model_validate(job)
    resp.has_prep_pack = has_prep
    return resp


@router.put("/{job_id}", response_model=JobApplicationResponse)
def update_job(
    job_id: int,
    job_in: JobApplicationUpdate,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    job = db.query(JobApplication).filter(JobApplication.id == job_id, JobApplication.user_id == user_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Application with id {job_id} not found."
        )

    update_data = job_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    has_prep = db.query(InterviewPrepPack).filter(InterviewPrepPack.job_id == job_id).first() is not None
    resp = JobApplicationResponse.model_validate(job)
    resp.has_prep_pack = has_prep
    return resp


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    job = db.query(JobApplication).filter(JobApplication.id == job_id, JobApplication.user_id == user_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Application with id {job_id} not found."
        )

    db.delete(job)
    db.commit()
    return None
