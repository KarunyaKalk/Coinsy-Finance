from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Transaction, User
from app.services.csv_parser import parse_csv_statement
from app.services.pdf_parser.base import PasswordProtectedPDFError
from app.services.pdf_parser.manager import pdf_statement_manager
from app.services.category_manager import auto_categorize_user_transactions
from app.models.schemas import TransactionResponse

router = APIRouter(prefix="/statements", tags=["Statements"])

def process_and_store_transactions(db: Session, user_id: int, parsed_items: List[dict]) -> dict:
    if not parsed_items:
        return {
            "imported_count": 0,
            "skipped_duplicates_count": 0,
            "total_parsed": 0,
            "transactions": []
        }

    # Fetch existing transactions within date range for deduplication
    dates = [item["date"] for item in parsed_items]
    min_date, max_date = min(dates), max(dates)

    existing_txs = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= min_date,
        Transaction.date <= max_date
    ).all()

    existing_keys = {
        (
            tx.user_id,
            tx.date,
            round(tx.amount, 2),
            tx.type,
            tx.description.strip().lower()
        )
        for tx in existing_txs
    }

    imported_txs = []
    imported_count = 0
    skipped_duplicates_count = 0

    for item in parsed_items:
        key = (
            user_id,
            item["date"],
            round(item["amount"], 2),
            item["type"],
            item["description"].strip().lower()
        )
        
        if key in existing_keys:
            skipped_duplicates_count += 1
            continue

        new_tx = Transaction(
            user_id=user_id,
            date=item["date"],
            amount=item["amount"],
            type=item["type"],
            description=item["description"],
            raw_text=item.get("raw_text"),
            merchant_name=item.get("merchant_name"),
            payment_mode=item.get("payment_mode", "UPI")
        )
        db.add(new_tx)
        existing_keys.add(key)
        imported_txs.append(new_tx)
        imported_count += 1

    db.commit()

    if imported_count > 0:
        auto_categorize_user_transactions(db, user_id=user_id)

    for tx in imported_txs:
        db.refresh(tx)

    return {
        "imported_count": imported_count,
        "skipped_duplicates_count": skipped_duplicates_count,
        "total_parsed": len(parsed_items),
        "transactions": [TransactionResponse.model_validate(tx) for tx in imported_txs]
    }

@router.post("/import-csv")
async def import_csv_statement(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported for this endpoint"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    try:
        content = await file.read()
        parsed_items = parse_csv_statement(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing CSV statement: {str(e)}"
        )

    return process_and_store_transactions(db, user_id, parsed_items)

@router.post("/import-pdf")
async def import_pdf_statement(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for this endpoint"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    try:
        content = await file.read()
        parsed_items = pdf_statement_manager.parse_pdf_statement(content, password=password)
    except PasswordProtectedPDFError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF is password-protected or password supplied is incorrect",
            headers={"X-Password-Required": "true"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing PDF statement: {str(e)}"
        )

    return process_and_store_transactions(db, user_id, parsed_items)
