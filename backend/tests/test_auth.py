# backend/tests/test_auth.py
from fastapi.testclient import TestClient
# We are importing 'app' even though it doesn't exist yet!
# This is part of the TDD process.
from main import app 

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "securepassword"}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}