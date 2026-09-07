import csv
import io
import json
from collections import Counter
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.reading import Reading, ReadingType
from app.models.user import User
from app.services.report_export import build_pdf, build_xlsx

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _my_readings(db: Session, current_user: User, reading_type: str | None = None) -> list[Reading]:
    query = db.query(Reading).filter(Reading.user_id == current_user.id)
    if reading_type:
        query = query.filter(Reading.reading_type == ReadingType(reading_type))
    return query.order_by(Reading.created_at.desc()).all()


@router.get("/me/trends")
def insight_trend_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Insight trend report (spec section 12): how the overall insight
    score and recurring themes have moved across this user's reading
    history, most recent first."""
    readings = _my_readings(db, current_user)
    points = []
    theme_counts: Counter[str] = Counter()

    for r in readings:
        try:
            details = json.loads(r.details) if r.details else {}
        except (json.JSONDecodeError, TypeError):
            details = {}
        interpretation = details.get("interpretation", {}) or {}
        scores = interpretation.get("scores", {}) or {}
        for theme in interpretation.get("themes", []) or []:
            theme_counts[theme] += 1
        points.append({
            "id": r.id,
            "type": r.reading_type.value,
            "date": r.created_at.isoformat() if r.created_at else None,
            "overall_insight_score": scores.get("overall_insight_score"),
        })

    points.reverse()  # oldest first, so the frontend can plot a trend line left-to-right
    return {
        "points": points,
        "top_themes": [{"theme": t, "count": c} for t, c in theme_counts.most_common(10)],
    }


ReportType = Literal["palm", "tarot"]


@router.get("/me.json")
def export_json(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    type: ReportType | None = Query(default=None, description="Filter to 'palm' or 'tarot' only — omit for all readings."),
):
    readings = _my_readings(db, current_user, type)
    payload = [{"id": r.id, "type": r.reading_type.value, "summary": r.summary, "details": json.loads(r.details), "created_at": r.created_at.isoformat()} for r in readings]
    filename = f"arcana-{type or 'readings'}.json"
    return Response(content=json.dumps(payload, indent=2), media_type="application/json", headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/me.csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    type: ReportType | None = Query(default=None),
):
    readings = _my_readings(db, current_user, type)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "type", "summary", "created_at"])
    for reading in readings:
        writer.writerow([reading.id, reading.reading_type.value, reading.summary, reading.created_at.isoformat()])
    filename = f"arcana-{type or 'readings'}.csv"
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/me.pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    type: ReportType | None = Query(default=None),
):
    """Palmistry report, Tarot report, or (default) the combined
    personality/spiritual-guidance report — spec section 12."""
    readings = _my_readings(db, current_user, type)
    pdf_bytes = build_pdf(current_user.name, readings)
    filename = f"arcana-{type or 'readings'}.pdf"
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/me.xlsx")
def export_xlsx(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    type: ReportType | None = Query(default=None),
):
    readings = _my_readings(db, current_user, type)
    xlsx_bytes = build_xlsx(current_user.name, readings)
    filename = f"arcana-{type or 'readings'}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )