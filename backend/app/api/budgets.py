from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import (
    BudgetCreate,
    BudgetResponse,
    CoinsyWidgetResponse,
)
from app.services.budget_service import (
    get_user_budgets,
    set_category_budget,
    delete_budget,
    get_coinsy_widget_status,
)

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=List[BudgetResponse])
def list_budgets(
    user_id: int = Query(..., description="User ID for budget list"),
    month: Optional[int] = Query(None, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year (YYYY)"),
    db: Session = Depends(get_db)
):
    """
    Returns category budget goals for a user with current spent amounts, percentage used, and 80%/100% alert status.
    """
    return get_user_budgets(db=db, user_id=user_id, month=month, year=year)


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(
    budget_in: BudgetCreate,
    user_id: int = Query(..., description="User ID setting the budget"),
    db: Session = Depends(get_db)
):
    """
    Sets or updates a monthly category budget cap.
    Checks 80%/100% thresholds and creates a stored CoinsyMessage alert for the Coinsy mascot widget.
    """
    try:
        return set_category_budget(db=db, user_id=user_id, budget_in=budget_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error setting budget: {str(e)}"
        )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_budget(
    budget_id: int,
    user_id: int = Query(..., description="User ID deleting the budget"),
    db: Session = Depends(get_db)
):
    """
    Deletes a monthly category budget goal.
    """
    success = delete_budget(db=db, user_id=user_id, budget_id=budget_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with id {budget_id} not found."
        )
    return None


@router.get("/coinsy-widget", response_model=CoinsyWidgetResponse)
def get_coinsy_widget(
    user_id: int = Query(..., description="User ID for widget status"),
    db: Session = Depends(get_db)
):
    """
    Returns latest stored notification message & mascot mood for the interactive Coinsy Mascot Widget.
    """
    return get_coinsy_widget_status(db=db, user_id=user_id)
