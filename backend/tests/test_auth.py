# backend/tests/test_auth.py
from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app)

# Helper to generate random username so tests don't clash
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def test_register_user():
    username = random_string()
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "securepassword"}
    )
    assert response.status_code == 201
    assert response.json() == {"message": "User created successfully"}