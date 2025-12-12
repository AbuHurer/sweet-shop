# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define the data shape
class UserSchema(BaseModel):
    username: str
    password: str

@app.post("/api/auth/register", status_code=201)
def register(user: UserSchema):
    # Fake database logic for now (we just want the test to pass)
    return {"message": "User created successfully"}