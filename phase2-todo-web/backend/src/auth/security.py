"""Security utilities for password hashing and JWT token generation"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from src.config import settings


# Password hashing context with explicit bcrypt configuration to handle length limitations
# Configure to avoid bcrypt initialization issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__rounds=12,
    # Use bcrypt with a specific backend to avoid initialization issues
    bcrypt__default_rounds=12
)

# Initialize bcrypt backend explicitly to handle potential initialization issues
# Note: CryptContext does not support direct scheme access via pwd_context["bcrypt"]
# passlib handles backend selection automatically, no manual intervention needed


def hash_password(password: str) -> str:
    """Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    # Ensure password is not longer than 72 bytes to comply with bcrypt limitation
    # Bcrypt has a 72-byte password length limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate at 72 bytes and decode back to string, handling potential multi-byte character cuts
        # We'll truncate the bytes first, then decode to avoid cutting multi-byte characters in the middle
        truncated_bytes = password_bytes[:72]
        # Find the right position to decode to avoid cutting multi-byte characters
        while len(truncated_bytes) > 0:
            try:
                final_password = truncated_bytes.decode('utf-8')
                break
            except UnicodeDecodeError:
                truncated_bytes = truncated_bytes[:-1]  # Remove the last byte and try again
        else:
            # If we can't decode any bytes, return an empty string (this shouldn't happen in practice)
            final_password = ""
    else:
        final_password = password  # Use the original password if it's within the limit

    return pwd_context.hash(final_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    # Truncate password to 72 bytes to comply with bcrypt limitation before verification
    # This ensures consistency with the hashing function
    plain_password_bytes = plain_password.encode('utf-8')
    if len(plain_password_bytes) > 72:
        # Truncate at 72 bytes and decode back to string, handling potential multi-byte character cuts
        # We'll truncate the bytes first, then decode to avoid cutting multi-byte characters in the middle
        truncated_bytes = plain_password_bytes[:72]
        # Find the right position to decode to avoid cutting multi-byte characters
        while len(truncated_bytes) > 0:
            try:
                final_password = truncated_bytes.decode('utf-8')
                break
            except UnicodeDecodeError:
                truncated_bytes = truncated_bytes[:-1]  # Remove the last byte and try again
        else:
            # If we can't decode any bytes, return an empty string (this shouldn't happen in practice)
            final_password = ""
    else:
        final_password = plain_password  # Use the original password if it's within the limit

    return pwd_context.verify(final_password, hashed_password)


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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt
