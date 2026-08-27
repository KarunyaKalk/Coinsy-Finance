from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

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


# Ask Coinsy Companion Schemas
class AskCoinsyRequest(BaseModel):
    message: str
    user_id: int
    roast_mode: bool = False

class AskCoinsyResponse(BaseModel):
    reply: str
    mascot_mood: str  # idle | thinking | happy | concerned | sleepy | celebrating
    is_llm_generated: bool = True
    created_at: datetime





