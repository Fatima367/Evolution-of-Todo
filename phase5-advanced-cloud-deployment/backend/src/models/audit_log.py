"""Audit Log entity model"""
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship, Column, JSON

if TYPE_CHECKING:
    from .user import User


class AuditLog(SQLModel, table=True):
    """Audit log for all task operations

    Attributes:
        id: Unique identifier (auto-increment)
        task_id: Associated task (nullable - task may be deleted)
        user_id: User who performed operation
        operation: Operation type (created, updated, completed, deleted, uncompleted)
        changes: Before/after values (JSONB format)
        request_id: For distributed tracing
        ip_address: Client IP address (IPv4 or IPv6)
        user_agent: Client user agent
        created_at: When operation occurred
    """
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[UUID] = Field(default=None, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    operation: str = Field(max_length=20, nullable=False, index=True)
    changes: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    request_id: Optional[str] = Field(default=None, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="audit_logs")
