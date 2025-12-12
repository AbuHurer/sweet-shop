# backend/tests/test_login.py
from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app)

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def test_login_user():
    # 1. First we must register a user (so they exist)
    username = random_string()
    password = "securepassword"
    
    client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )

    # 2. Now try to login with those same credentials
    # Note: OAuth2 (used by FastAPI) expects form data, not JSON, for login usually,
    # but for simplicity in this Kata, let's stick to a JSON endpoint first.
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )

    # 3. Expect success and a token
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"