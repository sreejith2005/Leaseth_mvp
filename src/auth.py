"""
Authentication and authorization
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from src.config import settings
from src.database import User
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Password Hashing
# ============================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# ============================================================
# JWT Tokens
# ============================================================

def create_access_token(user_id: int, username: str) -> str:
    """Create short-lived access token (15 minutes)"""
    expires = datetime.utcnow() + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "username": username,
        "type": "access",
        "exp": expires,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int, username: str) -> str:
    """Create long-lived refresh token (7 days)"""
    expires = datetime.utcnow() + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "username": username,
        "type": "refresh",
        "exp": expires,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None


def get_current_user(token: str, db: Session) -> Optional[User]:
    """Get current user from token"""
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        return None
    
    return user


# ============================================================
# User Management
# ============================================================

def create_user(db: Session, username: str, email: str, password: str, full_name: str = None) -> User:
    """Create new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise ValueError("User with this username or email already exists")
    
    # Create user
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role="landlord"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User created: {username}")
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username/password"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        logger.warning(f"Login attempt for non-existent user: {username}")
        return None
    
    if not verify_password(password, user.password_hash):
        logger.warning(f"Failed login for user: {username}")
        return None
    
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {username}")
        return None
    
    logger.info(f"User authenticated: {username}")
    return user
