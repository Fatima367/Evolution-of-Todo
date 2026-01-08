"""User API schemas for request/response validation"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration request"""
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Check for bcrypt password length limitation (72 bytes)
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must be 72 bytes or less when encoded in UTF-8')
        return v


class UserRead(BaseModel):
    """Schema for user response (excludes password)"""
    id: UUID
    email: EmailStr
    name: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    email_notifications: bool
    task_reminders: bool
    weekly_summary: bool
    deletion_scheduled: bool
    scheduled_for_deletion_at: Optional[datetime]

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for user update request"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email_notifications: Optional[bool] = None
    task_reminders: Optional[bool] = None
    weekly_summary: Optional[bool] = None


class UserLogin(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class PasswordChange(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str


class PasswordConfirmation(BaseModel):
    """Schema for password confirmation (e.g., for account deletion)"""
    password: str
