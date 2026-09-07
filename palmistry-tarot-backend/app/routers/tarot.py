import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional
from sqlalchemy.orm import Session

from app.data.tarot_deck import FULL_DECK
from app.database import get_db
from app.models.user import User
from app.models.reading import Reading, ReadingType
from app.auth.dependencies import get_optional_current_user
from app.services.insights import build_interpretation
from app.services.notifications import notify_reading_ready

router = APIRouter(prefix="/api/tarot", tags=["tarot"])

# Pydantic models define the *shape* of data coming in and going out.
# FastAPI uses them to validate requests automatically — if the frontend
# sends something malformed, the client gets a clear 422 error instead of
# your code crashing halfway through.

class TarotRequest(BaseModel):
    spread: str
    card_positions: List[int]  # indices into FULL_DECK, chosen by the frontend's shuffle


class TarotCard(BaseModel):
    position: str
    name: str
    meaning: str
    arcana: str            # "major" or "minor"
    suit: Optional[str]    # e.g. "cups"; None for Major Arcana


class TarotResponse(BaseModel):
    spread: str
    cards: List[TarotCard]
    interpretation: dict[str, Any] | None = None


# Which position labels apply to which spread. This mirrors the doc's
# "Supported Tarot Spreads" list.
SPREAD_LABELS = {
    "single_card": ["Focus"],
    "three_card": ["Past", "Present", "Future"],
    "relationship": ["You", "Connection", "Guidance"],
    "career": ["Current energy", "Opportunity", "Next action"],
    "life_path": ["Where you are", "What to release", "Where to grow"],
    "celtic_cross": ["Present", "Challenge", "Foundation", "Past", "Possibility", "Near future", "Self", "Environment", "Hopes", "Outcome"],
}


@router.get("/deck")
def get_deck_info():
    """Deck metadata for the frontend's shuffle (deck size, suits) so the
    client never has to hardcode the number of cards."""
    from app.data.tarot_deck import DECK_SIZE, SUIT_INFO
    return {"deck_size": DECK_SIZE, "major_count": 22, "minor_count": 56, "suits": SUIT_INFO}


@router.post("/reading", response_model=TarotResponse)
def get_tarot_reading(
    request: TarotRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    labels = SPREAD_LABELS.get(request.spread)
    if labels is None:
        raise HTTPException(status_code=422, detail="Unsupported spread.")
    if len(request.card_positions) != len(labels):
        raise HTTPException(status_code=422, detail=f"{request.spread} requires {len(labels)} cards.")
    if len(set(request.card_positions)) != len(request.card_positions):
        raise HTTPException(status_code=422, detail="Each card must be unique within a spread.")

    cards = []
    for label, index in zip(labels, request.card_positions):
        # Guard against an out-of-range index (e.g. a bug on the frontend)
        # by wrapping around the deck instead of crashing.
        card_data = FULL_DECK[index % len(FULL_DECK)]
        cards.append(TarotCard(
            position=label,
            name=card_data["name"],
            meaning=card_data["meaning"],
            arcana=card_data["arcana"],
            suit=card_data["suit"],
        ))

    response = TarotResponse(spread=request.spread, cards=cards)
    response_data = response.model_dump()
    response_data["interpretation"] = build_interpretation("tarot", response_data, current_user)

    if current_user:
        card_names = ", ".join(c.name for c in cards)
        reading = Reading(
            user_id=current_user.id,
            reading_type=ReadingType.TAROT,
            summary=f"{request.spread.replace('_', ' ').title()}: {card_names}",
            details=json.dumps(response_data),
        )
        db.add(reading)
        db.commit()
        notify_reading_ready(db, current_user, "tarot")

    return response_data
