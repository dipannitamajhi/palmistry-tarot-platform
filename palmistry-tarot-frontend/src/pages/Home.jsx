import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="text-center py-16">
      <p className="uppercase tracking-[0.3em] text-lavender text-xs mb-4">
        Two Ancient Practices, One Reading
      </p>
      <h1 className="font-display text-6xl leading-tight mb-6">
        What do your <span className="text-gold">hands</span> and the{' '}
        <span className="text-gold">cards</span> say?
      </h1>
      <p className="text-parchment/70 max-w-xl mx-auto mb-10">
        Upload a photo of your palm or draw from the deck — you'll get a
        personalized, AI-generated reading in seconds.
      </p>
      <div className="flex justify-center gap-4">
        <Link to="/palm" className="btn-primary">Start Palm Reading</Link>
        <Link to="/tarot" className="btn-secondary">Draw Tarot Cards</Link>
      </div>
    </div>
  )
}
