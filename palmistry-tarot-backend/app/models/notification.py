import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func

from app.database import Base


class NotificationType(str, enum.Enum):
    """The five notification types from the spec (section 11)."""
    DAILY_GUIDANCE = "daily_guidance"       # "Daily guidance notifications"
    READING_REMINDER = "reading_reminder"    # "Reading reminders"
    INSIGHT_UPDATE = "insight_update"        # "Insight updates"
    GROWTH_ALERT = "spiritual_growth_alert"  # "Spiritual growth alerts"
    ANNOUNCEMENT = "platform_announcement"   # "Platform announcements"


class Notification(Base):
    """
    One row per notification.

    user_id is nullable: a row with user_id = NULL is a platform-wide
    announcement (spec: "Platform announcements", staff-authored, visible
    to every user) instead of a personal one. Personal notifications
    (insight updates, reminders) always have a user_id.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
