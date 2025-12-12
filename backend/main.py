# backend/main.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
import jose

from database import engine, get_db, Base
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- SECURITY ---
SECRET_KEY = "supersecretkey" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- SCHEMAS (FIXED) ---

# 1. Base schema (shared fields)
class SweetBase(BaseModel):
    name: str
    category: str
    price: float
    quantity: int

# 2. Schema for CREATING (Input) - No ID required
class SweetCreate(SweetBase):
    pass

# 3. Schema for READING (Output) - Includes ID
class SweetResponse(SweetBase):
    id: int
    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    username: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

# --- HELPERS ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

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

@app.post("/api/auth/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Updated to use SweetCreate for input, SweetResponse for output
@app.post("/api/sweets", response_model=SweetResponse, status_code=201)
def create_sweet(sweet: SweetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_sweet = models.Sweet(name=sweet.name, category=sweet.category, price=sweet.price, quantity=sweet.quantity)
    db.add(new_sweet)
    db.commit()
    db.refresh(new_sweet)
    return new_sweet

@app.get("/api/sweets", response_model=List[SweetResponse])
def get_sweets(db: Session = Depends(get_db)):
    return db.query(models.Sweet).all()

@app.get("/api/sweets/search", response_model=List[SweetResponse])
def search_sweets(name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Sweet)
    if name:
        query = query.filter(models.Sweet.name.contains(name))
    return query.all()

@app.post("/api/sweets/{sweet_id}/purchase")
def purchase_sweet(sweet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    if sweet.quantity <= 0:
        raise HTTPException(status_code=400, detail="Out of stock")
    sweet.quantity -= 1
    db.commit()
    db.refresh(sweet)
    return {"message": "Purchase successful", "remaining_quantity": sweet.quantity}

@app.put("/api/sweets/{sweet_id}", response_model=SweetResponse)
def update_sweet(sweet_id: int, sweet: SweetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not db_sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    
    db_sweet.name = sweet.name
    db_sweet.category = sweet.category
    db_sweet.price = sweet.price
    db_sweet.quantity = sweet.quantity
    
    db.commit()
    db.refresh(db_sweet)
    return db_sweet

@app.delete("/api/sweets/{sweet_id}", status_code=204)
def delete_sweet(sweet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Note: In a real app, you would check if current_user.is_admin here
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not db_sweet:
        raise HTTPException(status_code=404, detail="Sweet not found")
    
    db.delete(db_sweet)
    db.commit()
    return None