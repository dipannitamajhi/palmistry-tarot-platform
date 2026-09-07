import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

export default function History() {
  const { token } = useAuth()
  const [readings, setReadings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  async function downloadReport(format) {
    try {
      const res = await fetch(`/api/reports/me.${format}`, { headers: { Authorization: `Bearer ${token}` } })
      if (!res.ok) throw new Error('Could not export readings.')
      const url = URL.createObjectURL(await res.blob())
      const link = document.createElement('a')
      link.href = url
      link.download = `arcana-readings.${format}`
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) { setError(err.message) }
  }
  useEffect(() => {
    fetch('/api/users/me/readings', { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) throw new Error('Could not load your reading history.')
        return res.json()
      })
      .then(setReadings)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [token])

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="font-display text-4xl mb-2">Reading History</h2>
      <p className="text-parchment/60 mb-8">Every palm and tarot reading you've done while signed in.</p>
      <div className="flex gap-3 mb-5 text-sm flex-wrap">
        <button className="btn-secondary py-2" onClick={() => downloadReport('json')}>Download JSON</button>
        <button className="btn-secondary py-2" onClick={() => downloadReport('csv')}>Download CSV</button>
        <button className="btn-secondary py-2" onClick={() => downloadReport('pdf')}>Download PDF</button>
        <button className="btn-secondary py-2" onClick={() => downloadReport('xlsx')}>Download Excel</button>
      </div>

      {loading && <p className="text-parchment/50">Loading…</p>}
      {error && <p className="text-red-300">{error}</p>}

      {!loading && !error && readings.length === 0 && (
        <p className="text-parchment/50 text-sm">
          No readings yet — try a Palm or Tarot reading while signed in.
        </p>
      )}

      <div className="space-y-4">
        {readings.map((reading) => (
          <div key={reading.id} className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-widest text-gold">
                {reading.reading_type}
              </span>
              <span className="text-xs text-parchment/50">
                {new Date(reading.created_at).toLocaleString()}
              </span>
            </div>
            <p className="text-sm">{reading.summary}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
