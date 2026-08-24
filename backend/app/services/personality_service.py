import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from sqlalchemy.orm import Session

import anthropic
from app.core.config import settings
from app.db.models import Transaction, Category, Budget
from app.models.schemas import (
    PersonalityResponse,
    MoneyRecapResponse,
    DailyTipResponse,
)
from app.services.budget_service import get_user_budgets, get_cash_flow_analytics
from app.services.insights_service import generate_daily_tip

logger = logging.getLogger(__name__)


def calculate_budget_streak(db: Session, user_id: int) -> int:
    """
    Calculates consecutive recent days where daily spend did not exceed the average daily budget target.
    """
    ref_d = date.today()
    # Compute daily limit from monthly budget totals
    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == user_id, Budget.month == ref_d.month, Budget.year == ref_d.year)
        .all()
    )
    total_budget_limit = sum(float(b.amount_limit) for b in budgets) if budgets else 3000.0
    daily_threshold = max(20.0, total_budget_limit / 30.0)

    # Fetch last 60 days debit transactions
    start_lookback = ref_d - timedelta(days=60)
    records = (
        db.query(Transaction.date, Transaction.amount)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "debit",
            Transaction.date >= start_lookback,
            Transaction.date <= ref_d
        )
        .all()
    )

    daily_spend_map: Dict[date, float] = {}
    for r in records:
        daily_spend_map[r.date] = daily_spend_map.get(r.date, 0.0) + float(r.amount)

    streak = 0
    curr_date = ref_d

    # Count consecutive days going backwards
    while True:
        day_spend = daily_spend_map.get(curr_date, 0.0)
        if day_spend <= daily_threshold:
            streak += 1
            curr_date -= timedelta(days=1)
        else:
            break

        if streak >= 60:
            break

    return streak


def calculate_money_mood(db: Session, user_id: int) -> Tuple[str, str, str]:
    """
    Calculates financial mood: 'thriving' (🚀), 'calm' (🌿), or 'stressed' (⚡).
    """
    ref_d = date.today()
    user_budgets = get_user_budgets(db, user_id=user_id, month=ref_d.month, year=ref_d.year)

    exceeded_count = sum(1 for b in user_budgets if b.status == "exceeded")
    warning_count = sum(1 for b in user_budgets if b.status == "warning")

    cashflow = get_cash_flow_analytics(db, user_id=user_id, timeframe="monthly")
    latest_savings_rate = cashflow.periods[-1].savings_rate if cashflow.periods else 0.0
    latest_savings = cashflow.periods[-1].savings if cashflow.periods else 0.0

    if exceeded_count > 0 or latest_savings < 0:
        mood = "stressed"
        emoji = "⚡"
        desc = "Spending is running hot! Over-budget alerts detected."
    elif latest_savings_rate >= 20.0 and warning_count == 0:
        mood = "thriving"
        emoji = "🚀"
        desc = "Financial superpower unlocked! Strong savings and 0 over-budget alerts."
    else:
        mood = "calm"
        emoji = "🌿"
        desc = "Balanced & steady. Spending is on track within target limits."

    return mood, emoji, desc


def get_personality_status(db: Session, user_id: int, roast_mode: bool = False) -> PersonalityResponse:
    streak = calculate_budget_streak(db, user_id)
    mood, emoji, desc = calculate_money_mood(db, user_id)

    return PersonalityResponse(
        user_id=user_id,
        streak_days=streak,
        money_mood=mood,
        money_mood_emoji=emoji,
        money_mood_description=desc,
        roast_mode_enabled=roast_mode
    )


