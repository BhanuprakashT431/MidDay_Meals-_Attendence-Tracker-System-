"""
Security & Authentication Module for Mid-Day Meal System
Implements bcrypt hashing, JWT tokens, Role-Based Access Control (RBAC),
and secure 6-digit Email OTP generation & verification with brute-force throttling.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security configuration (Loaded from env if present)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "karnataka-middaymeal-super-secret-key-2026-sec987#*!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
OTP_EXPIRE_MINUTES = 5
MAX_OTP_ATTEMPTS = 3

security_bearer = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_bearer)) -> dict:
    """FastAPI dependency to extract and verify the current authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def require_roles(allowed_roles: list[str]):
    """Role-based access control (RBAC) dependency factory."""
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}. Your role is: {user_role}",
            )
        return current_user
    return role_checker

def generate_secure_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return str(secrets.randbelow(900000) + 100000)

def hash_otp(otp: str, email: str) -> str:
    """Generate a SHA-256 hash of OTP with email as salt to prevent rainbow table attacks."""
    salt = SECRET_KEY[:16]
    return hashlib.sha256(f"{email.lower().strip()}:{otp}:{salt}".encode("utf-8")).hexdigest()

def verify_otp_hash(input_otp: str, email: str, stored_hash: str) -> bool:
    """Verify input OTP matches stored hash in constant time."""
    candidate_hash = hash_otp(input_otp, email)
    return secrets.compare_digest(candidate_hash, stored_hash)
