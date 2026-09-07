from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.models.user import UserRole


# --- What the client sends us ---

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --- What we send back ---
# Notice this never includes hashed_password. Pydantic's response_model
# in FastAPI strips out any field not listed here, so even if we
# accidentally pass the full DB object, the password hash never leaks
# into an API response.

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    age_group: Optional[str] = None
    interests: Optional[str] = None
    spiritual_goals: Optional[str] = None
    reading_preferences: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # lets this schema read directly from the SQLAlchemy model


class UserProfileUpdate(BaseModel):
    # Every field optional: the frontend only sends what the user actually
    # changed, and we don't want to accidentally wipe out other fields.
    name: Optional[str] = None
    age_group: Optional[str] = None
    interests: Optional[str] = None
    spiritual_goals: Optional[str] = None
    reading_preferences: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
