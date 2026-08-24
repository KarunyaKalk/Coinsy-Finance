from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="user", cascade="all, delete-orphan")
    coinsy_messages = relationship("CoinsyMessage", back_populates="user", cascade="all, delete-orphan")
    corrections = relationship("CategoryCorrection", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default="debit")  # debit | credit
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False, default="debit")  # debit | credit
    description = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)
    merchant_name = Column(String, nullable=True)
    payment_mode = Column(String, nullable=False, default="UPI")  # UPI | Card | NetBanking | Cash
    is_categorized_by_llm = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    amount_limit = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1 - 12
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # daily_tip | prediction | alert | recap
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="insights")

class CoinsyMessage(Base):
    __tablename__ = "coinsy_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # user | coinsy
    message = Column(Text, nullable=False)
    mascot_mood = Column(String, nullable=False, default="idle")  # idle | thinking | happy | concerned | sleepy | celebrating
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="coinsy_messages")

class CategoryCorrection(Base):
    __tablename__ = "category_corrections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    merchant_name = Column(String, nullable=True)
    corrected_category_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="corrections")


# Module 7: Interview Prep & Application Tracker Models
class UserResume(Base):
    __tablename__ = "user_resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False, default="Default Resume")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="Applied")  # Applied | Interview | Offered | Rejected
    location = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prep_packs = relationship("InterviewPrepPack", back_populates="job", cascade="all, delete-orphan")


class InterviewPrepPack(Base):
    __tablename__ = "interview_prep_packs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_applications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_context = Column(Text, nullable=True)
    resume_overlap_analysis = Column(Text, nullable=True)
    is_generated_by_llm = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobApplication", back_populates="prep_packs")
    items = relationship("PrepPackItem", back_populates="prep_pack", cascade="all, delete-orphan")


class PrepPackItem(Base):
    __tablename__ = "prep_pack_items"

    id = Column(Integer, primary_key=True, index=True)
    prep_pack_id = Column(Integer, ForeignKey("interview_prep_packs.id", ondelete="CASCADE"), nullable=False)
    item_type = Column(String, nullable=False)  # technical | behavioral | star_answer | company_notes
    title = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    star_situation = Column(Text, nullable=True)
    star_task = Column(Text, nullable=True)
    star_action = Column(Text, nullable=True)
    star_result = Column(Text, nullable=True)
    user_notes = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)

    prep_pack = relationship("InterviewPrepPack", back_populates="items")


# Module 8: Settings, Platform Management & Audit Log Models
class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    scan_frequency = Column(String, nullable=False, default="6h")  # 1h | 6h | 12h | 24h
    ats_threshold = Column(Float, nullable=False, default=75.0)
    daily_app_cap = Column(Integer, nullable=False, default=15)
    daily_email_cap = Column(Integer, nullable=False, default=5)
    active_platforms_json = Column(Text, nullable=True)  # JSON e.g. {"linkedin": true, "indeed": true}
    platform_credentials_json = Column(Text, nullable=True)  # JSON e.g. platform credentials
    telegram_webhook_url = Column(String, nullable=True)
    email_notification_address = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String, nullable=False)  # scrape_run | resume_generation | ats_score | application_submission | email_sent | captcha_blocked
    status = Column(String, nullable=False, default="success")  # success | warning | failed | blocked
    platform = Column(String, nullable=True)
    title = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)



