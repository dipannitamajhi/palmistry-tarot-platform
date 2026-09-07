"""Platform-wide analytics for the staff/admin dashboard.

Everything here returns data already shaped for a charting library
(Chart.js/Plotly, per the spec's tech stack) — flat lists of
`{label, value}`-style points — rather than raw ORM rows, so the
frontend never needs to know about the database schema.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

TREND_WINDOW_DAYS = 30


def platform_analytics(readings: list[Any], users: list[Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=TREND_WINDOW_DAYS)

    daily_counts: dict[str, int] = defaultdict(int)
    type_counts: Counter[str] = Counter()
    theme_counts: Counter[str] = Counter()
    score_total = 0.0
    score_count = 0
    ai_sourced = 0
    active_user_ids: set[int] = set()

    for r in readings:
        created = r.created_at
        if created is not None:
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            if created >= window_start:
                daily_counts[created.date().isoformat()] += 1

        type_counts[r.reading_type.value] += 1
        active_user_ids.add(r.user_id)

        try:
            details = json.loads(r.details) if r.details else {}
        except (json.JSONDecodeError, TypeError):
            details = {}
        interpretation = details.get("interpretation", {}) or {}

        for theme in interpretation.get("themes", []) or []:
            theme_counts[theme] += 1

        score = (interpretation.get("scores") or {}).get("overall_insight_score")
        if isinstance(score, (int, float)):
            score_total += score
            score_count += 1

        if interpretation.get("source") == "ai":
            ai_sourced += 1

    # Fill in zero-count days so a line/bar chart gets a continuous,
    # gap-free x-axis rather than only the days that had activity.
    daily_series = []
    for offset in range(TREND_WINDOW_DAYS - 1, -1, -1):
        day = (now - timedelta(days=offset)).date().isoformat()
        daily_series.append({"date": day, "count": daily_counts.get(day, 0)})

    role_counts = Counter(u.role.value for u in users)

    return {
        "totals": {
            "total_readings": len(readings),
            "total_users": len(users),
            "users_with_at_least_one_reading": len(active_user_ids),
            "ai_generated_readings": ai_sourced,
            "deterministic_readings": len(readings) - ai_sourced,
        },
        "readings_by_type": [{"type": t, "count": c} for t, c in type_counts.items()],
        "readings_last_30_days": daily_series,
        "top_themes": [{"theme": t, "count": c} for t, c in theme_counts.most_common(10)],
        "users_by_role": [{"role": r, "count": c} for r, c in role_counts.items()],
        "average_insight_score": round(score_total / score_count, 2) if score_count else None,
    }
