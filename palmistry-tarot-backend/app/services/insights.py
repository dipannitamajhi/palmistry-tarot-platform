"""Interpretation and guidance generation.

Two paths produce the exact same response shape:

  * `_build_ai_interpretation`  — calls an LLM (via app.services.ai_client)
    to write the reflective, natural-language parts of the report
    (summary, themes, personality notes, guidance, life trends).
  * `_build_deterministic_interpretation` — the original template-based
    generator. It never fails and never calls out to a third party, so it
    is always available as a fallback.

`build_interpretation` is the single entry point routers call. It tries
the AI path only if OPENAI_API_KEY is configured, validates the shape of
whatever comes back, and falls back to the deterministic path on *any*
problem (missing key, network error, timeout, malformed JSON, missing
fields) so a reading is never blocked by a third-party outage.

The numeric scores are always computed locally with the weighted formula
from the product spec (section 8) rather than trusted from the model —
that keeps the "Weighted Scoring Model" honest and reproducible instead of
being whatever number an LLM feels like writing.

Palmistry and tarot are presented as tools for reflection, not factual
predictions or health/financial advice, in both paths.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from typing import Any

from app.data.tarot_deck import FULL_DECK
from app.services.ai_client import AIUnavailable, chat_json, is_configured

logger = logging.getLogger(__name__)

# Built once from the full 78-card deck (see app/data/tarot_deck.py) so
# theme extraction works uniformly for both Major Arcana ("The Hermit" ->
# "reflection") and Minor Arcana ("Three of Cups" -> "community") cards,
# instead of a hardcoded list that only covered the old 22-card deck.
_CARD_KEYWORDS = {card["name"].lower(): card["keyword"] for card in FULL_DECK}

DISCLAIMER = "For entertainment and self-reflection only; it is not a prediction, diagnosis, or professional advice."

REQUIRED_GUIDANCE_ITEMS = 5
REQUIRED_TREND_ITEMS = 3

# The doc's "Insight Categories" list (section 5). Guidance items are
# tagged with one of these so the frontend/reports can group a reading's
# recommendations the same way the spec describes, instead of just three
# fixed buckets.
INSIGHT_CATEGORIES = [
    "personality",
    "relationships",
    "career",
    "finance",
    "health_and_wellness",
    "personal_growth",
    "life_opportunities",
]


def build_interpretation(kind: str, source: dict[str, Any], profile: Any | None) -> dict[str, Any]:
    """Create a reflective report from a palm or tarot result.

    Tries the AI-backed generator first (if configured), otherwise —
    or if that call fails or returns something malformed — falls back
    to the deterministic generator so the endpoint always returns a
    complete, well-formed report.
    """
    scores = _scores(kind, source, profile)

    if is_configured():
        try:
            narrative = _build_ai_interpretation(kind, source, profile)
            return {**narrative, "disclaimer": DISCLAIMER, "scores": scores, "source": "ai"}
        except AIUnavailable as exc:
            logger.warning("AI interpretation unavailable, falling back to deterministic path: %s", exc)

    narrative = _build_deterministic_interpretation(kind, source, profile)
    return {**narrative, "disclaimer": DISCLAIMER, "scores": scores, "source": "deterministic"}


# --------------------------------------------------------------------------
# AI-backed path
# --------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a thoughtful reflection-and-journaling assistant embedded in a \
palmistry/tarot entertainment app. Your job is to turn a card spread or a \
description of palm features into warm, specific, self-reflection content.

Hard rules:
- This is entertainment and self-reflection, never fortune-telling presented as fact.
- Never give medical, legal, financial, or mental-health advice or diagnoses.
- Never make claims about the future as if they are certain to happen.
- Keep language warm, concrete, and non-generic — reference the actual cards or \
palm features you were given, not vague platitudes.
- The "guidance" list must draw its "category" values from exactly this set,
  covering as many as make sense for this reading (at least 5):
  personality, relationships, career, finance, health_and_wellness,
  personal_growth, life_opportunities.
- Respond with ONLY a JSON object matching exactly this shape, no extra keys, no markdown:
{
  "summary": "2-3 sentences summarizing the reading",
  "themes": ["theme1", "theme2", ...],
  "personality": {
    "strength": "1 sentence",
    "growth_edge": "1 sentence",
    "reflection_prompt": "1 open-ended question"
  },
  "guidance": [
    {"category": "personal_growth", "action": "a concrete, doable action"},
    {"category": "relationships", "action": "a concrete, doable action"},
    {"category": "career", "action": "a concrete, doable action"},
    {"category": "finance", "action": "a concrete, doable action"},
    {"category": "health_and_wellness", "action": "a concrete, doable action"}
  ],
  "life_trends": [
    {"period": "Now", "theme": "...", "guidance": "..."},
    {"period": "Next step", "theme": "...", "guidance": "..."},
    {"period": "Longer term", "theme": "...", "guidance": "..."}
  ]
}"""


