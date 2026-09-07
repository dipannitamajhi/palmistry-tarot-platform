# Minor Arcana reference data (56 cards).
#
# The Minor Arcana reflects day-to-day situations rather than the big
# life themes of the Major Arcana (see major_arcana.py). It is split into
# four suits, each carrying its own emotional "flavor":
#
#   Wands     - energy, passion, action, ambition (element: Fire)
#   Cups      - emotions, relationships, intuition (element: Water)
#   Swords    - thoughts, communication, conflict, truth (element: Air)
#   Pentacles - work, money, the physical world, stability (element: Earth)
#
# Each suit runs Ace -> 10, then four court cards (Page, Knight, Queen, King).
# 4 suits x 14 cards = 56 cards, which combined with the 22 Major Arcana
# cards makes the full, standard 78-card tarot deck.
#
# `keyword` is a single short theme word used by app/services/insights.py
# to fold a drawn card into the reading's overall themes, the same way
# individual Major Arcana cards are already mapped to themes there.

SUITS = ["wands", "cups", "swords", "pentacles"]

SUIT_INFO = {
    "wands": {"element": "Fire", "domain": "energy, passion, and action"},
    "cups": {"element": "Water", "domain": "emotions, love, and relationships"},
    "swords": {"element": "Air", "domain": "thoughts, communication, and conflict"},
    "pentacles": {"element": "Earth", "domain": "money, work, and the physical world"},
}

_RANKS = [
    ("Ace", "wands", "A spark of new ambition or motivation.", "initiative"),
    ("Two", "wands", "Planning ahead, weighing a bigger decision.", "planning"),
    ("Three", "wands", "Early progress; watching your effort start to expand.", "expansion"),
    ("Four", "wands", "A milestone worth celebrating with others.", "celebration"),
    ("Five", "wands", "Friendly competition or minor friction to work through.", "friction"),
    ("Six", "wands", "Recognition for effort already put in.", "recognition"),
    ("Seven", "wands", "Holding your ground under pressure.", "resilience"),
    ("Eight", "wands", "Fast-moving momentum; things picking up speed.", "momentum"),
    ("Nine", "wands", "Persistence after a long stretch of effort.", "persistence"),
    ("Ten", "wands", "Carrying a heavy load, possibly more than needed.", "overload"),
    ("Page", "wands", "Curiosity and eagerness to explore something new.", "curiosity"),
    ("Knight", "wands", "Bold, fast action, sometimes before fully thinking it through.", "boldness"),
    ("Queen", "wands", "Confident warmth and self-assured energy.", "confidence"),
    ("King", "wands", "Steady leadership and a clear sense of direction.", "leadership"),

    ("Ace", "cups", "An emotional new beginning or open heart.", "openness"),
    ("Two", "cups", "A mutual connection or partnership taking shape.", "connection"),
    ("Three", "cups", "Friendship, community, and shared celebration.", "community"),
    ("Four", "cups", "Mild discontent; something offered isn't landing yet.", "reevaluation"),
    ("Five", "cups", "Grief or disappointment, with what's left still standing nearby.", "grief"),
    ("Six", "cups", "Nostalgia and comfort found in the familiar.", "nostalgia"),
    ("Seven", "cups", "Many appealing options, worth sorting from illusion.", "choices"),
    ("Eight", "cups", "Walking away from something that no longer fits.", "release"),
    ("Nine", "cups", "Contentment; a wish quietly fulfilled.", "contentment"),
    ("Ten", "cups", "Lasting happiness shared with the people close to you.", "fulfillment"),
    ("Page", "cups", "A tender, imaginative emotional message or idea.", "sensitivity"),
    ("Knight", "cups", "Following the heart, sometimes idealistically.", "romance"),
    ("Queen", "cups", "Deep empathy and emotional intuition.", "empathy"),
    ("King", "cups", "Emotional maturity; steady even in rough waters.", "composure"),

    ("Ace", "swords", "A moment of mental clarity or a breakthrough idea.", "clarity"),
    ("Two", "swords", "A standoff or a decision you've been avoiding.", "indecision"),
    ("Three", "swords", "Heartbreak or a painful truth coming to light.", "heartbreak"),
    ("Four", "swords", "Rest and recovery before the next push.", "rest"),
    ("Five", "swords", "A hollow win, or conflict that costs more than it's worth.", "conflict"),
    ("Six", "swords", "Moving on toward calmer waters.", "transition"),
    ("Seven", "swords", "Working around a problem quietly, maybe evasively.", "strategy"),
    ("Eight", "swords", "Feeling boxed in by your own thoughts.", "self-doubt"),
    ("Nine", "swords", "Anxiety and rumination, often worse at night.", "anxiety"),
    ("Ten", "swords", "A painful ending that has finally run its course.", "closure"),
    ("Page", "swords", "Watchful curiosity; gathering information before acting.", "vigilance"),
    ("Knight", "swords", "Fast, direct, sometimes blunt pursuit of a goal.", "directness"),
    ("Queen", "swords", "Clear-eyed honesty and independent thinking.", "honesty"),
    ("King", "swords", "Sound judgment grounded in logic and principle.", "judgment"),

    ("Ace", "pentacles", "A tangible new opportunity, financial or practical.", "opportunity"),
    ("Two", "pentacles", "Juggling priorities and adapting as things shift.", "balance"),
    ("Three", "pentacles", "Collaborative work building toward something solid.", "teamwork"),
    ("Four", "pentacles", "Holding tightly to security or resources.", "security"),
    ("Five", "pentacles", "A hard patch, financially or otherwise, that won't last forever.", "hardship"),
    ("Six", "pentacles", "Generosity, giving or receiving support fairly.", "generosity"),
    ("Seven", "pentacles", "Patiently assessing progress on a long-term effort.", "patience"),
    ("Eight", "pentacles", "Focused, detail-oriented craftsmanship.", "diligence"),
    ("Nine", "pentacles", "Self-sufficiency and enjoying what you've built.", "independence"),
    ("Ten", "pentacles", "Long-term stability, often involving family or legacy.", "legacy"),
    ("Page", "pentacles", "A practical new study or opportunity worth pursuing.", "opportunity"),
    ("Knight", "pentacles", "Slow, steady, reliable effort toward a goal.", "steadiness"),
    ("Queen", "pentacles", "Nurturing practicality; caring for people and resources alike.", "nurturing"),
    ("King", "pentacles", "Real-world mastery and dependable abundance.", "abundance"),
]

MINOR_ARCANA = [
    {
        "name": f"{rank} of {suit.capitalize()}",
        "suit": suit,
        "meaning": meaning,
        "keyword": keyword,
    }
    for rank, suit, meaning, keyword in _RANKS
]
