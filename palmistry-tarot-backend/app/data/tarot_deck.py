# The full, standard 78-card tarot deck: 22 Major Arcana + 56 Minor Arcana.
#
# This is the single source of truth routers/services should import from —
# `app/routers/tarot.py` draws cards from FULL_DECK, and
# `app/services/insights.py` uses each card's `keyword` to build reading
# themes, regardless of whether the card is Major or Minor Arcana.

from app.data.major_arcana import MAJOR_ARCANA
from app.data.minor_arcana import MINOR_ARCANA, SUIT_INFO

# Normalize both lists to the same shape: every card has name, meaning,
# arcana ("major"/"minor"), suit (None for Major Arcana), and keyword.
FULL_DECK = [
    {**card, "arcana": "major", "suit": None}
    for card in MAJOR_ARCANA
] + [
    {**card, "arcana": "minor"}
    for card in MINOR_ARCANA
]

DECK_SIZE = len(FULL_DECK)  # 78

__all__ = ["FULL_DECK", "DECK_SIZE", "SUIT_INFO"]
