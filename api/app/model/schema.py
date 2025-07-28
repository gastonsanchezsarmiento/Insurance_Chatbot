from typing import Optional
from pydantic import BaseModel

class Question(BaseModel):
    text: str

class Answer(BaseModel):
    text: str
    confidence: Optional[float] = None

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None