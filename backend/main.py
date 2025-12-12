# backend/main.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt # NEW: For creating tokens

from database import engine, get_db, Base
import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- SECURITY CONFIGURATION (NEW) ---
# In a real app, hide this SECRET_KEY in an environment variable!
SECRET_KEY = "supersecretkey" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- SCHEMAS ---
class UserSchema(BaseModel):
    username: str
    password: str

# NEW: Schema for Login Request
class LoginSchema(BaseModel):
    username: str
    password: str

# --- HELPER FUNCTIONS ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password): # NEW
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict): # NEW
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- ENDPOINTS ---

@app.post("/api/auth/register", status_code=201)
def register(user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# NEW: Login Endpoint
@app.post("/api/auth/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):
    # 1. Find user
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    # 2. Check if user exists AND password matches
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create Token
    access_token = create_access_token(data={"sub": db_user.username})
    
    # 4. Return Token
    return {"access_token": access_token, "token_type": "bearer"}