def _build_ai_interpretation(kind: str, source: dict[str, Any], profile: Any | None) -> dict[str, Any]:
    user_prompt = _user_prompt(kind, source, profile)
    payload = chat_json(SYSTEM_PROMPT, user_prompt)
    _validate_narrative_shape(payload)
    return {
        "summary": payload["summary"],
        "themes": payload["themes"],
        "personality": payload["personality"],
        "guidance": payload["guidance"][:REQUIRED_GUIDANCE_ITEMS],
        "life_trends": payload["life_trends"][:REQUIRED_TREND_ITEMS],
        "profile_context_used": _profile_context(profile) or None,
    }


def _user_prompt(kind: str, source: dict[str, Any], profile: Any | None) -> str:
    context = _profile_context(profile)
    if kind == "tarot":
        cards = source.get("cards", [])
        card_lines = "\n".join(f"- {c.get('position')}: {c.get('name')} — {c.get('meaning')}" for c in cards)
        body = f"Tarot spread: {source.get('spread')}\nCards drawn:\n{card_lines}"
    else:
        insights = source.get("insights", {})
        feature_lines = "\n".join(f"- {k.replace('_', ' ')}: {v}" for k, v in insights.items())
        quality_bits = [f"image analysis confidence {source.get('confidence')}", f"source: {source.get('source', 'heuristic')}"]
        if "edge_density" in source:
            quality_bits.append(f"edge density {source['edge_density']}")
        if "detected_lines" in source:
            quality_bits.append(f"lines the model detected: {', '.join(source.get('detected_lines') or []) or 'none'}")
        body = f"Palm reading — {', '.join(quality_bits)}.\nDetected features:\n{feature_lines}"
    if context:
        body += f"\n\nThe user's stated interests/goals/preferences: {context}"
    return body


def _validate_narrative_shape(payload: dict[str, Any]) -> None:
    """Raise AIUnavailable (triggering the deterministic fallback) if the
    model returned anything we can't safely serve as-is."""
    try:
        assert isinstance(payload.get("summary"), str) and payload["summary"].strip()
        assert isinstance(payload.get("themes"), list) and len(payload["themes"]) >= 1
        assert all(isinstance(t, str) for t in payload["themes"])

        personality = payload.get("personality")
        assert isinstance(personality, dict)
        for field in ("strength", "growth_edge", "reflection_prompt"):
            assert isinstance(personality.get(field), str) and personality[field].strip()

        guidance = payload.get("guidance")
        assert isinstance(guidance, list) and len(guidance) >= REQUIRED_GUIDANCE_ITEMS
        for item in guidance:
            assert isinstance(item, dict) and item.get("category") and item.get("action")

        trends = payload.get("life_trends")
        assert isinstance(trends, list) and len(trends) >= REQUIRED_TREND_ITEMS
        for item in trends:
            assert isinstance(item, dict) and item.get("period") and item.get("theme") and item.get("guidance")
    except (AssertionError, AttributeError, TypeError) as exc:
        raise AIUnavailable(f"Model response failed shape validation: {exc}") from exc


# --------------------------------------------------------------------------
# Deterministic path (unchanged behavior, always available)
# --------------------------------------------------------------------------

def _build_deterministic_interpretation(kind: str, source: dict[str, Any], profile: Any | None) -> dict[str, Any]:
    context = _profile_context(profile)
    themes = _themes(kind, source)
    focus = _focus_for(themes)
    recommendations = _recommendations(themes, context)

    return {
        "summary": f"This {kind} reading highlights {', '.join(themes[:2])}. {focus}",
        "themes": themes,
        "personality": _personality(themes),
        "guidance": recommendations,
        "life_trends": _life_trends(themes),
        "profile_context_used": context or None,
    }


def _profile_context(profile: Any | None) -> str:
    if not profile:
        return ""
    values = [getattr(profile, field, None) for field in ("interests", "spiritual_goals", "reading_preferences")]
    return "; ".join(value.strip() for value in values if value and value.strip())


