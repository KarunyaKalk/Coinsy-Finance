from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Transaction, Category
from app.models.schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services.category_manager import (
    record_user_category_correction,
    auto_categorize_user_transactions
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    user_id: Optional[int] = None,
    category_id: Optional[int] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if type is not None:
        query = query.filter(Transaction.type == type)
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))
        
    return query.order_by(Transaction.date.desc(), Transaction.id.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db)
):
    if transaction_in.category_id is not None:
        category = db.query(Category).filter(Category.id == transaction_in.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {transaction_in.category_id} does not exist"
            )

    transaction = Transaction(**transaction_in.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.post("/auto-categorize")
def trigger_auto_categorization(
    user_id: int,
    db: Session = Depends(get_db)
):
    categorized_count = auto_categorize_user_transactions(db, user_id=user_id)
    return {
        "user_id": user_id,
        "categorized_count": categorized_count,
        "status": "success"
    }

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )

    old_category_id = transaction.category_id
        
    if transaction_in.category_id is not None:
        category = db.query(Category).filter(Category.id == transaction_in.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {transaction_in.category_id} does not exist"
            )
        # If user explicitly changed or set category, record correction for LLM few-shot learning
        if old_category_id != transaction_in.category_id:
            record_user_category_correction(
                db=db,
                user_id=transaction.user_id,
                description=transaction.description,
                merchant_name=transaction.merchant_name,
                corrected_category_name=category.name
            )
            # Mark transaction as manually overridden
            transaction.is_categorized_by_llm = False
            transaction.confidence_score = 1.0
            
    update_data = transaction_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
        
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )
    db.delete(transaction)
    db.commit()
    return None
