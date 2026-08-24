from datetime import date
from app.db.models import Category, Transaction, CoinsyMessage, Budget


def test_set_and_list_budget(client, db_session, sample_user):
    # Create test category
    cat = Category(user_id=sample_user.id, name="Dining Out", type="debit")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)

    # Seed transaction (spent $85 out of $100 budget -> 85% = warning alert)
    tx = Transaction(
        user_id=sample_user.id,
        category_id=cat.id,
        date=date.today(),
        amount=85.0,
        type="debit",
        description="Fancy Dinner"
    )
    db_session.add(tx)
    db_session.commit()

    # Set Budget
    payload = {
        "category_id": cat.id,
        "amount_limit": 100.0,
        "month": date.today().month,
        "year": date.today().year
    }
    res = client.post(f"/api/v1/budgets?user_id={sample_user.id}", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["amount_limit"] == 100.0
    assert data["current_spent"] == 85.0
    assert data["percentage_used"] == 85.0
    assert data["status"] == "warning"

    # Verify CoinsyMessage alert notification was stored
    msg_db = (
        db_session.query(CoinsyMessage)
        .filter(CoinsyMessage.user_id == sample_user.id)
        .order_by(CoinsyMessage.created_at.desc())
        .first()
    )
    assert msg_db is not None
    assert "85.0%" in msg_db.message
    assert msg_db.mascot_mood == "concerned"

    # List Budgets
    list_res = client.get(f"/api/v1/budgets?user_id={sample_user.id}")
    assert list_res.status_code == 200
    budgets = list_res.json()
    assert len(budgets) == 1
    assert budgets[0]["category_name"] == "Dining Out"


def test_exceeded_budget_alert(client, db_session, sample_user):
    cat = Category(user_id=sample_user.id, name="Shopping", type="debit")
    db_session.add(cat)
    db_session.commit()

    tx = Transaction(
        user_id=sample_user.id,
        category_id=cat.id,
        date=date.today(),
        amount=250.0,
        type="debit",
        description="Mall Clothes"
    )
    db_session.add(tx)
    db_session.commit()

    payload = {
        "category_id": cat.id,
        "amount_limit": 200.0,
        "month": date.today().month,
        "year": date.today().year
    }
    res = client.post(f"/api/v1/budgets?user_id={sample_user.id}", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["status"] == "exceeded"
    assert data["percentage_used"] == 125.0

    # Verify Coinsy Widget endpoint
    widget_res = client.get(f"/api/v1/budgets/coinsy-widget?user_id={sample_user.id}")
    assert widget_res.status_code == 200
    widget_data = widget_res.json()
    assert "exceeded" in widget_data["message"]
    assert widget_data["mascot_mood"] == "concerned"


def test_daily_heatmap_endpoint(client, db_session, sample_user):
    tx = Transaction(
        user_id=sample_user.id,
        date=date.today(),
        amount=120.0,
        type="debit",
        description="Weekend trip"
    )
    db_session.add(tx)
    db_session.commit()

    res = client.get(f"/api/v1/analytics/heatmap?user_id={sample_user.id}&days_back=30")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    assert any(i["total_spend"] > 0 for i in items)


def test_cashflow_endpoint(client, db_session, sample_user):
    # Credit income $5000, Debit expense $2000
    t1 = Transaction(user_id=sample_user.id, date=date.today(), amount=5000.0, type="credit", description="Salary")
    t2 = Transaction(user_id=sample_user.id, date=date.today(), amount=2000.0, type="debit", description="Rent & Utilities")
    db_session.add_all([t1, t2])
    db_session.commit()

    res = client.get(f"/api/v1/analytics/cashflow?user_id={sample_user.id}&timeframe=monthly")
    assert res.status_code == 200
    data = res.json()

    assert data["total_income"] == 5000.0
    assert data["total_expense"] == 2000.0
    assert data["total_savings"] == 3000.0
    assert data["avg_savings_rate"] == 60.0
