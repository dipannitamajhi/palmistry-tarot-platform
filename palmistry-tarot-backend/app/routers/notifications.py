from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.notification import Notification, NotificationType
from app.models.user import User, UserRole
from app.schemas.notification import AnnouncementCreate, NotificationOut
from app.services.notifications import ensure_daily_guidance, maybe_add_reading_reminder

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

STAFF_ROLES = (UserRole.ADMINISTRATOR, UserRole.TAROT_READER, UserRole.SPIRITUAL_CONSULTANT)


@router.get("/me", response_model=list[NotificationOut])
def my_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Personal notifications (daily guidance, reminders, insight updates,
    growth alerts) plus every platform-wide announcement, newest first.
    Also lazily creates today's daily-guidance prompt and a reading
    reminder if one's due, so the feed stays current without a
    background scheduler."""
    ensure_daily_guidance(db, current_user)
    maybe_add_reading_reminder(db, current_user)

    rows = (
        db.query(Notification)
        .filter(or_(Notification.user_id == current_user.id, Notification.user_id.is_(None)))
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        NotificationOut(
            id=row.id, type=row.type, title=row.title, message=row.message,
            is_read=row.is_read, is_announcement=row.user_id is None, created_at=row.created_at,
        )
        for row in rows
    ]


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Notification).filter(Notification.id == notification_id).first()
    if row is None or (row.user_id is not None and row.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Notification not found.")
    # Platform announcements (user_id is None) are shared, so "read" is
    # tracked per-viewer in a real product; for this MVP, marking one read
    # only applies to personal notifications to avoid hiding it for everyone.
    if row.user_id is not None:
        row.is_read = True
        db.commit()
        db.refresh(row)
    return NotificationOut(
        id=row.id, type=row.type, title=row.title, message=row.message,
        is_read=row.is_read, is_announcement=row.user_id is None, created_at=row.created_at,
    )


@router.post("/announcement", response_model=NotificationOut)
def post_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    _staff: User = Depends(require_role(*STAFF_ROLES)),
):
    """Platform announcements (spec section 11) — staff-authored, visible to all users."""
    row = Notification(
        user_id=None,
        type=NotificationType.ANNOUNCEMENT,
        title=payload.title,
        message=payload.message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return NotificationOut(
        id=row.id, type=row.type, title=row.title, message=row.message,
        is_read=row.is_read, is_announcement=True, created_at=row.created_at,
    )
