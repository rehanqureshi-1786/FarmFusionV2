"""
User schemas for request/response validation.
"""
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
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    pincode: Optional[str] = None
    preferred_language: str = "en"


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    pincode: Optional[str] = None
    preferred_language: Optional[str] = None
    notification_enabled: Optional[bool] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    preferred_language: str
    notification_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=255)
