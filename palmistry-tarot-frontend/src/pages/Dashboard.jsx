import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

export default function Dashboard() {
  const { token } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/dashboard/me', { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.ok ? res.json() : Promise.reject(new Error('Could not load dashboard.')))
      .then(setData).catch((err) => setError(err.message))
  }, [token])

  if (error) return <p className="text-red-300">{error}</p>
  if (!data) return <p className="text-parchment/50">Loading your dashboard…</p>
  return <div className="max-w-3xl mx-auto">
    <h2 className="font-display text-4xl mb-2">Your Insight Dashboard</h2>
    <p className="text-parchment/60 mb-8">A private overview of your saved reflection sessions.</p>
    <div className="grid sm:grid-cols-3 gap-4 mb-8">
      <Metric label="Total readings" value={data.total_readings} />
      <Metric label="Palm readings" value={data.by_type.palm} />
      <Metric label="Tarot readings" value={data.by_type.tarot} />
    </div>
    <div className="card mb-6"><h3 className="font-display text-2xl text-gold mb-2">Suggested next step</h3><p>{data.next_step}</p></div>
    <div className="card"><h3 className="font-display text-2xl text-gold mb-4">Recent activity</h3>
      {data.recent_activity.length ? <ul className="space-y-3">{data.recent_activity.map((item, index) => <li key={`${item.date}-${index}`} className="border-b border-lavender/15 pb-3"><span className="uppercase text-xs tracking-widest text-lavender">{item.type}</span><p className="text-sm">{item.summary}</p></li>)}</ul> : <p className="text-parchment/50">Your completed readings will appear here.</p>}
    </div>
  </div>
}

function Metric({ label, value }) { return <div className="card text-center"><p className="font-display text-4xl text-gold">{value}</p><p className="text-xs uppercase tracking-widest text-parchment/60 mt-2">{label}</p></div> }
