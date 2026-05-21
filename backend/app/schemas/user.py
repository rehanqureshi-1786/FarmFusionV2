from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone_number: Optional[str] = None
    language_preference: Optional[str] = "en"

    model_config = ConfigDict(extra='ignore')


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    firebase_uid: str
    created_at: Optional[datetime] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserData(BaseModel):
    user_id: int
    email: EmailStr


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None

    model_config = ConfigDict(extra='ignore')
