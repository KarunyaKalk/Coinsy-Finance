from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from app.db.models import Category, Transaction, Insight
from app.core.scheduler import InsightsScheduler


def _seed_historical_transactions(db_session, user_id: int):
    cat_food = Category(user_id=user_id, name="Food", type="debit", icon="utensils", color="#EF4444")
    cat_rent = Category(user_id=user_id, name="Rent", type="debit", icon="home", color="#8B5CF6")
    db_session.add_all([cat_food, cat_rent])
    db_session.commit()
    db_session.refresh(cat_food)
    db_session.refresh(cat_rent)

    today = date.today()
    d_30 = today - timedelta(days=10)
    d_60 = today - timedelta(days=40)
    d_90 = today - timedelta(days=70)

    txs = [
        # 3 months ago (Month -2)
        Transaction(user_id=user_id, category_id=cat_food.id, date=d_90, amount=100.0, type="debit", description="Groceries Month 1"),
        Transaction(user_id=user_id, category_id=cat_rent.id, date=d_90, amount=1000.0, type="debit", description="Rent Month 1"),

        # 2 months ago (Month -1)
        Transaction(user_id=user_id, category_id=cat_food.id, date=d_60, amount=150.0, type="debit", description="Groceries Month 2"),
        Transaction(user_id=user_id, category_id=cat_rent.id, date=d_60, amount=1000.0, type="debit", description="Rent Month 2"),

        # Current month (Last 30 days)
        Transaction(user_id=user_id, category_id=cat_food.id, date=d_30, amount=200.0, type="debit", description="Groceries Starbucks", merchant_name="Starbucks"),
        Transaction(user_id=user_id, category_id=cat_food.id, date=d_30 - timedelta(days=2), amount=50.0, type="debit", description="Coffee Starbucks", merchant_name="Starbucks"),
        Transaction(user_id=user_id, category_id=cat_food.id, date=d_30 - timedelta(days=4), amount=40.0, type="debit", description="Cafe Starbucks", merchant_name="Starbucks"),
        Transaction(user_id=user_id, category_id=cat_rent.id, date=d_30, amount=1000.0, type="debit", description="Rent Month 3"),
    ]
    db_session.add_all(txs)
    db_session.commit()
    return cat_food, cat_rent


def test_prediction_endpoint(client, db_session, sample_user):
    _seed_historical_transactions(db_session, sample_user.id)

    response = client.get(f"/api/v1/insights/prediction?user_id={sample_user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == sample_user.id
    assert data["total_predicted_spend"] > 0
    assert len(data["category_predictions"]) > 0
    assert "explanation" in data
    assert len(data["explanation"]) > 0

    # Verify prediction insight record is saved in DB
    insight_db = (
        db_session.query(Insight)
        .filter(Insight.user_id == sample_user.id, Insight.type == "prediction")
        .first()
    )
    assert insight_db is not None
    assert "Spend Forecast" in insight_db.title


def test_daily_tip_endpoint(client, db_session, sample_user):
    _seed_historical_transactions(db_session, sample_user.id)

    response = client.get(f"/api/v1/insights/daily-tip?user_id={sample_user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == sample_user.id
    assert data["total_30d_spend"] > 0
    assert data["top_category"] is not None
    assert len(data["tip"]) > 0

    # Specific tip content check (should mention top category or merchant)
    assert "Food" in data["tip"] or "Starbucks" in data["tip"] or "rent" in data["tip"].lower()

    # Verify daily tip insight is saved in DB
    insight_db = (
        db_session.query(Insight)
        .filter(Insight.user_id == sample_user.id, Insight.type == "daily_tip")
        .first()
    )
    assert insight_db is not None


def test_batch_run_job_endpoint(client, db_session, sample_user):
    _seed_historical_transactions(db_session, sample_user.id)

    response = client.post(f"/api/v1/insights/run-batch?user_id={sample_user.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["users_processed"] == 1


def test_prediction_llm_mock(client, db_session, sample_user):
    _seed_historical_transactions(db_session, sample_user.id)

    mock_llm_response = MagicMock()
    mock_llm_response.content = [MagicMock(text="Food spend is projected to rise to $240 next month due to increased dining trends.")]

    with patch("app.services.insights_service.settings.ANTHROPIC_API_KEY", "fake-key"):
        with patch("anthropic.Anthropic") as MockAnthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_llm_response
            MockAnthropic.return_value = mock_client

            response = client.get(f"/api/v1/insights/prediction?user_id={sample_user.id}&force_refresh=true")
            assert response.status_code == 200
            data = response.json()

            assert data["is_llm_generated"] is True
            assert "Food spend is projected to rise" in data["explanation"]


def test_scheduler_lifecycle():
    scheduler_instance = InsightsScheduler(interval_seconds=3600)
    scheduler_instance.start()
    assert scheduler_instance._thread is not None
    assert scheduler_instance._thread.is_alive()
    scheduler_instance.stop()
    assert not scheduler_instance._thread.is_alive()
