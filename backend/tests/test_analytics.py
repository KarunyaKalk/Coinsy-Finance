from datetime import date
from unittest.mock import patch, MagicMock
from app.db.models import Category, Transaction


def _seed_test_transactions(db_session, user_id: int):
    # Create Categories
    cat_food = Category(user_id=user_id, name="Food", type="debit", icon="utensils", color="#EF4444")
    cat_transport = Category(user_id=user_id, name="Transport", type="debit", icon="car", color="#3B82F6")
    cat_shopping = Category(user_id=user_id, name="Shopping", type="debit", icon="shopping-bag", color="#EC4899")
    db_session.add_all([cat_food, cat_transport, cat_shopping])
    db_session.commit()
    db_session.refresh(cat_food)
    db_session.refresh(cat_transport)
    db_session.refresh(cat_shopping)

    # Seed transactions across July and August 2026
    txs = [
        # Prior month: July 2026
        Transaction(user_id=user_id, category_id=cat_food.id, date=date(2026, 7, 10), amount=100.0, type="debit", description="Groceries July"),
        Transaction(user_id=user_id, category_id=cat_transport.id, date=date(2026, 7, 15), amount=50.0, type="debit", description="Uber July"),

        # Target month: August 2026
        Transaction(user_id=user_id, category_id=cat_food.id, date=date(2026, 8, 5), amount=150.0, type="debit", description="Groceries Aug 1"),
        Transaction(user_id=user_id, category_id=cat_food.id, date=date(2026, 8, 20), amount=80.0, type="debit", description="Dining Aug 2"),
        Transaction(user_id=user_id, category_id=cat_transport.id, date=date(2026, 8, 12), amount=40.0, type="debit", description="Cab Aug"),
        Transaction(user_id=user_id, category_id=cat_shopping.id, date=date(2026, 8, 18), amount=200.0, type="debit", description="Clothes Aug"),

        # Credit transaction (should be excluded from spend analytics)
        Transaction(user_id=user_id, category_id=None, date=date(2026, 8, 1), amount=5000.0, type="credit", description="Salary Aug"),
    ]
    db_session.add_all(txs)
    db_session.commit()
    return cat_food, cat_transport, cat_shopping


def test_spend_aggregation_monthly(client, db_session, sample_user):
    _seed_test_transactions(db_session, sample_user.id)

    response = client.get(f"/api/v1/analytics/spend?timeframe=monthly&user_id={sample_user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["timeframe"] == "monthly"
    # Total debit spend: 100 + 50 + 150 + 80 + 40 + 200 = 620
    assert data["total_spend"] == 620.0

    # Category totals
    cat_names = [c["category_name"] for c in data["category_totals"]]
    assert "Food" in cat_names
    assert "Shopping" in cat_names
    assert "Transport" in cat_names

    # Periods (2026-07 and 2026-08)
    periods = [p["period"] for p in data["periods"]]
    assert "2026-07" in periods
    assert "2026-08" in periods

    aug_period = next(p for p in data["periods"] if p["period"] == "2026-08")
    assert aug_period["total_spend"] == 470.0  # 150 + 80 + 40 + 200


def test_spend_aggregation_weekly(client, db_session, sample_user):
    _seed_test_transactions(db_session, sample_user.id)

    response = client.get(f"/api/v1/analytics/spend?timeframe=weekly&user_id={sample_user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["timeframe"] == "weekly"
    assert data["total_spend"] == 620.0
    assert len(data["periods"]) > 0


def test_spend_aggregation_yearly(client, db_session, sample_user):
    _seed_test_transactions(db_session, sample_user.id)

    response = client.get(f"/api/v1/analytics/spend?timeframe=yearly&user_id={sample_user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["timeframe"] == "yearly"
    assert data["total_spend"] == 620.0
    assert len(data["periods"]) == 1
    assert data["periods"][0]["period"] == "2026"


def test_period_comparison_mom(client, db_session, sample_user):
    _seed_test_transactions(db_session, sample_user.id)

    response = client.get(
        f"/api/v1/analytics/comparison?period=mom&user_id={sample_user.id}&target_date=2026-08-20"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["period_type"] == "mom"
    assert data["target_period"] == "2026-08"
    assert data["prior_period"] == "2026-07"
    assert data["total_current_spend"] == 470.0  # 150 + 80 + 40 + 200
    assert data["total_prior_spend"] == 150.0    # 100 + 50
    assert data["total_change_amount"] == 320.0
    assert data["trend"] == "increased"

    # Category specific checks
    food_cat = next(c for c in data["categories"] if c["category_name"] == "Food")
    assert food_cat["current_spend"] == 230.0
    assert food_cat["prior_spend"] == 100.0
    assert food_cat["change_amount"] == 130.0
    assert food_cat["trend"] == "increased"

    shopping_cat = next(c for c in data["categories"] if c["category_name"] == "Shopping")
    assert shopping_cat["current_spend"] == 200.0
    assert shopping_cat["prior_spend"] == 0.0
    assert shopping_cat["trend"] == "new"


def test_period_comparison_wow(client, db_session, sample_user):
    _seed_test_transactions(db_session, sample_user.id)

    response = client.get(
        f"/api/v1/analytics/comparison?period=wow&user_id={sample_user.id}&target_date=2026-08-20"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["period_type"] == "wow"
    assert "target_period" in data
    assert "prior_period" in data


def test_spend_text_summary_fallback(client, db_session, sample_user):
    _seed_test_transactions(db_session, sample_user.id)

    # Without ANTHROPIC_API_KEY set, rule-based fallback summary should be returned
    response = client.get(
        f"/api/v1/analytics/summary?period=mom&user_id={sample_user.id}&target_date=2026-08-20"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["period_type"] == "mom"
    assert data["target_period"] == "2026-08"
    assert data["is_llm_generated"] is False
    assert "In 2026-08, your total spend was $470.00" in data["summary"]
    assert "increased by $320.00" in data["summary"]


def test_spend_text_summary_llm_mock(client, db_session, sample_user):
    _seed_test_transactions(db_session, sample_user.id)

    mock_llm_response = MagicMock()
    mock_llm_response.content = [MagicMock(text="Your spending in August 2026 increased by $320.00 overall. High increase in Shopping.")]

    with patch("app.services.spend_analytics.settings.ANTHROPIC_API_KEY", "fake-api-key"):
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_llm_response
            MockAnthropic.return_value = mock_client

            response = client.get(
                f"/api/v1/analytics/summary?period=mom&user_id={sample_user.id}&target_date=2026-08-20"
            )
            assert response.status_code == 200
            data = response.json()

            assert data["is_llm_generated"] is True
            assert "Your spending in August 2026" in data["summary"]


def test_invalid_timeframe_or_period(client, db_session, sample_user):
    res1 = client.get(f"/api/v1/analytics/spend?timeframe=invalid_timeframe&user_id={sample_user.id}")
    assert res1.status_code == 400

    res2 = client.get(f"/api/v1/analytics/comparison?period=invalid_period&user_id={sample_user.id}")
    assert res2.status_code == 400
