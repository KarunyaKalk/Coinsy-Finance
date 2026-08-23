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
