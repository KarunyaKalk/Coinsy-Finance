from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_db, engine, Base
from app.api.categories import router as categories_router
from app.api.transactions import router as transactions_router
from app.api.statements import router as statements_router
from app.api.analytics import router as analytics_router
from app.api.insights import router as insights_router
from app.api.auth import router as auth_router
from app.api.budgets import router as budgets_router
from app.api.personality import router as personality_router
from app.core.scheduler import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (suitable for initial dev/staging deployment)
    Base.metadata.create_all(bind=engine)
    scheduler.start()
    yield
    scheduler.stop()

app = FastAPI(
    title="Coinsy Finance API",
    description="LLM-Powered Personal Finance Tracker Backend",
    version="0.1.0",
    lifespan=lifespan
)

# Dynamic CORS Configuration from Environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(budgets_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(statements_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(insights_router, prefix="/api/v1")
app.include_router(personality_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "app": "Coinsy Finance API",
        "status": "healthy",
        "version": "0.1.0"
    }

@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "unhealthy"
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    scheduler_running = scheduler._thread is not None and scheduler._thread.is_alive()

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database": db_status,
        "scheduler_running": scheduler_running,
        "allowed_origins": settings.cors_origins_list,
    }
