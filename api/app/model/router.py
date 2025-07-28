from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import datetime
from typing import  List
from app.auth.jwt import get_current_user,fake_users_db, get_password_hash
from app.auth.schema import User
from app.model.services import get_chatbot_response 

from . import schema

router = APIRouter(tags=["model"])

conversation_db = []

@router.post("/register")
async def register_user(user_data: schema.RegisterRequest):
    if user_data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": get_password_hash(user_data.password),
    }
    return {"message": "User registered successfully"}

@router.post("/ask", response_model=schema.Answer)
async def ask_question(
    question: schema.Question,
    current_user: User = Depends(get_current_user)
):
    if not question.text.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    answer_text = get_chatbot_response(question.text)
    # answer_text = ""
    conversation_db.append({
        "question": question.text,
        "answer": answer_text,
        "timestamp": datetime.utcnow(),
        "user_id": current_user.username
    })
    return {"text": answer_text, "confidence": 0.9}

@router.get("/conversation", response_model=List[dict])
async def get_conversation_history(current_user: User = Depends(get_current_user)):
    return [conv for conv in conversation_db if conv["user_id"] == current_user.username]

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user