from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Category, Transaction, CategoryCorrection
from app.services.llm_categorizer import (
    ALLOWED_CATEGORIES,
    DEFAULT_CATEGORY_ICONS,
    DEFAULT_CATEGORY_COLORS,
    categorize_transactions_batch
)

def ensure_default_categories(db: Session, user_id: Optional[int] = None) -> List[Category]:
    """
    Ensures system default categories exist in DB.
    """
    existing = db.query(Category).filter(Category.is_default == True).all()
    existing_names = {c.name for c in existing}
    
    created = []
    for cat_name in ALLOWED_CATEGORIES:
        if cat_name not in existing_names:
            cat = Category(
                name=cat_name,
                type="debit" if cat_name != "Salary" else "credit",
                icon=DEFAULT_CATEGORY_ICONS.get(cat_name, "help-circle"),
                color=DEFAULT_CATEGORY_COLORS.get(cat_name, "#64748B"),
                is_default=True,
                user_id=None
            )
            db.add(cat)
            created.append(cat)
            
    if created:
        db.commit()
        
    return db.query(Category).filter(
        (Category.is_default == True) | (Category.user_id == user_id if user_id else False)
    ).all()

def get_recent_user_corrections(db: Session, user_id: int, limit: int = 5) -> List[dict]:
    """
    Fetches up to `limit` recent category corrections by the user for few-shot prompting.
    """
    corrections = db.query(CategoryCorrection).filter(
        CategoryCorrection.user_id == user_id
    ).order_by(CategoryCorrection.created_at.desc()).limit(limit).all()
    
    return [
        {
            "description": c.description,
            "merchant_name": c.merchant_name,
            "category": c.corrected_category_name
        }
        for c in corrections
    ]

def record_user_category_correction(
    db: Session,
    user_id: int,
    description: str,
    merchant_name: Optional[str],
    corrected_category_name: str
):
    """
    Stores user's explicit category assignment/correction for future few-shot LLM prompts.
    """
    correction = CategoryCorrection(
        user_id=user_id,
        description=description,
        merchant_name=merchant_name,
        corrected_category_name=corrected_category_name
    )
    db.add(correction)
    db.commit()

def auto_categorize_user_transactions(db: Session, user_id: int, batch_size: int = 20) -> int:
    """
    Finds all uncategorized transactions for a user, fetches up to 5 recent user corrections,
    runs batched LLM categorization, maps back to DB Category IDs, and updates records.
    """
    categories = ensure_default_categories(db, user_id=user_id)
    cat_map = {c.name.lower(): c.id for c in categories}
    
    uncategorized_txs = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category_id == None
    ).all()
    
    if not uncategorized_txs:
        return 0
        
    recent_corrections = get_recent_user_corrections(db, user_id, limit=5)
    categorized_count = 0
    
    # Process in batches
    for i in range(0, len(uncategorized_txs), batch_size):
        batch = uncategorized_txs[i:i + batch_size]
        items_payload = [
            {
                "id": tx.id,
                "description": tx.description,
                "merchant_name": tx.merchant_name,
                "amount": tx.amount
            }
            for tx in batch
        ]
        
        batch_results = categorize_transactions_batch(items_payload, recent_corrections)
        result_map = {res["id"]: res for res in batch_results}
        
        for tx in batch:
            if tx.id in result_map:
                res = result_map[tx.id]
                assigned_cat_name = res["category"]
                cat_id = cat_map.get(assigned_cat_name.lower(), cat_map.get("other"))
                
                tx.category_id = cat_id
                tx.is_categorized_by_llm = True
                tx.confidence_score = res.get("confidence", 0.90)
                categorized_count += 1
                
    db.commit()
    return categorized_count
