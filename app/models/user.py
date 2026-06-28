"""
KrishakBondhu - User Models
Pydantic schemas for user registration, login, and profile.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Request schema for user registration."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    phone: Optional[str] = None
    location: Optional[str] = None


class UserLogin(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Request schema for updating user profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_base64: Optional[str] = None


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: str
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime


class UserRoleUpdate(BaseModel):
    """Request schema for admin to change a user's role."""
    role: str = Field(..., pattern="^(user|expert|admin)$")


class TokenResponse(BaseModel):
    """Response schema for JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
