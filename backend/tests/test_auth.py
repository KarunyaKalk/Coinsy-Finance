def test_signup_user(client):
    payload = {
        "email": "newuser@coinsy.app",
        "password": "securepassword123",
        "full_name": "New Coinsy User"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@coinsy.app"
    assert data["user"]["full_name"] == "New Coinsy User"


def test_signup_duplicate_email(client):
    payload = {
        "email": "dupe@coinsy.app",
        "password": "password123",
        "full_name": "User One"
    }
    res1 = client.post("/api/v1/auth/signup", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/signup", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_login_user_success(client):
    signup_payload = {
        "email": "loginuser@coinsy.app",
        "password": "mypassword123",
        "full_name": "Login User"
    }
    client.post("/api/v1/auth/signup", json=signup_payload)

    login_payload = {
        "email": "loginuser@coinsy.app",
        "password": "mypassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "loginuser@coinsy.app"


def test_login_user_invalid_credentials(client):
    login_payload = {
        "email": "nonexistent@coinsy.app",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401


def test_get_me_endpoint(client):
    signup_payload = {
        "email": "meuser@coinsy.app",
        "password": "mypassword123",
        "full_name": "Me User"
    }
    signup_res = client.post("/api/v1/auth/signup", json=signup_payload)
    token = signup_res.json()["access_token"]

    # Call /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "meuser@coinsy.app"
