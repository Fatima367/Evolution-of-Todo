"""Reminder API schemas for request/response validation"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class ReminderCreate(BaseModel):
    """Schema for creating a reminder"""
    task_id: UUID = Field(..., description="Associated task UUID")
    remind_at: datetime = Field(..., description="When to send reminder (UTC)")

    @field_validator('remind_at')
    @classmethod
    def validate_remind_at(cls, v: datetime) -> datetime:
        """Validate remind_at is in the future"""
        if v < datetime.now(timezone.utc):
            raise ValueError('Reminder time must be in the future')
        return v


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder"""
    remind_at: Optional[datetime] = Field(None, description="When to send reminder (UTC)")
    sent: Optional[bool] = Field(None, description="Has reminder been sent")

    @field_validator('remind_at')
    @classmethod
    def validate_remind_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate remind_at is in the future if provided"""
        if v is not None and v < datetime.now(timezone.utc):
            raise ValueError('Reminder time must be in the future')
        return v


class ReminderRead(BaseModel):
    """Schema for reminder response"""
    id: int
    task_id: UUID
    user_id: UUID
    remind_at: datetime
    sent: bool
    sent_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
