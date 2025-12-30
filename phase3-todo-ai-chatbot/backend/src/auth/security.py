"""Security utilities for password hashing and JWT token generation"""
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from src.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    # Encode password to bytes
    password_bytes = password.encode('utf-8')

    # Ensure password is not longer than 72 bytes to comply with bcrypt limitation
    # Bcrypt has a 72-byte password length limit
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    # Encode both passwords to bytes
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')

    # Truncate plain password to 72 bytes for comparison
    # This ensures consistency with the hashing function
    if len(plain_password_bytes) > 72:
        plain_password_bytes = plain_password_bytes[:72]

    try:
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token

    Args:
        data: Data to encode in the token (must include 'sub' claim with user_id)
        expires_delta: Optional token expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt
