from datetime import datetime, date
from typing import Optional, List, Dict, Any
import re
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

    @field_validator('email')
    def validate_email_format(cls, v):
        if not v or not v.strip():
            raise ValueError('Email address is required.')
        email_str = v.strip().lower()
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email_str):
            raise ValueError('Please enter a valid email address.')
        return email_str

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password_strength(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]]', v):
            raise ValueError('Password must contain at least one special character (e.g. !@#$%^&*).')
        return v


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    type: str = Field(default="debit", description="debit or credit")
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: bool = False

class CategoryCreate(CategoryBase):
    user_id: Optional[int] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Transaction Schemas
class TransactionBase(BaseModel):
    date: date
    amount: float
    type: str = Field(default="debit", description="debit or credit")
    description: str
    category_id: Optional[int] = None
    raw_text: Optional[str] = None
    merchant_name: Optional[str] = None
    payment_mode: str = Field(default="UPI", description="UPI | Card | NetBanking | Cash")
    is_categorized_by_llm: bool = False
    confidence_score: Optional[float] = None

class TransactionCreate(TransactionBase):
    user_id: int

class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    raw_text: Optional[str] = None
    merchant_name: Optional[str] = None
    payment_mode: Optional[str] = None
    is_categorized_by_llm: Optional[bool] = None
    confidence_score: Optional[float] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Analytics & Spend Schemas
class CategorySpend(BaseModel):
    category_name: str
    total_spend: float
    percentage_of_total: float

class TimePeriodSpendBreakdown(BaseModel):
    period: str
    total_spend: float
    categories: List[CategorySpend]

class SpendAggregationResponse(BaseModel):
    timeframe: str
    total_spend: float
    category_totals: List[CategorySpend]
    periods: List[TimePeriodSpendBreakdown]

class CategoryComparison(BaseModel):
    category_name: str
    current_spend: float
    prior_spend: float
    change_amount: float
    percentage_change: Optional[float] = None
    trend: str  # increased | decreased | unchanged | new

class PeriodComparisonResponse(BaseModel):
    period_type: str  # mom | wow
    target_period: str
    prior_period: str
    total_current_spend: float
    total_prior_spend: float
    total_change_amount: float
    total_percentage_change: Optional[float] = None
    trend: str
    categories: List[CategoryComparison]

class SpendSummaryResponse(BaseModel):
    summary: str
    period_type: str
    target_period: str
    prior_period: str
    is_llm_generated: bool


# Insights & Batch Job Schemas
class CategoryPrediction(BaseModel):
    category_name: str
    predicted_spend: float
    avg_monthly_spend: float
    trend_direction: str  # upward | downward | stable
    percentage_change: Optional[float] = None

class PredictionResponse(BaseModel):
    user_id: int
    forecast_month: str
    total_predicted_spend: float
    explanation: str
    category_predictions: List[CategoryPrediction]
    created_at: datetime
    is_llm_generated: bool

class DailyTipResponse(BaseModel):
    user_id: int
    tip: str
    total_30d_spend: float
    top_category: Optional[str] = None
    created_at: datetime
    is_llm_generated: bool

class BatchJobResponse(BaseModel):
    status: str
    users_processed: int
    timestamp: datetime


# Budget & Advanced Analytics Schemas
class BudgetBase(BaseModel):
    category_id: int
    amount_limit: float
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)

class BudgetCreate(BudgetBase):
    user_id: Optional[int] = None

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    category_name: str
    current_spent: float
    percentage_used: float
    status: str  # normal | warning | exceeded
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DailyHeatmapItem(BaseModel):
    date: str
    total_spend: float
    transaction_count: int
    intensity_level: int  # 0 to 4

class CashFlowItem(BaseModel):
    period: str
    income: float
    expense: float
    savings: float
    savings_rate: float

class CashFlowResponse(BaseModel):
    timeframe: str
    periods: List[CashFlowItem]
    total_income: float
    total_expense: float
    total_savings: float
    avg_savings_rate: float

class CoinsyWidgetResponse(BaseModel):
    user_id: int
    message: str
    mascot_mood: str  # idle | thinking | happy | concerned | sleepy | celebrating
    alert_type: Optional[str] = None
    created_at: datetime


# Day 11 Personality & Recap Schemas
class PersonalityResponse(BaseModel):
    user_id: int
    streak_days: int
    money_mood: str  # thriving | calm | stressed
    money_mood_emoji: str
    money_mood_description: str
    roast_mode_enabled: bool = False

class MoneyRecapResponse(BaseModel):
    user_id: int
    month_label: str
    total_spend: float
    total_income: float
    total_savings: float
    savings_rate: float
    top_category: str
    top_category_spend: float
    top_merchant: str
    biggest_transaction_description: str
    biggest_transaction_amount: float
    spending_persona: str
    recap_story: str
    streak_days: int
    money_mood: str
    money_mood_emoji: str


# Module 7: Interview Prep & Job Application Schemas
class JobApplicationBase(BaseModel):
    company_name: str
    job_title: str
    job_description: str
    status: str = Field(default="Applied", description="Applied | Interview | Offered | Rejected")
    location: Optional[str] = None
    salary_range: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    user_id: Optional[int] = None

class JobApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None

class JobApplicationResponse(JobApplicationBase):
    id: int
    user_id: int
    created_at: datetime
    has_prep_pack: bool = False

    model_config = ConfigDict(from_attributes=True)

class UserResumeBase(BaseModel):
    title: str = "Default Resume"
    content: str

class UserResumeCreate(UserResumeBase):
    user_id: Optional[int] = None

class UserResumeResponse(UserResumeBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PrepPackItemResponse(BaseModel):
    id: int
    prep_pack_id: int
    item_type: str  # technical | behavioral | star_answer | company_notes
    title: str
    question: str
    star_situation: Optional[str] = None
    star_task: Optional[str] = None
    star_action: Optional[str] = None
    star_result: Optional[str] = None
    user_notes: Optional[str] = None
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)

class PrepPackItemUpdate(BaseModel):
    user_notes: Optional[str] = None
    is_completed: Optional[bool] = None

class InterviewPrepPackResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    company_context: Optional[str] = None
    resume_overlap_analysis: Optional[str] = None
    is_generated_by_llm: bool = False
    created_at: datetime
    items: List[PrepPackItemResponse] = []
    completed_count: int = 0
    total_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# Module 8: Central Settings & Audit Log Schemas
class UserSettingsBase(BaseModel):
    scan_frequency: str = "6h"
    ats_threshold: float = 75.0
    daily_app_cap: int = 15
    daily_email_cap: int = 5
    active_platforms: Dict[str, bool] = Field(
        default_factory=lambda: {
            "linkedin": True,
            "indeed": True,
            "glassdoor": False,
            "wellfound": True,
            "ziprecruiter": False
        }
    )
    platform_credentials: Dict[str, str] = Field(default_factory=dict)
    telegram_webhook_url: Optional[str] = None
    email_notification_address: Optional[str] = None

class UserSettingsUpdate(BaseModel):
    scan_frequency: Optional[str] = None
    ats_threshold: Optional[float] = None
    daily_app_cap: Optional[int] = None
    daily_email_cap: Optional[int] = None
    active_platforms: Optional[Dict[str, bool]] = None
    platform_credentials: Optional[Dict[str, str]] = None
    telegram_webhook_url: Optional[str] = None
    email_notification_address: Optional[str] = None

class UserSettingsResponse(UserSettingsBase):
    user_id: int
    updated_at: datetime

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action_type: str
    status: str
    platform: Optional[str] = None
    title: str
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BlockAlertTriggerRequest(BaseModel):
    platform: str = "LinkedIn"
    error_message: str = "CAPTCHA challenge detected on login page"






