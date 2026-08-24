import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

import anthropic
from app.core.config import settings
from app.db.models import JobApplication, UserResume, InterviewPrepPack, PrepPackItem
from app.models.schemas import (
    InterviewPrepPackResponse,
    PrepPackItemResponse,
    PrepPackItemUpdate,
    UserResumeCreate,
    UserResumeResponse,
)

logger = logging.getLogger(__name__)

DEFAULT_RESUME_CONTENT = """
Summary: Senior Software Engineer with 5+ years experience building scalable backend microservices, REST APIs, database models, and cloud solutions.
Key Experience:
- Designed and maintained high-throughput REST APIs using Python, FastAPI, SQL, and PostgreSQL/SQLite.
- Implemented background batch processing pipelines, caching layers, and automated testing suites achieving 90%+ coverage.
- Led technical design reviews, improved system performance by 35%, and integrated LLM AI features into customer applications.
- Built responsive web dashboards using React, JavaScript/TypeScript, and modern CSS frameworks.
"""


def save_user_resume(db: Session, user_id: int, content: str, title: str = "Default Resume") -> UserResumeResponse:
    resume = db.query(UserResume).filter(UserResume.user_id == user_id).first()
    if resume:
        resume.content = content
        resume.title = title
        resume.created_at = datetime.utcnow()
    else:
        resume = UserResume(
            user_id=user_id,
            title=title,
            content=content,
            created_at=datetime.utcnow()
        )
        db.add(resume)

    db.commit()
    db.refresh(resume)
    return UserResumeResponse.model_validate(resume)


def get_user_resume(db: Session, user_id: int) -> UserResumeResponse:
    resume = db.query(UserResume).filter(UserResume.user_id == user_id).first()
    if not resume:
        # Create default initial resume record for user
        return save_user_resume(db, user_id=user_id, content=DEFAULT_RESUME_CONTENT, title="Default Resume")
    return UserResumeResponse.model_validate(resume)


def generate_interview_prep_pack(db: Session, job_id: int, user_id: int) -> InterviewPrepPackResponse:
    """
    Generates a tailored Interview Prep Pack with Claude API (or heuristic fallback)
    for a job application in 'Interview' status.
    """
    job = db.query(JobApplication).filter(JobApplication.id == job_id, JobApplication.user_id == user_id).first()
    if not job:
        raise ValueError(f"Job application with id {job_id} not found.")

    # Automatically set status to 'Interview' if triggered
    if job.status != "Interview":
        job.status = "Interview"
        db.commit()

    resume_obj = get_user_resume(db, user_id=user_id)
    resume_text = resume_obj.content

    # Clear existing prep pack for this job if recreating
    existing_pack = db.query(InterviewPrepPack).filter(InterviewPrepPack.job_id == job_id).first()
    if existing_pack:
        db.delete(existing_pack)
        db.commit()

    is_llm = False
    company_context = ""
    resume_overlap = ""
    items_data = []

    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip() != "":
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            prompt = (
                f"You are an expert technical and behavioral interview coach.\n"
                f"Analyze the Job Description (JD) and candidate's Resume below to build a highly tailored, checkable Interview Prep Pack.\n\n"
                f"JOB DETAILS:\n"
                f"- Company: {job.company_name}\n"
                f"- Job Title: {job.job_title}\n"
                f"- Job Description:\n{job.job_description}\n\n"
                f"CANDIDATE RESUME BULLETS:\n{resume_text}\n\n"
                f"INSTRUCTIONS:\n"
                f"Generate a valid JSON object with the following schema:\n"
                f"{{\n"
                f'  "company_context": "2-3 sentence overview of company background & key focus",\n'
                f'  "resume_overlap_analysis": "Summary of overlap strengths vs JD requirements and gaps to cover",\n'
                f'  "items": [\n'
                f'    {{\n'
                f'      "item_type": "technical" | "behavioral" | "star_answer" | "company_notes",\n'
                f'      "title": "Short item title",\n'
                f'      "question": "Question or prep prompt text",\n'
                f'      "star_situation": "Situation context (if star_answer)",\n'
                f'      "star_task": "Task objective (if star_answer)",\n'
                f'      "star_action": "Action steps incorporating actual resume bullets (if star_answer)",\n'
                f'      "star_result": "Measurable outcome/result (if star_answer)"\n'
                f'    }}\n'
                f'  ]\n'
                f"}}\n"
                f"Include 6 to 9 items covering likely technical questions, behavioral questions, STAR draft answers using actual resume bullets, and company research notes. Return ONLY valid JSON."
            )

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            content_text = response.content[0].text.strip()
            if content_text.startswith("```"):
                content_text = content_text.split("```")[1]
                if content_text.startswith("json"):
                    content_text = content_text[4:]
            content_text = content_text.strip()

            parsed = json.loads(content_text)
            company_context = parsed.get("company_context", "")
            resume_overlap = parsed.get("resume_overlap_analysis", "")
            items_data = parsed.get("items", [])
            is_llm = True

        except Exception as e:
            logger.error(f"Error generating Claude LLM interview prep pack: {e}. Using heuristic generator.")
            company_context, resume_overlap, items_data = _fallback_prep_pack_generator(job, resume_text)
    else:
        company_context, resume_overlap, items_data = _fallback_prep_pack_generator(job, resume_text)

    # Save to database
    prep_pack = InterviewPrepPack(
        job_id=job_id,
        user_id=user_id,
        company_context=company_context,
        resume_overlap_analysis=resume_overlap,
        is_generated_by_llm=is_llm,
        created_at=datetime.utcnow()
    )
    db.add(prep_pack)
    db.commit()
    db.refresh(prep_pack)

    prep_items = []
    for item in items_data:
        p_item = PrepPackItem(
            prep_pack_id=prep_pack.id,
            item_type=item.get("item_type", "technical"),
            title=item.get("title", "Interview Prep Question"),
            question=item.get("question", ""),
            star_situation=item.get("star_situation"),
            star_task=item.get("star_task"),
            star_action=item.get("star_action"),
            star_result=item.get("star_result"),
            user_notes="",
            is_completed=False
        )
        db.add(p_item)
        prep_items.append(p_item)

    db.commit()

    return get_prep_pack_by_job(db, job_id=job_id, user_id=user_id)


