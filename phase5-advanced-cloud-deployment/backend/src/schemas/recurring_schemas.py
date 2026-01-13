"""Recurring pattern API schemas for request/response validation"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RecurringPatternCreate(BaseModel):
    """Schema for creating a recurring pattern"""
    task_id: UUID = Field(..., description="Associated task UUID")
    frequency: str = Field(..., min_length=1, max_length=20, description="Recurrence frequency")
    interval: int = Field(1, ge=1, description="Repeat every N periods")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="For weekly: 0-6 (0=Monday)")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="For monthly: 1-31")
    month_of_year: Optional[int] = Field(None, ge=1, le=12, description="For yearly: 1-12")
    end_date: Optional[datetime] = Field(None, description="When to stop recurring (null = forever)")

    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        """Validate frequency is one of allowed values"""
        allowed = ['daily', 'weekly', 'monthly', 'yearly', 'custom']
        if v not in allowed:
            raise ValueError(f'Frequency must be one of: {", ".join(allowed)}')
        return v

    @field_validator('day_of_week')
    @classmethod
    def validate_day_of_week(cls, v: Optional[int], info) -> Optional[int]:
        """Validate day_of_week is required for weekly frequency"""
        if info.data.get('frequency') == 'weekly' and v is None:
            raise ValueError('day_of_week is required for weekly frequency')
        return v

    @field_validator('day_of_month')
    @classmethod
    def validate_day_of_month(cls, v: Optional[int], info) -> Optional[int]:
        """Validate day_of_month is required for monthly frequency"""
        if info.data.get('frequency') == 'monthly' and v is None:
            raise ValueError('day_of_month is required for monthly frequency')
        return v

    @field_validator('month_of_year')
    @classmethod
    def validate_month_of_year(cls, v: Optional[int], info) -> Optional[int]:
        """Validate month_of_year is required for yearly frequency"""
        if info.data.get('frequency') == 'yearly' and v is None:
            raise ValueError('month_of_year is required for yearly frequency')
        return v


class RecurringPatternUpdate(BaseModel):
    """Schema for updating a recurring pattern (all fields optional)"""
    frequency: Optional[str] = Field(None, min_length=1, max_length=20)
    interval: Optional[int] = Field(None, ge=1)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    month_of_year: Optional[int] = Field(None, ge=1, le=12)
    end_date: Optional[datetime] = None

    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v: Optional[str]) -> Optional[str]:
        """Validate frequency is one of allowed values"""
        if v is not None:
            allowed = ['daily', 'weekly', 'monthly', 'yearly', 'custom']
            if v not in allowed:
                raise ValueError(f'Frequency must be one of: {", ".join(allowed)}')
        return v


class RecurringPatternRead(BaseModel):
    """Schema for recurring pattern response"""
    id: int
    task_id: UUID
    user_id: UUID
    frequency: str
    interval: int
    day_of_week: Optional[int]
    day_of_month: Optional[int]
    month_of_year: Optional[int]
    end_date: Optional[datetime]
    last_generated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
