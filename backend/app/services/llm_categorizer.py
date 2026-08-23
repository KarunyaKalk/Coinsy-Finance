import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import anthropic
from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Utilities",
    "Shopping",
    "Entertainment",
    "Subscriptions",
    "Investments",
    "Other"
]

DEFAULT_CATEGORY_ICONS = {
    "Food": "utensils",
    "Transport": "car",
    "Rent": "home",
    "Utilities": "zap",
    "Shopping": "shopping-bag",
    "Entertainment": "film",
    "Subscriptions": "tv",
    "Investments": "trending-up",
    "Other": "help-circle"
}

DEFAULT_CATEGORY_COLORS = {
    "Food": "#EF4444",
    "Transport": "#3B82F6",
    "Rent": "#8B5CF6",
    "Utilities": "#F59E0B",
    "Shopping": "#EC4899",
    "Entertainment": "#10B981",
    "Subscriptions": "#6366F1",
    "Investments": "#14B8A6",
    "Other": "#64748B"
}

def fallback_rule_categorizer(description: str, merchant_name: Optional[str] = None) -> Tuple[str, float]:
    desc = (description or "").lower()
    merch = (merchant_name or "").lower()
    text = f"{desc} {merch}"
    
    rules = [
        ("Food", ["swiggy", "zomato", "mcdonald", "starbucks", "food", "restaurant", "dining", "cafe", "grocer", "blinkit", "zepto", "supermarket"]),
        ("Transport", ["uber", "ola", "fuel", "petrol", "cab", "metro", "train", "toll", "rapido"]),
        ("Rent", ["rent", "landlord", "house rent"]),
        ("Utilities", ["electricity", "water", "gas", "bill", "recharge", "mobile", "wifi", "broadband", "bescom"]),
        ("Shopping", ["amazon", "flipkart", "myntra", "retail", "store", "cloth", "fashion", "mall"]),
        ("Entertainment", ["cinema", "movie", "pvr", "bookmyshow", "game", "steam", "playstation"]),
        ("Subscriptions", ["netflix", "spotify", "prime", "youtube", "apple", "disney", "hotstar"]),
        ("Investments", ["zerodha", "groww", "mf", "mutual fund", "stock", "sip", "nps", "coin"])
    ]
    
    for category, keywords in rules:
        if any(kw in text for kw in keywords):
            return category, 0.85
            
    return "Other", 0.50

def categorize_transactions_batch(
    transactions: List[Dict[str, Any]],
    recent_corrections: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, Any]]:
    """
    Categorizes a batch of transactions using Claude API with few-shot user corrections,
    falling back to heuristic rules if LLM key is absent or call fails.
    """
    if not transactions:
        return []

    # Check if API key is present
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.strip() == "":
        logger.info("No ANTHROPIC_API_KEY configured. Using heuristic rule categorizer.")
        results = []
        for tx in transactions:
            cat, conf = fallback_rule_categorizer(tx.get("description", ""), tx.get("merchant_name"))
            results.append({
                "id": tx["id"],
                "category": cat,
                "confidence": conf
            })
        return results

    # Construct prompt for Anthropic Claude
    corrections_prompt = ""
    if recent_corrections:
        corrections_prompt = "User Specific Preferences / Recent Category Corrections (Use as Few-Shot Examples):\n"
        for corr in recent_corrections[:5]:
            corrections_prompt += f"- Text: '{corr.get('description')}' (Merchant: '{corr.get('merchant_name', 'N/A')}') -> Category: '{corr.get('category')}'\n"

    items_to_categorize = [
        {
            "id": tx["id"],
            "description": tx.get("description", ""),
            "merchant": tx.get("merchant_name", "")
        }
        for tx in transactions
    ]

    system_prompt = (
        f"You are Coinsy, an expert finance categorization engine. "
        f"Categorize each transaction into EXACTLY ONE category from this permitted list: {ALLOWED_CATEGORIES}. "
        f"Return ONLY a valid JSON array of objects with keys 'id', 'category', and 'confidence' (float 0.0-1.0)."
    )

    user_prompt = (
        f"{corrections_prompt}\n"
        f"Categorize the following transaction list into JSON:\n"
        f"{json.dumps(items_to_categorize, indent=2)}\n\n"
        f"JSON Output:"
    )

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        content_text = response.content[0].text.strip()
        # Clean potential markdown JSON block ```json ... ```
        if content_text.startswith("```"):
            content_text = content_text.split("```")[1]
            if content_text.startswith("json"):
                content_text = content_text[4:]
        content_text = content_text.strip()

        parsed_results = json.loads(content_text)
        
        # Validate result format
        validated_results = []
        parsed_dict = {item["id"]: item for item in parsed_results if "id" in item}

        for tx in transactions:
            tx_id = tx["id"]
            if tx_id in parsed_dict:
                cat = parsed_dict[tx_id].get("category", "Other")
                if cat not in ALLOWED_CATEGORIES:
                    cat = "Other"
                conf = float(parsed_dict[tx_id].get("confidence", 0.90))
                validated_results.append({
                    "id": tx_id,
                    "category": cat,
                    "confidence": conf
                })
            else:
                cat, conf = fallback_rule_categorizer(tx.get("description", ""), tx.get("merchant_name"))
                validated_results.append({
                    "id": tx_id,
                    "category": cat,
                    "confidence": conf
                })

        return validated_results

    except Exception as e:
        logger.error(f"Error calling Claude API for categorization: {e}. Falling back to rule categorizer.")
        results = []
        for tx in transactions:
            cat, conf = fallback_rule_categorizer(tx.get("description", ""), tx.get("merchant_name"))
            results.append({
                "id": tx["id"],
                "category": cat,
                "confidence": conf
            })
        return results
