"""Notification API endpoints"""
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from src.database import get_session
from src.auth.dependencies import get_current_user
from src.models.user import User

router = APIRouter(prefix="/push-subscription", tags=["Notifications"])

@router.post("/", status_code=status.HTTP_200_OK)
async def save_push_subscription(
    subscription: dict,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Save user's push notification subscription"""
    current_user.push_subscription = subscription
    session.add(current_user)
    session.commit()
    return {"message": "Push subscription saved"}

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_push_subscription(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Remove user's push notification subscription"""
    current_user.push_subscription = None
    session.add(current_user)
    session.commit()
    return None
