import io
import pytest
from app.services.llm_categorizer import categorize_transactions_batch, ALLOWED_CATEGORIES
from app.services.category_manager import (
    ensure_default_categories,
    record_user_category_correction,
    get_recent_user_corrections,
    auto_categorize_user_transactions
)
from app.db.models import Transaction, CategoryCorrection, Category

def test_allowed_categories_list():
    assert "Food" in ALLOWED_CATEGORIES
    assert "Transport" in ALLOWED_CATEGORIES
    assert "Rent" in ALLOWED_CATEGORIES
    assert "Utilities" in ALLOWED_CATEGORIES
    assert "Shopping" in ALLOWED_CATEGORIES
    assert "Entertainment" in ALLOWED_CATEGORIES
    assert "Subscriptions" in ALLOWED_CATEGORIES
    assert "Investments" in ALLOWED_CATEGORIES
    assert "Other" in ALLOWED_CATEGORIES

def test_batch_categorizer_rule_fallback():
    batch = [
        {"id": 1, "description": "Swiggy order #9123", "merchant_name": "Swiggy"},
        {"id": 2, "description": "Uber Ride to airport", "merchant_name": "Uber"},
        {"id": 3, "description": "Netflix Subscription", "merchant_name": "Netflix"},
        {"id": 4, "description": "Zerodha Coin Mutual Fund", "merchant_name": "Zerodha"},
        {"id": 5, "description": "Electricity Bill Payment", "merchant_name": "BESCOM"},
    ]

    results = categorize_transactions_batch(batch, recent_corrections=[])
    assert len(results) == 5
    
    res_map = {r["id"]: r["category"] for r in results}
    assert res_map[1] == "Food"
    assert res_map[2] == "Transport"
    assert res_map[3] == "Subscriptions"
    assert res_map[4] == "Investments"
    assert res_map[5] == "Utilities"

def test_user_corrections_recording_and_few_shot(client, sample_user, db_session):
    ensure_default_categories(db_session, user_id=sample_user.id)
    food_cat = db_session.query(Category).filter(Category.name == "Food").first()
    shopping_cat = db_session.query(Category).filter(Category.name == "Shopping").first()

    # Create transaction
    tx_resp = client.post("/api/v1/transactions", json={
        "user_id": sample_user.id,
        "date": "2026-08-23",
        "amount": 999.0,
        "type": "debit",
        "description": "Unusual Store Purchase",
        "merchant_name": "UnusualStore",
        "category_id": food_cat.id
    }).json()
    tx_id = tx_resp["id"]

    # User manually corrects category to Shopping
    update_resp = client.put(f"/api/v1/transactions/{tx_id}", json={
        "category_id": shopping_cat.id
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["category"]["name"] == "Shopping"
    assert update_resp.json()["is_categorized_by_llm"] is False

    # Check that correction was saved
    corrections = get_recent_user_corrections(db_session, user_id=sample_user.id, limit=5)
    assert len(corrections) == 1
    assert corrections[0]["description"] == "Unusual Store Purchase"
    assert corrections[0]["category"] == "Shopping"

def test_auto_categorization_on_csv_import(client, sample_user, db_session):
    ensure_default_categories(db_session, user_id=sample_user.id)

    csv_content = (
        "Date, Particulars, Withdrawal Amt., Deposit Amt.\n"
        "2026-08-20, UPI-ZOMATO-DINING, 450.00, \n"
        "2026-08-21, Spotify Premium, 119.00, \n"
        "2026-08-22, Amazon Retail India, 1899.00, \n"
    )

    response = client.post(
        "/api/v1/statements/import-csv",
        data={"user_id": sample_user.id},
        files={"file": ("statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 3

    # Verify transactions have been auto-categorized
    txs = client.get(f"/api/v1/transactions?user_id={sample_user.id}").json()
    assert len(txs) == 3

    zomato_tx = next(t for t in txs if "ZOMATO" in t["description"])
    assert zomato_tx["category"]["name"] == "Food"
    assert zomato_tx["is_categorized_by_llm"] is True

    spotify_tx = next(t for t in txs if "Spotify" in t["description"])
    assert spotify_tx["category"]["name"] == "Subscriptions"

    amazon_tx = next(t for t in txs if "Amazon" in t["description"])
    assert amazon_tx["category"]["name"] == "Shopping"
