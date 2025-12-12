# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Import our new files
from database import engine, get_db, Base
import models

# 1. Create the database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. Define the Pydantic Schema (Validation)
class UserSchema(BaseModel):
    username: str
    password: str

# 4. Helper function to hash passwords
def get_password_hash(password):
    return pwd_context.hash(password)

# 5. The Real Register Endpoint
@app.post("/api/auth/register", status_code=201)
def register(user: UserSchema, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create new user model
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    
    # Add to DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}