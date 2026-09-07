import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { TarotCardBack, TarotCardFace } from '../components/TarotCard.jsx'

const SPREADS = {
  single_card: ['Focus'],
  three_card: ['Past', 'Present', 'Future'],
  relationship: ['You', 'Connection', 'Guidance'],
  career: ['Current energy', 'Opportunity', 'Next action'],
  life_path: ['Where you are', 'What to release', 'Where to grow'],
  celtic_cross: ['Present', 'Challenge', 'Foundation', 'Past', 'Possibility', 'Near future', 'Self', 'Environment', 'Hopes', 'Outcome'],
}

const SUIT_SYMBOL = { wands: '🔥', cups: '💧', swords: '⚔️', pentacles: '🪙' }

export default function TarotReading() {
  const { token } = useAuth()
  const [deckSize, setDeckSize] = useState(78) // fallback until /api/tarot/deck responds
  const [spread, setSpread] = useState('three_card')
  const [drawnIndices, setDrawnIndices] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const labels = SPREADS[spread]

  useEffect(() => {
    // Ask the backend for the real deck size instead of hardcoding it on
    // the client — keeps the frontend correct even if the deck changes.
    fetch('/api/tarot/deck')
      .then((res) => res.json())
      .then((data) => { if (data.deck_size) setDeckSize(data.deck_size) })
      .catch(() => {}) // deckSize fallback (78) already covers this
  }, [])

  function drawCards() {
    const indices = new Set()
    while (indices.size < labels.length) indices.add(Math.floor(Math.random() * deckSize))
    setDrawnIndices([...indices]); setResult(null); setError(null)
  }
  async function handleReveal() {
    setLoading(true); setError(null)
    try {
      const res = await fetch('/api/tarot/reading', { method: 'POST', headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ spread, card_positions: drawnIndices }) })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Reading could not be generated.')
      setResult(data)
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  return <div>
    <h2 className="font-display text-4xl mb-2">Tarot Reading</h2>
    <p className="text-parchment/60 mb-6">Choose a spread, draw the cards, then use the result as a prompt for reflection. Drawn from the full 78-card deck — Major Arcana plus all four Minor Arcana suits.</p>
    <label className="block max-w-sm mb-7"><span className="text-xs uppercase tracking-widest text-lavender">Spread</span><select value={spread} onChange={(e) => { setSpread(e.target.value); setDrawnIndices([]); setResult(null) }} className="w-full mt-1 bg-plum border border-lavender/30 rounded-lg px-3 py-3"><option value="single_card">Single Card</option><option value="three_card">Three Card</option><option value="relationship">Relationship</option><option value="career">Career</option><option value="life_path">Life Path</option><option value="celtic_cross">Celtic Cross</option></select></label>
    {drawnIndices.length === 0 ? <button onClick={drawCards} className="btn-primary">Shuffle & Draw</button> : <div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 max-w-4xl mb-6">
        {labels.map((label, i) => {
          const revealedCard = result?.cards?.[i]
          return (
            <div key={label} className="text-center">
              <div className="w-24 h-36 mx-auto mb-2 drop-shadow-lg">
                {revealedCard
                  ? <TarotCardFace name={revealedCard.name} arcana={revealedCard.arcana} suit={revealedCard.suit} />
                  : <TarotCardBack />}
              </div>
              <p className="text-xs uppercase tracking-widest text-lavender">{label}</p>
            </div>
          )
        })}
      </div>
      <div className="flex gap-4"><button onClick={handleReveal} disabled={loading || !!result} className="btn-primary">{loading ? 'Interpreting…' : result ? 'Revealed' : 'Reveal Reading'}</button><button onClick={drawCards} className="btn-secondary">Re-shuffle</button></div>
    </div>}
    {error && <p className="text-red-300 text-sm mt-4">{error}</p>}
    {result && <div className="card mt-8"><h3 className="font-display text-2xl text-gold mb-4">Your Spread</h3><ul className="space-y-4 text-sm">{result.cards.map((card) => <li key={card.position}><span className="text-gold">{card.position} — {SUIT_SYMBOL[card.suit] ? `${SUIT_SYMBOL[card.suit]} ` : ''}{card.name}:</span> {card.meaning}</li>)}</ul>{result.interpretation && <div className="mt-6 pt-5 border-t border-lavender/20"><h4 className="font-display text-xl text-gold mb-2">Reflection & Guidance</h4><p>{result.interpretation.summary}</p><p className="text-parchment/60 mt-2">{result.interpretation.personality?.reflection_prompt}</p><ul className="list-disc pl-5 mt-3 space-y-1 text-sm">{result.interpretation.guidance.map((item) => <li key={item.category}>{item.action}</li>)}</ul><p className="text-xs text-parchment/40 mt-4">{result.interpretation.disclaimer}</p></div>}</div>}
  </div>
}
