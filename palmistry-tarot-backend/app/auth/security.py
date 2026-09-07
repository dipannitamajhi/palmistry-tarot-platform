"""
Security helpers: password hashing and JWT tokens.

Two separate concerns here, both essential to understand:
1. Passwords are hashed with bcrypt — a one-way function. We can check if
   a password is correct, but we can never reverse a hash back to the
   original password. This means even if the database leaked, raw
   passwords wouldn't be exposed.
2. JWTs (JSON Web Tokens) are how the server proves "this request came
   from an already-logged-in user" without a database lookup on every
   single request. The token is signed with a secret key, so the server
   can trust it hasn't been tampered with.
"""

import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

# A secret must be explicitly configured outside development.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
