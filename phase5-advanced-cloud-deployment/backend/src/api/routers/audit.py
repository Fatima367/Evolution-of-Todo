"""Audit log API endpoints"""
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, desc
from src.database import get_session
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.audit_log import AuditLog
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

class AuditLogRead(BaseModel):
    id: int
    task_id: Optional[UUID]
    operation: str
    changes: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AuditLogRead])
async def get_audit_logs(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Get audit logs for the authenticated user"""
    statement = select(AuditLog).where(
        AuditLog.user_id == current_user.id
    ).order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)
    
    results = session.exec(statement).all()
    return results
