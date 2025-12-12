# backend/tests/test_sweets.py
from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app)

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

# Helper to get a valid token
def get_auth_token():
    username = random_string()
    password = "password123"
    # Register
    client.post("/api/auth/register", json={"username": username, "password": password})
    # Login
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    return response.json()["access_token"]

def test_create_sweet_unauthorized():
    # Try to add sweet without token
    response = client.post(
        "/api/sweets",
        json={"name": "Chocolate", "price": 10.5, "quantity": 100}
    )
    assert response.status_code == 401

def test_create_sweet_authorized():
    token = get_auth_token()
    # Try to add sweet WITH token
    response = client.post(
        "/api/sweets",
        json={"name": "Lollipop", "price": 0.5, "quantity": 200},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lollipop"
    assert "id" in data