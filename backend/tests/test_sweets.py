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

def test_list_sweets():
    # We already added sweets in previous tests, but let's ensure we can fetch them
    response = client.get("/api/sweets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_sweets_by_name():
    # First, add a specific sweet to search for
    token = get_auth_token()
    client.post(
        "/api/sweets",
        json={"name": "Super Sour Candy", "price": 2.0, "quantity": 50},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Search for "Sour"
    response = client.get("/api/sweets/search?name=Sour")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Sour" in data[0]["name"]