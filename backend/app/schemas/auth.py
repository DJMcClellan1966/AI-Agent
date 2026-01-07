from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    refresh_token: str = None
    token_type: str = "bearer"
    checkout_url: Optional[str] = None


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserCreate(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
