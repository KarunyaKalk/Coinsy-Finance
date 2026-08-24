from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.categories import router as categories_router
from app.api.transactions import router as transactions_router
from app.api.statements import router as statements_router
from app.api.analytics import router as analytics_router
from app.api.insights import router as insights_router
from app.api.auth import router as auth_router
from app.api.budgets import router as budgets_router
from app.core.scheduler import scheduler

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.stop()

app = FastAPI(
    title="Coinsy Finance API",
    description="LLM-Powered Personal Finance Tracker Backend",
    version="0.1.0",
    lifespan=lifespan
)

# Enable CORS for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
def health_check():
    return {"status": "ok"}

