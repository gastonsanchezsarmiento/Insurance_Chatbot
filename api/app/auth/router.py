from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import timedelta

from . import jwt
from . import schema

router = APIRouter(tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/token", response_model=schema.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = jwt.authenticate_user(jwt.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = jwt.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}