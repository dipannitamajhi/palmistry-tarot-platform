"""Notification & Engagement System (spec section 11).

Five notification types, all backed by the same `notifications` table:

  * daily_guidance     — a short reflective prompt, created at most once
                          per user per calendar day (see `ensure_daily_guidance`).
  * reading_reminder    — nudges a user back who hasn't had a reading in a
                          while (see `maybe_add_reading_reminder`).
  * insight_update      — fired right after a palm/tarot reading completes
                          (see `notify_reading_ready`, called from the
                          palm/tarot routers).
  * spiritual_growth_alert — fired when a user crosses a reading-count
                          milestone (see `maybe_add_growth_alert`).
  * platform_announcement — staff-authored, user_id is NULL, visible to
                          everyone (see the /api/notifications/announcement
                          endpoint).

Nothing here ever sends an email/push notification — it's an in-app feed,
which keeps the MVP dependency-free. Swapping in real delivery (email/SMS/
push) later only means adding a sender in this module; the call sites in
the routers don't need to change.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.models.reading import Reading
from app.models.user import User

DAILY_GUIDANCE_PROMPTS = [
    "Take a slow breath and notice one thing you're grateful for today.",
    "What's one small, honest step you could take toward a goal this week?",
    "Reflect on a recent choice — what did it reveal about what you value?",
    "Where in your life could a little more patience help right now?",
    "Name one strength you leaned on recently, even in a small moment.",
]

READING_REMINDER_AFTER = timedelta(days=7)
GROWTH_ALERT_MILESTONES = {3, 10, 25, 50}


def notify_reading_ready(db: Session, user: User, reading_type: str) -> None:
    """Insight update: fired right after a reading is saved."""
    title = "Your reading is ready"
    message = f"Your new {reading_type} reading and reflection guidance are ready to view in History."
    db.add(Notification(
        user_id=user.id,
        type=NotificationType.INSIGHT_UPDATE,
        title=title,
        message=message,
    ))
    db.commit()
    maybe_add_growth_alert(db, user)


def maybe_add_growth_alert(db: Session, user: User) -> None:
    """Spiritual growth alert: fired once when a user crosses a reading-count milestone."""
    count = db.query(Reading).filter(Reading.user_id == user.id).count()
    if count not in GROWTH_ALERT_MILESTONES:
        return
    already_sent = (
        db.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.type == NotificationType.GROWTH_ALERT,
            Notification.title.like(f"%{count} readings%"),
        )
        .first()
    )
    if already_sent:
        return
    db.add(Notification(
        user_id=user.id,
        type=NotificationType.GROWTH_ALERT,
        title=f"Milestone: {count} readings",
        message=f"You've completed {count} readings. Consider looking back at your History page for patterns in your reflections.",
    ))
    db.commit()


def ensure_daily_guidance(db: Session, user: User) -> None:
    """Create at most one daily_guidance notification per user per calendar day."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    existing = (
        db.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.type == NotificationType.DAILY_GUIDANCE,
            Notification.created_at >= today_start,
        )
        .first()
    )
    if existing:
        return
    prompt = DAILY_GUIDANCE_PROMPTS[user.id % len(DAILY_GUIDANCE_PROMPTS)]
    db.add(Notification(
        user_id=user.id,
        type=NotificationType.DAILY_GUIDANCE,
        title="Today's reflection",
        message=prompt,
    ))
    db.commit()


def maybe_add_reading_reminder(db: Session, user: User) -> None:
    """Reading reminder: fired if the user's most recent reading is 7+ days old
    (or they've never had one) and there isn't already an unread reminder."""
    last_reading = (
        db.query(Reading)
        .filter(Reading.user_id == user.id)
        .order_by(Reading.created_at.desc())
        .first()
    )
    now = datetime.now(timezone.utc)
    is_stale = last_reading is None or (now - last_reading.created_at.replace(tzinfo=timezone.utc)) > READING_REMINDER_AFTER
    if not is_stale:
        return

    unread_reminder = (
        db.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.type == NotificationType.READING_REMINDER,
            Notification.is_read.is_(False),
        )
        .first()
    )
    if unread_reminder:
        return

    db.add(Notification(
        user_id=user.id,
        type=NotificationType.READING_REMINDER,
        title="It's been a while",
        message="You haven't had a reading in over a week — a quick tarot draw or palm scan can be a nice reset.",
    ))
    db.commit()