def _fallback_prep_pack_generator(job: JobApplication, resume_text: str) -> Tuple[str, str, List[Dict[str, Any]]]:
    company_context = (
        f"{job.company_name} is hiring for a {job.job_title} role. Key focus involves building scalable systems, "
        f"collaborating with cross-functional engineering teams, and delivering high quality features."
    )
    resume_overlap = (
        f"Candidate resume shows strong alignment with {job.job_title} requirements in microservices, REST API design, "
        f"and automated testing. Highlight specific metrics from recent projects during technical discussions."
    )

    items = [
        {
            "item_type": "company_notes",
            "title": f"{job.company_name} Core Mission & Product Focus",
            "question": f"Review {job.company_name}'s recent technical architecture, engineering blog posts, and core product offerings prior to the call."
        },
        {
            "item_type": "technical",
            "title": f"Technical Deep-Dive: {job.job_title} Architecture",
            "question": f"How would you design a scalable microservices backend for the requirements listed in {job.company_name}'s job description?"
        },
        {
            "item_type": "technical",
            "title": "API Design & Error Handling Strategy",
            "question": "Walk through your approach to designing idempotent REST APIs, database indexing, and fault-tolerant background workers."
        },
        {
            "item_type": "behavioral",
            "title": "Behavioral: Handling Technical Disagreements",
            "question": "Describe a scenario where you had a architectural disagreement with a teammate and how you resolved it to achieve a successful release."
        },
        {
            "item_type": "star_answer",
            "title": "STAR Draft: Optimizing System Performance",
            "question": "Tell me about a time you identified a bottleneck in production and optimized backend performance.",
            "star_situation": f"While working on high-throughput backend services relevant to {job.company_name}...",
            "star_task": "Identified high latency bottlenecks and DB query slow-downs under peak load.",
            "star_action": "Refactored ORM queries, implemented Redis/Pandas caching pipelines, and added comprehensive pytest unit tests.",
            "star_result": "Improved response times by 35% and maintained 99.9% uptime during peak traffic."
        },
        {
            "item_type": "star_answer",
            "title": "STAR Draft: Delivering Under Tight Deadlines",
            "question": "Give an example of delivering a critical feature on a tight deadline.",
            "star_situation": "Faced a tight deadline to ship full-stack application features with auth and data visualization...",
            "star_task": "Deliver complete end-to-end functionality within target sprint timeframe.",
            "star_action": "Prioritized core API schemas, built reusable UI components, and integrated automated testing pipelines.",
            "star_result": "Successfully deployed feature package ahead of schedule with zero critical bugs."
        }
    ]

    return company_context, resume_overlap, items


def get_prep_pack_by_job(db: Session, job_id: int, user_id: int) -> Optional[InterviewPrepPackResponse]:
    prep_pack = (
        db.query(InterviewPrepPack)
        .filter(InterviewPrepPack.job_id == job_id, InterviewPrepPack.user_id == user_id)
        .first()
    )

    if not prep_pack:
        return None

    items = (
        db.query(PrepPackItem)
        .filter(PrepPackItem.prep_pack_id == prep_pack.id)
        .order_by(PrepPackItem.id.asc())
        .all()
    )

    completed_count = sum(1 for item in items if item.is_completed)
    total_count = len(items)

    item_responses = [PrepPackItemResponse.model_validate(item) for item in items]

    return InterviewPrepPackResponse(
        id=prep_pack.id,
        job_id=prep_pack.job_id,
        user_id=prep_pack.user_id,
        company_context=prep_pack.company_context,
        resume_overlap_analysis=prep_pack.resume_overlap_analysis,
        is_generated_by_llm=prep_pack.is_generated_by_llm or False,
        created_at=prep_pack.created_at,
        items=item_responses,
        completed_count=completed_count,
        total_count=total_count
    )


def update_prep_pack_item(
    db: Session,
    item_id: int,
    user_id: int,
    update_in: PrepPackItemUpdate
) -> PrepPackItemResponse:
    item = (
        db.query(PrepPackItem)
        .join(InterviewPrepPack, PrepPackItem.prep_pack_id == InterviewPrepPack.id)
        .filter(PrepPackItem.id == item_id, InterviewPrepPack.user_id == user_id)
        .first()
    )

    if not item:
        raise ValueError(f"PrepPackItem with id {item_id} not found.")

    if update_in.is_completed is not None:
        item.is_completed = update_in.is_completed
    if update_in.user_notes is not None:
        item.user_notes = update_in.user_notes

    db.commit()
    db.refresh(item)
    return PrepPackItemResponse.model_validate(item)
