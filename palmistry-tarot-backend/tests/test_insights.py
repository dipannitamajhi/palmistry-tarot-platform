import os
from types import SimpleNamespace

import pytest

from app.services import insights
from app.services.ai_client import AIUnavailable


def test_tarot_interpretation_is_reflective_and_scored():
    report = insights.build_interpretation(
        "tarot",
        {"spread": "three_card", "cards": [{"position": "Past", "name": "The Star", "meaning": "hope"}, {"position": "Present", "name": "The Hermit", "meaning": "reflection"}]},
        SimpleNamespace(interests="meditation", spiritual_goals="build a habit", reading_preferences="tarot"),
    )
    assert "entertainment" in report["disclaimer"].lower()
    assert "renewal" in report["themes"]
    assert 0 <= report["scores"]["overall_insight_score"] <= 1
    assert len(report["guidance"]) == 3
    assert report["source"] == "deterministic"  # no OPENAI_API_KEY set in the test env


def test_tarot_theme_extraction_covers_minor_arcana():
    # Minor Arcana cards (suit cards) didn't produce themes before the
    # deck was expanded from 22 to 78 cards — this guards against that.
    report = insights.build_interpretation(
        "tarot",
        {"spread": "single_card", "cards": [{"position": "Focus", "name": "Three of Cups", "meaning": "community"}]},
        None,
    )
    assert "community" in report["themes"]


def test_palm_interpretation_handles_missing_profile():
    report = insights.build_interpretation("palm", {"confidence": 0.7, "insights": {}}, None)
    assert report["profile_context_used"] is None
    assert report["scores"]["palm_analysis_confidence"] == 0.7


def test_ai_path_used_when_configured_and_response_is_valid(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(insights, "is_configured", lambda: True)

    def fake_chat_json(system_prompt, user_prompt):
        return {
            "summary": "A reflective summary about your reading.",
            "themes": ["renewal", "clarity"],
            "personality": {
                "strength": "You adapt well to change.",
                "growth_edge": "Try naming your needs earlier.",
                "reflection_prompt": "What would renewal look like this month?",
            },
            "guidance": [
                {"category": "personal growth", "action": "Write down one thing you want to release."},
                {"category": "mindfulness", "action": "Take a five-minute walk without your phone."},
                {"category": "goals", "action": "Pick one small task to finish today."},
            ],
            "life_trends": [
                {"period": "Now", "theme": "renewal", "guidance": "Notice small wins."},
                {"period": "Next step", "theme": "clarity", "guidance": "Ask one clarifying question this week."},
                {"period": "Longer term", "theme": "integration", "guidance": "Revisit your goals monthly."},
            ],
        }

    monkeypatch.setattr(insights, "chat_json", fake_chat_json)

    report = insights.build_interpretation(
        "tarot",
        {"spread": "three_card", "cards": [{"position": "Past", "name": "The Star", "meaning": "hope"}]},
        None,
    )
    assert report["source"] == "ai"
    assert report["summary"] == "A reflective summary about your reading."
    assert len(report["guidance"]) == 3


def test_ai_path_falls_back_when_model_response_is_malformed(monkeypatch):
    monkeypatch.setattr(insights, "is_configured", lambda: True)
    monkeypatch.setattr(insights, "chat_json", lambda *a, **k: {"summary": "missing everything else"})

    report = insights.build_interpretation("tarot", {"spread": "single_card", "cards": [{"position": "Focus", "name": "The Sun", "meaning": "clarity"}]}, None)
    assert report["source"] == "deterministic"


def test_ai_path_falls_back_when_client_raises(monkeypatch):
    monkeypatch.setattr(insights, "is_configured", lambda: True)

    def raise_unavailable(*args, **kwargs):
        raise AIUnavailable("simulated outage")

    monkeypatch.setattr(insights, "chat_json", raise_unavailable)

    report = insights.build_interpretation("palm", {"confidence": 0.6, "insights": {"life_line": "steady"}}, None)
    assert report["source"] == "deterministic"
