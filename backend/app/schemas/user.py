"""User schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)
    role: UserRole = UserRole.FARMER


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)


class UserData(BaseModel):
    id: int
    firebase_uid: str
    phone_number: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    language_preference: str = "en"
    created_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserData] = None
