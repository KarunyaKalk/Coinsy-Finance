def test_create_category(client):
    payload = {
        "name": "Food & Dining",
        "type": "debit",
        "icon": "utensils",
        "color": "#EF4444",
        "is_default": True
    }
    response = client.post("/api/v1/categories", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Food & Dining"
    assert data["type"] == "debit"
    assert data["icon"] == "utensils"
    assert "id" in data

def test_list_categories(client):
    client.post("/api/v1/categories", json={"name": "Groceries", "type": "debit"})
    client.post("/api/v1/categories", json={"name": "Salary", "type": "credit"})

    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_category(client):
    created = client.post("/api/v1/categories", json={"name": "Shopping", "type": "debit"}).json()
    cat_id = created["id"]

    response = client.get(f"/api/v1/categories/{cat_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Shopping"

def test_update_category(client):
    created = client.post("/api/v1/categories", json={"name": "Transport", "type": "debit"}).json()
    cat_id = created["id"]

    response = client.put(f"/api/v1/categories/{cat_id}", json={"name": "Travel & Cab", "color": "#3B82F6"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Travel & Cab"
    assert data["color"] == "#3B82F6"

def test_delete_category(client):
    created = client.post("/api/v1/categories", json={"name": "Temp Category", "type": "debit"}).json()
    cat_id = created["id"]

    del_resp = client.delete(f"/api/v1/categories/{cat_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/v1/categories/{cat_id}")
    assert get_resp.status_code == 404
