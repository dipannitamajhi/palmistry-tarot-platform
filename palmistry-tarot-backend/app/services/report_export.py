"""PDF and Excel export for a user's reading history.

Both builders take the same rows the JSON/CSV exporters in
`app/routers/reports.py` already use (a list of `Reading` ORM rows) and
return raw bytes, so the router just has to pick the right media type and
filename. Keeping the parsing/shaping logic in one `_rows` helper means
the four export formats (JSON, CSV, PDF, XLSX) can never quietly drift
out of sync with each other.
"""

from __future__ import annotations

import io
import json
from typing import Any

from fpdf import FPDF
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

DISCLAIMER = "For entertainment and self-reflection only; not a prediction, diagnosis, or professional advice."

BRAND_PURPLE = "4C1D95"


def _rows(readings: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for r in readings:
        try:
            details = json.loads(r.details) if r.details else {}
        except (json.JSONDecodeError, TypeError):
            details = {}
        interpretation = details.get("interpretation", {}) or {}
        scores = interpretation.get("scores", {}) or {}
        rows.append(
            {
                "id": r.id,
                "type": r.reading_type.value,
                "summary": r.summary,
                "created_at": r.created_at.isoformat() if r.created_at else "",
                "themes": interpretation.get("themes", []),
                "narrative_summary": interpretation.get("summary", ""),
                "personality": interpretation.get("personality", {}) or {},
                "guidance": interpretation.get("guidance", []) or [],
                "overall_insight_score": scores.get("overall_insight_score", ""),
                "source": interpretation.get("source", ""),
            }
        )
    return rows


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------

def build_pdf(user_name: str, readings: list[Any]) -> bytes:
    """A readable, printable report: one section per reading with its
    themes, personality notes, and recommended actions."""
    rows = _rows(readings)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "Arcana - Reading History Report", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Prepared for: {user_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Total readings: {len(rows)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, DISCLAIMER)
    pdf.ln(4)
    pdf.set_draw_color(180, 160, 220)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(6)

    if not rows:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, "No readings yet.", new_x="LMARGIN", new_y="NEXT")

    for row in rows:
        pdf.set_font("Helvetica", "B", 14)
        title = f"{row['type'].title()} reading  -  {row['created_at'][:10] or 'undated'}"
        pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, row["summary"])

        if row["themes"]:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Themes", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, ", ".join(row["themes"]))

        if row["narrative_summary"]:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Reflection", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, row["narrative_summary"])

        personality = row["personality"]
        if personality:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Personality notes", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            for label, key in (("Strength", "strength"), ("Growth edge", "growth_edge"), ("Reflection prompt", "reflection_prompt")):
                if personality.get(key):
                    pdf.multi_cell(0, 5, f"- {label}: {personality[key]}")

        if row["guidance"]:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, "Guidance", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            for item in row["guidance"]:
                category = item.get("category", "").title()
                action = item.get("action", "")
                pdf.multi_cell(0, 5, f"- {category}: {action}")

        if row["overall_insight_score"] != "":
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, f"Overall insight score: {row['overall_insight_score']}  (source: {row['source'] or 'n/a'})", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(5)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(5)

    output = pdf.output()
    # fpdf2 returns a bytearray; normalize to bytes for the Response body.
    return bytes(output)


# --------------------------------------------------------------------------
# Excel
# --------------------------------------------------------------------------

def build_xlsx(user_name: str, readings: list[Any]) -> bytes:
    """Two sheets: a flat 'Readings' summary table for filtering/sorting,
    and an 'Interpretation Detail' sheet with the personality notes and
    guidance items broken out row-by-row for deeper analysis."""
    rows = _rows(readings)

    wb = Workbook()
    summary_ws = wb.active
    summary_ws.title = "Readings"

    headers = ["ID", "Type", "Created At", "Summary", "Themes", "Overall Insight Score", "Source"]
    summary_ws.append(headers)
    header_fill = PatternFill(start_color=BRAND_PURPLE, end_color=BRAND_PURPLE, fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for col_idx in range(1, len(headers) + 1):
        cell = summary_ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font

    for row in rows:
        summary_ws.append(
            [
                row["id"],
                row["type"],
                row["created_at"],
                row["summary"],
                ", ".join(row["themes"]),
                row["overall_insight_score"],
                row["source"],
            ]
        )

    for col_idx, header in enumerate(headers, start=1):
        summary_ws.column_dimensions[get_column_letter(col_idx)].width = max(16, len(header) + 6)
    summary_ws.freeze_panes = "A2"

    detail_ws = wb.create_sheet("Interpretation Detail")
    detail_headers = ["Reading ID", "Type", "Field", "Value"]
    detail_ws.append(detail_headers)
    for col_idx in range(1, len(detail_headers) + 1):
        cell = detail_ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font

    for row in rows:
        for label, key in (("Strength", "strength"), ("Growth edge", "growth_edge"), ("Reflection prompt", "reflection_prompt")):
            value = row["personality"].get(key)
            if value:
                detail_ws.append([row["id"], row["type"], f"personality.{label.lower().replace(' ', '_')}", value])
        for item in row["guidance"]:
            detail_ws.append([row["id"], row["type"], f"guidance.{item.get('category', '')}", item.get("action", "")])

    for col_idx, header in enumerate(detail_headers, start=1):
        detail_ws.column_dimensions[get_column_letter(col_idx)].width = max(16, len(header) + 6)
    detail_ws.freeze_panes = "A2"

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
