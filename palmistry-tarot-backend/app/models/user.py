import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    """
    The four roles from the spec (section 4.1). Using an Enum instead of a
    plain string means the database will reject any typo'd role value —
    it's constrained to exactly these four options.
    """
    USER = "user"
    TAROT_READER = "tarot_reader"
    SPIRITUAL_CONSULTANT = "spiritual_consultant"
    ADMINISTRATOR = "administrator"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # NEVER store plain-text passwords
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- Profile fields (spec section 4.2 "User Information") ---
    # Stored as plain text/comma-separated rather than a separate table:
    # it's a 1-to-1 relationship (one profile per user), so keeping it on
    # the same row avoids an unnecessary extra JOIN for a beginner project.
    age_group = Column(String, nullable=True)             # e.g. "18-24", "25-34"
    interests = Column(String, nullable=True)              # comma-separated, e.g. "astrology,meditation"
    spiritual_goals = Column(Text, nullable=True)           # free text, e.g. "build a daily reflection habit"
    reading_preferences = Column(String, nullable=True)     # e.g. "tarot,palmistry"

    # SQLAlchemy relationship: lets us write `user.readings` in Python and
    # get all of that user's saved readings, without writing a JOIN by hand.
    readings = relationship("Reading", back_populates="user", cascade="all, delete-orphan")
