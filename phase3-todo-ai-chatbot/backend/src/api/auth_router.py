"""Authentication API endpoints"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta

from src.database import get_session
from src.models.user import User
from src.schemas.user_schemas import UserCreate, UserLogin, UserRead, UserUpdate, TokenResponse
from src.auth.security import hash_password, verify_password, create_access_token
from src.auth.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Annotated[Session, Depends(get_session)]
):
    """Register a new user account

    Creates a new user with hashed password and returns JWT token for immediate login.
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )

    # Save user to database
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    session: Annotated[Session, Depends(get_session)]
):
    """Authenticate user and return JWT token"""
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user)
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: Annotated[User, Depends(get_current_user)]):
    """Logout current user

    With JWT tokens, logout is primarily handled on the client side by deleting the token.
    This endpoint validates the token and can be used for logging/auditing.
    """
    # JWT tokens are stateless, so logout is primarily client-side
    # This endpoint validates that the token is still valid
    return None


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get current authenticated user's information"""
    return UserRead.model_validate(current_user)


@router.put("/me", response_model=UserRead)
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Update current authenticated user's information"""
    # Update user fields if provided
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.email_notifications is not None:
        current_user.email_notifications = user_update.email_notifications
    if user_update.task_reminders is not None:
        current_user.task_reminders = user_update.task_reminders
    if user_update.weekly_summary is not None:
        current_user.weekly_summary = user_update.weekly_summary

    current_user.updated_at = datetime.utcnow()

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return UserRead.model_validate(current_user)


from src.schemas.user_schemas import UserCreate, UserLogin, UserRead, UserUpdate, TokenResponse, PasswordChange, PasswordConfirmation

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    passwords: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Change current user's password"""
    # Verify current password
    if not verify_password(passwords.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(passwords.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )

    # Check for bcrypt password length limitation (72 bytes)
    if len(passwords.new_password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be 72 bytes or less when encoded in UTF-8"
        )

    # Update password
    current_user.password_hash = hash_password(passwords.new_password)
    current_user.updated_at = datetime.utcnow()

    session.add(current_user)
    session.commit()

    return None


@router.delete("/me", status_code=status.HTTP_202_ACCEPTED)
async def delete_account(
    payload: PasswordConfirmation,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Schedule current user's account for deletion"""
    # Verify password
    if not verify_password(payload.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )

    # Soft delete the user
    current_user.is_active = False
    current_user.deletion_scheduled = True
    current_user.scheduled_for_deletion_at = datetime.utcnow() + timedelta(days=90)
    current_user.updated_at = datetime.utcnow()

    session.add(current_user)
    session.commit()

    return {"message": "Account scheduled for deletion in 90 days."}
