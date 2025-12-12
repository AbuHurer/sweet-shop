# backend/tests/test_sweets.py
from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app)

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def get_auth_token():
    username = random_string()
    password = "password123"
    client.post("/api/auth/register", json={"username": username, "password": password})
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    return response.json()["access_token"]

def test_create_sweet_unauthorized():
    response = client.post(
        "/api/sweets",
        json={"name": "Chocolate", "category": "Bar", "price": 10.5, "quantity": 100}
    )
    assert response.status_code == 401

def test_create_sweet_authorized():
    token = get_auth_token()
    response = client.post(
        "/api/sweets",
        json={"name": "Lollipop", "category": "Candy", "price": 0.5, "quantity": 200},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lollipop"
    assert data["category"] == "Candy"
    assert "id" in data

def test_list_sweets():
    response = client.get("/api/sweets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_sweets_by_name():
    token = get_auth_token()
    client.post(
        "/api/sweets",
        json={"name": "Super Sour Candy", "category": "Sour", "price": 2.0, "quantity": 50},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Search for "Sour"
    response = client.get("/api/sweets/search?name=Sour")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Sour" in data[0]["name"]

def test_purchase_sweet():
    token = get_auth_token()
    create_response = client.post(
        "/api/sweets",
        json={"name": "KitKat", "category": "Wafer", "price": 1.0, "quantity": 10},
        headers={"Authorization": f"Bearer {token}"}
    )
    sweet_id = create_response.json()["id"]

    purchase_response = client.post(
        f"/api/sweets/{sweet_id}/purchase",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert purchase_response.status_code == 200
    
    # Verify stock decreased
    get_response = client.get("/api/sweets")
    my_sweet = next(s for s in get_response.json() if s["id"] == sweet_id)
    assert my_sweet["quantity"] == 9

def test_purchase_out_of_stock():
    token = get_auth_token()
    create_response = client.post(
        "/api/sweets",
        json={"name": "Air", "category": "Nothing", "price": 0.0, "quantity": 0},
        headers={"Authorization": f"Bearer {token}"}
    )
    sweet_id = create_response.json()["id"]

    response = client.post(
        f"/api/sweets/{sweet_id}/purchase",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Out of stock"