def generate_personality_tip(db: Session, user_id: int, roast_mode: bool = False) -> DailyTipResponse:
    """
    Generates daily tip with standard or sarcastic Roast Mode tone.
    """
    if not roast_mode:
        return generate_daily_tip(db, user_id=user_id)

    # Roast Mode active
    cutoff_date = date.today() - timedelta(days=30)
    records = (
        db.query(
            Transaction.amount,
            Transaction.description,
            Transaction.merchant_name,
            Category.name.label("category_name")
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "debit",
            Transaction.date >= cutoff_date
        )
        .all()
    )

    if not records:
        roast_tip = "No transactions in 30 days? Either you're living off the grid or hiding your receipts from Coinsy! 😂"
        return DailyTipResponse(
            user_id=user_id,
            tip=roast_tip,
            total_30d_spend=0.0,
            top_category=None,
            created_at=datetime.utcnow(),
            is_llm_generated=False
        )

    df = pd.DataFrame(
        [
            {
                "amount": float(r.amount),
                "description": r.description or "",
                "merchant": r.merchant_name or "",
                "category": r.category_name or "Uncategorized"
            }
            for r in records
        ]
    )

    total_spend = round(float(df["amount"].sum()), 2)
    cat_grouped = df.groupby("category")["amount"].agg(["sum", "count"]).reset_index()
    cat_grouped.sort_values(by="sum", ascending=False, inplace=True)

    top_cat = cat_grouped.iloc[0]["category"]
    top_cat_amt = round(float(cat_grouped.iloc[0]["sum"]), 2)
    top_cat_count = int(cat_grouped.iloc[0]["count"])

    df["vendor"] = df["merchant"].replace("", None).fillna(df["description"])
    vendor_counts = df["vendor"].value_counts()
    top_vendor = vendor_counts.index[0] if not vendor_counts.empty else top_cat
    top_vendor_count = int(vendor_counts.iloc[0]) if not vendor_counts.empty else 1

    is_llm = False

    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip() != "":
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            prompt = (
                f"You are Coinsy, a hilarious, witty, and slightly sarcastic AI personal finance mascot in 'ROAST MODE'. "
                f"Roast the user's spending habits based on their actual 30-day data:\n"
                f"- Total Spend: ${total_spend:.2f}\n"
                f"- Top Spending Category: '{top_cat}' (${top_cat_amt:.2f}, {top_cat_count} transactions)\n"
                f"- Frequent Vendor: '{top_vendor}' ({top_vendor_count} orders/visits)\n\n"
                f"Write EXACTLY ONE hilarious, witty, lighthearted 1-2 sentence roast. "
                f"Mention their top category or vendor. Keep it funny, punchy, and friendly without being offensive."
            )
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            roast_tip = "🔥 ROAST: " + response.content[0].text.strip().replace("\n", " ")
            is_llm = True
        except Exception as e:
            logger.error(f"Error generating LLM roast tip: {e}")
            roast_tip = _fallback_roast_tip(top_cat, top_cat_amt, top_vendor, top_vendor_count)
    else:
        roast_tip = _fallback_roast_tip(top_cat, top_cat_amt, top_vendor, top_vendor_count)

    return DailyTipResponse(
        user_id=user_id,
        tip=roast_tip,
        total_30d_spend=total_spend,
        top_category=top_cat,
        created_at=datetime.utcnow(),
        is_llm_generated=is_llm
    )


def _fallback_roast_tip(top_cat: str, top_cat_amt: float, top_vendor: str, top_vendor_count: int) -> str:
    if top_vendor_count > 2 and top_vendor:
        return (
            f"🔥 ROAST: You spent ${top_cat_amt:.2f} on {top_cat} with {top_vendor_count} visits to {top_vendor}... "
            f"they should probably name a table after you at this point! 🍽️"
        )
    return (
        f"🔥 ROAST: ${top_cat_amt:.2f} spent on {top_cat} this month? "
        f"Your wallet is officially requesting a emergency vacation! 💸"
    )