def _themes(kind: str, source: dict[str, Any]) -> list[str]:
    if kind == "tarot":
        cards = source.get("cards", [])
        found = [
            _CARD_KEYWORDS[name]
            for card in cards
            if (name := card.get("name", "").lower()) in _CARD_KEYWORDS
        ]
        return list(dict.fromkeys(found)) or ["reflection", "intentional action"]
    insights = " ".join(source.get("insights", {}).values()).lower()
    themes = []
    if "resilience" in insights:
        themes.append("resilience")
    if "creative" in insights or "intuition" in insights:
        themes.append("creative thinking")
    if "analytical" in insights or "logic" in insights:
        themes.append("thoughtful decisions")
    if "affection" in insights or "feelings" in insights:
        themes.append("connection")
    return themes or ["self-awareness", "steady growth"]


def _focus_for(themes: list[str]) -> str:
    if "change" in themes or "renewal" in themes:
        return "Consider one small, practical step toward the transition you want to make."
    if "connection" in themes:
        return "A candid conversation or a small act of care may be a useful next step."
    return "Use the theme as a journal prompt and keep only what feels useful to you."


def _personality(themes: list[str]) -> dict[str, str]:
    primary = themes[0]
    return {
        "strength": f"You may draw on {primary} when navigating uncertainty.",
        "growth_edge": "Balance reflection with a specific action you can take this week.",
        "reflection_prompt": f"Where would more {primary} serve you right now?",
    }


def _recommendations(themes: list[str], context: str) -> list[dict[str, str]]:
    """Deterministic guidance, spread across the spec's Insight Categories
    (section 5) rather than three fixed, uncategorized buckets."""
    context_note = " based on the preferences in your profile" if context else ""
    primary = themes[0]
    return [
        {"category": "personal_growth", "action": f"Journal for ten minutes about {primary}{context_note}."},
        {"category": "relationships", "action": "Have one honest, low-stakes conversation this week about something you've been holding back."},
        {"category": "career", "action": f"Identify one task at work where more {primary} would make a visible difference, and try it once."},
        {"category": "finance", "action": "Review one recurring expense or savings goal and make a single small, deliberate adjustment."},
        {"category": "health_and_wellness", "action": "Choose one calming practice - a walk, breathwork, or a short screen-free pause - and repeat it three times this week."},
        {"category": "life_opportunities", "action": "Turn one intention into a next action that takes less than fifteen minutes."},
    ]


def _life_trends(themes: list[str]) -> list[dict[str, str]]:
    return [
        {"period": "Now", "theme": themes[0], "guidance": "Notice what is already working before making a large change."},
        {"period": "Next step", "theme": themes[min(1, len(themes) - 1)], "guidance": "Experiment gently and review what you learn."},
        {"period": "Longer term", "theme": "integration", "guidance": "Return to your stated goals and track progress over time."},
    ]


# --------------------------------------------------------------------------
# Scoring — always local/deterministic, per spec section 8's weighted model
# --------------------------------------------------------------------------

def _scores(kind: str, source: dict[str, Any], profile: Any | None) -> dict[str, float]:
    palm_confidence = source.get("confidence", 0.55) if kind == "palm" else 0.55
    tarot_relevance = 0.72 if kind == "tarot" else 0.55
    context = _profile_context(profile)
    personality_alignment = 0.78 if context else 0.55
    user_context_relevance = 0.76 if profile else 0.45
    reading_consistency = 0.75

    overall = round(
        palm_confidence * 0.30
        + tarot_relevance * 0.25
        + personality_alignment * 0.20
        + user_context_relevance * 0.15
        + reading_consistency * 0.10,
        2,
    )

    return {
        "palm_analysis_confidence": palm_confidence,
        "tarot_interpretation_relevance": tarot_relevance,
        "personality_alignment": personality_alignment,
        "user_context_relevance": user_context_relevance,
        "reading_consistency": reading_consistency,
        "overall_insight_score": overall,
    }


def dashboard_summary(readings: list[Any]) -> dict[str, Any]:
    """Summarize persisted readings without making claims about user wellbeing."""
    counts = Counter(row.reading_type.value for row in readings)
    recent = list(reversed(readings[:5]))
    return {
        "total_readings": len(readings),
        "by_type": {"palm": counts.get("palm", 0), "tarot": counts.get("tarot", 0)},
        "recent_activity": [
            {"date": row.created_at.isoformat() if row.created_at else None, "type": row.reading_type.value, "summary": row.summary}
            for row in recent
        ],
        "next_step": "Complete a reading, then use its reflection prompt to set one small goal.",
    }