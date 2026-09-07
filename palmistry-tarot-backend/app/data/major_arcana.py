# Major Arcana reference data (22 cards).
# In a real product this might live in a database table so tarot readers
# (see the "Tarot Reader" role in the spec) could edit meanings without a
# code deploy. For now, a plain Python list is simpler and just as correct.
#
# `keyword` is the single short theme word app/services/insights.py folds
# into a reading's overall themes — see MINOR_ARCANA for the same pattern
# applied to the suit cards.

MAJOR_ARCANA = [
    {"name": "The Fool", "meaning": "New beginnings, spontaneity, a leap of faith.", "keyword": "new beginnings"},
    {"name": "The Magician", "meaning": "Resourcefulness, willpower, turning ideas into action.", "keyword": "initiative"},
    {"name": "The High Priestess", "meaning": "Intuition, quiet knowledge, trusting what you sense.", "keyword": "intuition"},
    {"name": "The Empress", "meaning": "Abundance, nurturing, creative growth.", "keyword": "creative growth"},
    {"name": "The Emperor", "meaning": "Structure, authority, stability through discipline.", "keyword": "structure"},
    {"name": "The Hierophant", "meaning": "Tradition, mentorship, shared belief systems.", "keyword": "tradition"},
    {"name": "The Lovers", "meaning": "Connection, alignment of values, meaningful choice.", "keyword": "connection"},
    {"name": "The Chariot", "meaning": "Determination, forward motion, disciplined ambition.", "keyword": "momentum"},
    {"name": "Strength", "meaning": "Quiet courage, patience, mastering instinct with compassion.", "keyword": "courage"},
    {"name": "The Hermit", "meaning": "Reflection, solitude, seeking inner guidance.", "keyword": "reflection"},
    {"name": "Wheel of Fortune", "meaning": "Cycles, change, timing beyond your control.", "keyword": "change"},
    {"name": "Justice", "meaning": "Fairness, cause and effect, honest accounting.", "keyword": "balance"},
    {"name": "The Hanged Man", "meaning": "A pause, new perspective, letting go of control.", "keyword": "new perspective"},
    {"name": "Death", "meaning": "Endings that clear space for transformation.", "keyword": "transformation"},
    {"name": "Temperance", "meaning": "Balance, patience, blending opposites into harmony.", "keyword": "balance"},
    {"name": "The Devil", "meaning": "Attachment, old patterns, facing what binds you.", "keyword": "old patterns"},
    {"name": "The Tower", "meaning": "Sudden upheaval that reveals what was unstable.", "keyword": "change"},
    {"name": "The Star", "meaning": "Hope, renewal, quiet faith after hardship.", "keyword": "renewal"},
    {"name": "The Moon", "meaning": "Uncertainty, the subconscious, things not yet clear.", "keyword": "intuition"},
    {"name": "The Sun", "meaning": "Clarity, vitality, straightforward joy.", "keyword": "clarity"},
    {"name": "Judgement", "meaning": "Reckoning, awakening, a call to step up.", "keyword": "awakening"},
    {"name": "The World", "meaning": "Completion, wholeness, a cycle closing well.", "keyword": "completion"},
]