def generate_monthly_recap(
    db: Session,
    user_id: int,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> MoneyRecapResponse:
    """
    Generates Spotify-Wrapped style shareable monthly money recap summary data.
    """
    ref_d = date.today()
    target_month = month or ref_d.month
    target_year = year or ref_d.year

    start_d, end_d = date(target_year, target_month, 1), (
        date(target_year + 1, 1, 1) - timedelta(days=1)
        if target_month == 12
        else date(target_year, target_month + 1, 1) - timedelta(days=1)
    )

    month_label = f"{start_d.strftime('%B %Y')}"

    records = (
        db.query(
            Transaction.amount,
            Transaction.type,
            Transaction.description,
            Transaction.merchant_name,
            Category.name.label("category_name")
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_d,
            Transaction.date <= end_d
        )
        .all()
    )

    if not records:
        streak = calculate_budget_streak(db, user_id)
        mood, emoji, _ = calculate_money_mood(db, user_id)
        return MoneyRecapResponse(
            user_id=user_id,
            month_label=month_label,
            total_spend=0.0,
            total_income=0.0,
            total_savings=0.0,
            savings_rate=0.0,
            top_category="N/A",
            top_category_spend=0.0,
            top_merchant="N/A",
            biggest_transaction_description="None",
            biggest_transaction_amount=0.0,
            spending_persona="The Zen Saver",
            recap_story=f"No transactions recorded for {month_label}. Start tracking to unlock your monthly Money Recap!",
            streak_days=streak,
            money_mood=mood,
            money_mood_emoji=emoji
        )

    df = pd.DataFrame(
        [
            {
                "amount": float(r.amount),
                "type": r.type,
                "description": r.description or "Expense",
                "merchant": r.merchant_name or "",
                "category": r.category_name or "Uncategorized"
            }
            for r in records
        ]
    )

    debit_df = df[df["type"] == "debit"]
    credit_df = df[df["type"] == "credit"]

    tot_spend = round(float(debit_df["amount"].sum()), 2) if not debit_df.empty else 0.0
    tot_income = round(float(credit_df["amount"].sum()), 2) if not credit_df.empty else 0.0
    tot_savings = round(tot_income - tot_spend, 2)
    savings_rate = round((tot_savings / tot_income) * 100, 2) if tot_income > 0 else 0.0

    # Top category
    if not debit_df.empty:
        cat_sums = debit_df.groupby("category")["amount"].sum().reset_index()
        cat_sums.sort_values(by="amount", ascending=False, inplace=True)
        top_cat = cat_sums.iloc[0]["category"]
        top_cat_amt = round(float(cat_sums.iloc[0]["amount"]), 2)

        # Biggest purchase
        biggest_row = debit_df.sort_values(by="amount", ascending=False).iloc[0]
        biggest_desc = biggest_row["description"]
        biggest_amt = round(float(biggest_row["amount"]), 2)

        # Top merchant
        debit_df["vendor"] = debit_df["merchant"].replace("", None).fillna(debit_df["description"])
        v_counts = debit_df["vendor"].value_counts()
        top_vendor = v_counts.index[0] if not v_counts.empty else top_cat
    else:
        top_cat = "N/A"
        top_cat_amt = 0.0
        biggest_desc = "None"
        biggest_amt = 0.0
        top_vendor = "N/A"

    # Assign Spotify-Wrapped Spending Persona
    if tot_spend > 0 and top_cat_amt / tot_spend >= 0.40 and top_cat == "Food":
        persona = "The Foodie Adventurer 🍕"
    elif tot_spend > 0 and top_cat_amt / tot_spend >= 0.35 and top_cat == "Shopping":
        persona = "The Trendsetter 🛍️"
    elif tot_spend > 0 and top_cat_amt / tot_spend >= 0.30 and top_cat == "Transport":
        persona = "The Commuter Explorer 🚗"
    elif savings_rate >= 30.0:
        persona = "The Wealth Architect 🏦"
    else:
        persona = "The Balanced Navigator ⚖️"

    recap_story = (
        f"In {month_label}, you spent ${tot_spend:.2f} and saved ${tot_savings:.2f} ({savings_rate:.1f}% savings rate)! "
        f"Your top spending category was {top_cat} (${top_cat_amt:.2f}), and your biggest purchase was '{biggest_desc}' (${biggest_amt:.2f}). "
        f"You earned the '{persona}' Spotify-Wrapped badge!"
    )

    streak = calculate_budget_streak(db, user_id)
    mood, emoji, _ = calculate_money_mood(db, user_id)

    return MoneyRecapResponse(
        user_id=user_id,
        month_label=month_label,
        total_spend=tot_spend,
        total_income=tot_income,
        total_savings=tot_savings,
        savings_rate=savings_rate,
        top_category=top_cat,
        top_category_spend=top_cat_amt,
        top_merchant=top_vendor,
        biggest_transaction_description=biggest_desc,
        biggest_transaction_amount=biggest_amt,
        spending_persona=persona,
        recap_story=recap_story,
        streak_days=streak,
        money_mood=mood,
        money_mood_emoji=emoji
    )
