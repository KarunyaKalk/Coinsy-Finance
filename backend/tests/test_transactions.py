def test_create_transaction(client, sample_user):
    cat_resp = client.post("/api/v1/categories", json={"name": "Food", "type": "debit"}).json()
    cat_id = cat_resp["id"]

    payload = {
        "user_id": sample_user.id,
        "category_id": cat_id,
        "date": "2026-08-23",
        "amount": 250.50,
        "type": "debit",
        "description": "Swiggy order #10293",
        "raw_text": "UPI/20260823/SWIGGY/250.50",
        "merchant_name": "Swiggy",
        "payment_mode": "UPI"
    }

    response = client.post("/api/v1/transactions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 250.50
    assert data["merchant_name"] == "Swiggy"
    assert data["user_id"] == sample_user.id
    assert data["category"]["id"] == cat_id

def test_list_transactions(client, sample_user):
    payload = {
        "user_id": sample_user.id,
        "date": "2026-08-23",
        "amount": 100.0,
        "type": "debit",
        "description": "Tea & Coffee"
    }
    client.post("/api/v1/transactions", json=payload)

    response = client.get(f"/api/v1/transactions?user_id={sample_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Tea & Coffee"

def test_update_transaction(client, sample_user):
    created = client.post("/api/v1/transactions", json={
        "user_id": sample_user.id,
        "date": "2026-08-23",
        "amount": 500.0,
        "type": "debit",
        "description": "Book purchase"
    }).json()
    tx_id = created["id"]

    response = client.put(f"/api/v1/transactions/{tx_id}", json={
        "amount": 450.0,
        "description": "Book purchase (discounted)"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 450.0
    assert data["description"] == "Book purchase (discounted)"

def test_delete_transaction(client, sample_user):
    created = client.post("/api/v1/transactions", json={
        "user_id": sample_user.id,
        "date": "2026-08-23",
        "amount": 99.0,
        "type": "debit",
        "description": "Subscription"
    }).json()
    tx_id = created["id"]

    del_resp = client.delete(f"/api/v1/transactions/{tx_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/v1/transactions/{tx_id}")
    assert get_resp.status_code == 404
