import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_e2e_full_user_flow():
    # 1. Signup Flow
    unique_email = f"flowuser_{uuid.uuid4().hex[:8]}@coinsy.com"
    signup_payload = {
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Flow User"
    }
    signup_res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code in [200, 201], signup_res.text


    auth_data = signup_res.json()
    token = auth_data["access_token"]
    user_id = auth_data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Import CSV Statement Flow
    csv_content = (
        "Date,Description,Amount,Type\n"
        "2026-08-01,Swiggy Food Order A/C 50100123456789,250.00,debit\n"
        "2026-08-02,Uber Ride A/C 50100123456789,150.00,debit\n"
        "2026-08-03,Salary Credit A/C 50100123456789,5000.00,credit\n"
        "2026-08-05,Amazon Purchase,1200.00,debit\n"
    )
    files = {"file": ("statement.csv", csv_content.encode("utf-8"), "text/csv")}
    data = {"user_id": str(user_id)}
    import_res = client.post(
        "/api/v1/statements/import-csv",
        files=files,
        data=data,
        headers=headers
    )
    assert import_res.status_code == 200, import_res.text
    import_data = import_res.json()
    assert import_data["imported_count"] == 4


    # 3. Dashboard Analytics Flow
    spend_res = client.get(f"/api/v1/analytics/spend?timeframe=monthly&user_id={user_id}", headers=headers)
    assert spend_res.status_code == 200
    assert spend_res.json()["total_spend"] == 1600.0

    comp_res = client.get(f"/api/v1/analytics/comparison?period=mom&user_id={user_id}", headers=headers)
    assert comp_res.status_code == 200

    pred_res = client.get(f"/api/v1/insights/prediction?user_id={user_id}", headers=headers)
    assert pred_res.status_code == 200

    # 4. Budget Setup & Threshold Alerts Flow
    # Find category id for Food
    cats_res = client.get(f"/api/v1/categories?user_id={user_id}", headers=headers)
    categories = cats_res.json()
    food_cat = next((c for c in categories if c["name"] == "Food"), categories[0])

    # Set Food budget cap to $200 (spent $250 -> exceeded status!)
    budget_payload = {
        "category_id": food_cat["id"],
        "amount_limit": 200.0,
        "month": 8,
        "year": 2026
    }
    budget_res = client.post(f"/api/v1/budgets?user_id={user_id}", json=budget_payload, headers=headers)
    assert budget_res.status_code in [200, 201], budget_res.text

    budget_data = budget_res.json()
    assert budget_data["status"] == "exceeded"
    assert budget_data["percentage_used"] >= 100.0

    # 5. Coinsy Mascot Status & Companion Chat Flow
    widget_res = client.get(f"/api/v1/budgets/coinsy-widget?user_id={user_id}", headers=headers)
    assert widget_res.status_code == 200
    widget_data = widget_res.json()
    assert widget_data["mascot_mood"] in ["concerned", "happy", "thinking"]

    ask_payload = {
        "user_id": user_id,
        "message": "How can I lower my food expenses?",
        "roast_mode": False
    }
    ask_res = client.post("/api/v1/insights/ask", json=ask_payload, headers=headers)
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert "reply" in ask_data
    assert "mascot_mood" in ask_data
