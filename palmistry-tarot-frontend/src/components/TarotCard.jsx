// Renders a tarot card as original SVG artwork — an ornamental frame plus
// a simple geometric emblem keyed off suit/arcana — instead of the emoji
// placeholder the MVP shipped with. This is drawn from scratch in code, not
// a scan or reproduction of any published tarot deck's artwork.

const SUIT_COLORS = {
  wands: { accent: '#E08A3E', glow: '#3A2110' },
  cups: { accent: '#5FA8C9', glow: '#0F2530' },
  swords: { accent: '#C4C8D6', glow: '#20232E' },
  pentacles: { accent: '#C9A24B', glow: '#2A2110' },
  major: { accent: '#C9A24B', glow: '#2B1B45' },
}

function SuitEmblem({ suit, arcana }) {
  const key = arcana === 'major' ? 'major' : suit
  const stroke = SUIT_COLORS[key]?.accent || '#C9A24B'

  if (arcana === 'major') {
    // A radiant eye-in-star motif — a generic "greater mystery" emblem,
    // used the same way for every Major Arcana card.
    return (
      <g stroke={stroke} strokeWidth="2" fill="none" strokeLinejoin="round">
        {[...Array(8)].map((_, i) => {
          const angle = (i * Math.PI) / 4
          const x2 = 50 + 34 * Math.cos(angle)
          const y2 = 62 + 34 * Math.sin(angle)
          return <line key={i} x1="50" y1="62" x2={x2} y2={y2} strokeWidth="1.2" opacity="0.55" />
        })}
        <circle cx="50" cy="62" r="16" />
        <ellipse cx="50" cy="62" rx="15.5" ry="8" />
        <circle cx="50" cy="62" r="4.5" fill={stroke} />
      </g>
    )
  }

  if (suit === 'wands') {
    return (
      <g stroke={stroke} strokeWidth="2.4" fill="none" strokeLinecap="round">
        <line x1="50" y1="40" x2="50" y2="84" />
        <path d="M50 40 Q42 32 44 22 Q50 28 50 40" fill={stroke} stroke="none" opacity="0.9" />
        <path d="M50 40 Q58 32 56 22 Q50 28 50 40" fill={stroke} stroke="none" opacity="0.9" />
        <line x1="38" y1="52" x2="62" y2="52" strokeWidth="1.4" opacity="0.6" />
        <line x1="38" y1="70" x2="62" y2="70" strokeWidth="1.4" opacity="0.6" />
      </g>
    )
  }
  if (suit === 'cups') {
    return (
      <g stroke={stroke} strokeWidth="2.4" fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d="M34 40 Q34 62 50 62 Q66 62 66 40 Z" />
        <line x1="50" y1="62" x2="50" y2="76" />
        <line x1="38" y1="82" x2="62" y2="82" />
        <path d="M40 44 Q50 52 60 44" strokeWidth="1.4" opacity="0.6" />
      </g>
    )
  }
  if (suit === 'swords') {
    return (
      <g stroke={stroke} strokeWidth="2.4" fill="none" strokeLinecap="round">
        <line x1="50" y1="24" x2="50" y2="80" />
        <path d="M50 24 L44 34 L56 34 Z" fill={stroke} stroke="none" />
        <line x1="36" y1="58" x2="64" y2="58" />
        <line x1="42" y1="80" x2="58" y2="80" />
      </g>
    )
  }
  // pentacles
  return (
    <g stroke={stroke} strokeWidth="2.2" fill="none" strokeLinejoin="round">
      <circle cx="50" cy="54" r="20" />
      {[0, 1, 2, 3, 4].map((i) => {
        const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5
        const a2 = -Math.PI / 2 + ((i + 2) * 2 * Math.PI) / 5
        const x1 = 50 + 14 * Math.cos(a), y1 = 54 + 14 * Math.sin(a)
        const x2 = 50 + 14 * Math.cos(a2), y2 = 54 + 14 * Math.sin(a2)
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="1.6" />
      })}
    </g>
  )
}

export function TarotCardFace({ name, arcana, suit, small = false }) {
  const accent = SUIT_COLORS[arcana === 'major' ? 'major' : suit]?.accent || '#C9A24B'
  return (
    <svg viewBox="0 0 100 150" className={small ? 'w-16 h-24' : 'w-full h-full'} role="img" aria-label={name}>
      <defs>
        <linearGradient id={`bg-${name}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#241638" />
          <stop offset="100%" stopColor="#160F27" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="96" height="146" rx="6" fill={`url(#bg-${name})`} stroke={accent} strokeWidth="1.5" />
      <rect x="6" y="6" width="88" height="138" rx="4" fill="none" stroke={accent} strokeWidth="0.6" opacity="0.5" />
      <SuitEmblem suit={suit} arcana={arcana} />
      {arcana === 'minor' && (
        <text x="50" y="18" textAnchor="middle" fontSize="8" fill={accent} opacity="0.85" fontFamily="serif" letterSpacing="1">
          {suit?.toUpperCase()}
        </text>
      )}
      <text
        x="50" y="128" textAnchor="middle" fontSize={name.length > 14 ? 6 : 7}
        fill="#F1E9DA" fontFamily="serif" letterSpacing="0.5"
      >
        {name}
      </text>
    </svg>
  )
}

export function TarotCardBack({ small = false }) {
  return (
    <svg viewBox="0 0 100 150" className={small ? 'w-16 h-24' : 'w-full h-full'} role="img" aria-label="Face-down tarot card">
      <defs>
        <linearGradient id="cardback" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#2B1B45" />
          <stop offset="100%" stopColor="#160F27" />
        </linearGradient>
        <pattern id="weave" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="10" stroke="#9B87B5" strokeWidth="0.6" opacity="0.35" />
        </pattern>
      </defs>
      <rect x="2" y="2" width="96" height="146" rx="6" fill="url(#cardback)" stroke="#C9A24B" strokeWidth="1.5" />
      <rect x="9" y="9" width="82" height="132" rx="3" fill="url(#weave)" stroke="#C9A24B" strokeWidth="1" opacity="0.9" />
      <circle cx="50" cy="75" r="18" fill="none" stroke="#C9A24B" strokeWidth="1.2" opacity="0.8" />
      <circle cx="50" cy="75" r="4" fill="#C9A24B" opacity="0.9" />
    </svg>
  )
}
