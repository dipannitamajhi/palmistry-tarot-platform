import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ReadingType(str, enum.Enum):
    PALM = "palm"
    TAROT = "tarot"


class Reading(Base):
    """
    One row per completed reading. This is what makes the doc's "Reading
    history" and "Session History" dashboard features possible — without
    this table, every reading would vanish the moment the page refreshes.
    """
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)

    # ForeignKey links this row to a specific row in the users table.
    # This is how a relational database expresses "this reading belongs
    # to that user" without duplicating the user's data into every row.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    reading_type = Column(Enum(ReadingType), nullable=False)
    summary = Column(String, nullable=False)   # short line for a history list view
    details = Column(Text, nullable=False)      # full result, stored as a JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="readings")
