from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.reading import Reading
from app.models.user import User, UserRole
from app.services.analytics import platform_analytics
from app.services.insights import dashboard_summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

STAFF_ROLES = (UserRole.ADMINISTRATOR, UserRole.TAROT_READER, UserRole.SPIRITUAL_CONSULTANT)


@router.get("/me")
def my_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    readings = db.query(Reading).filter(Reading.user_id == current_user.id).order_by(Reading.created_at.desc()).all()
    return dashboard_summary(readings)


@router.get("/platform")
def platform_dashboard(
    db: Session = Depends(get_db),
    _staff: User = Depends(require_role(*STAFF_ROLES)),
):
    readings = db.query(Reading).order_by(Reading.created_at.desc()).all()
    report = dashboard_summary(readings)
    report["active_users"] = db.query(User).count()
    return report


@router.get("/platform/analytics")
def platform_analytics_dashboard(
    db: Session = Depends(get_db),
    _staff: User = Depends(require_role(*STAFF_ROLES)),
):
    """Chart-ready platform analytics: reading volume trend, type and role
    breakdowns, top themes, and AI-vs-deterministic interpretation mix.
    Restricted to Tarot Reader, Spiritual Consultant, and Administrator
    roles (spec section 4.10 - Admin Dashboard / Platform analytics)."""
    readings = db.query(Reading).all()
    users = db.query(User).all()
    return platform_analytics(readings, users)


@router.get("/role")
def role_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*STAFF_ROLES)),
):
    """Returns a view of the platform data shaped for the caller's own
    role (spec section 4.10 lists three *different* staff dashboards,
    not one shared view):

      * tarot_reader        -> reading analytics, user engagement,
                                session tracking, report management
      * spiritual_consultant -> user trend analysis, guidance
                                effectiveness, consultation insights
      * administrator        -> user management, platform analytics,
                                reading statistics, system reports
    """
    readings = db.query(Reading).all()
    users = db.query(User).all()
    base = platform_analytics(readings, users)
    role = current_user.role.value

    if role == "tarot_reader":
        return {
            "role": role,
            "reading_analytics": {
                "readings_by_type": base["readings_by_type"],
                "readings_last_30_days": base["readings_last_30_days"],
            },
            "user_engagement_insights": {"top_themes": base["top_themes"]},
            "session_tracking": {"total_readings": base["totals"]["total_readings"]},
            "report_management": {"note": "Use /api/reports to export any user's readings."},
        }

    if role == "spiritual_consultant":
        return {
            "role": role,
            "user_trend_analysis": {"top_themes": base["top_themes"], "users_by_role": base["users_by_role"]},
            "guidance_effectiveness": {"average_insight_score": base["average_insight_score"]},
            "consultation_insights": {
                "ai_generated_readings": base["totals"]["ai_generated_readings"],
                "deterministic_readings": base["totals"]["deterministic_readings"],
            },
        }

    # administrator
    return {
        "role": role,
        "user_management": {"total_users": base["totals"]["total_users"], "users_by_role": base["users_by_role"]},
        "platform_analytics": base,
        "reading_statistics": {
            "total_readings": base["totals"]["total_readings"],
            "users_with_at_least_one_reading": base["totals"]["users_with_at_least_one_reading"],
        },
        "system_reports": {"average_insight_score": base["average_insight_score"]},
    }