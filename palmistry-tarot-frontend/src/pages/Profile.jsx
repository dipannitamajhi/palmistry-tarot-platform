import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

// This mirrors the doc's "User Information" list: age group, interests,
// spiritual goals, and reading preferences (section 4.2).
export default function Profile() {
  const { user, token, login } = useAuth()
  const [form, setForm] = useState({
    age_group: user.age_group || '',
    interests: user.interests || '',
    spiritual_goals: user.spiritual_goals || '',
    reading_preferences: user.reading_preferences || '',
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)

  function updateField(field) {
    return (e) => {
      setForm({ ...form, [field]: e.target.value })
      setSaved(false)
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    setError(null)

    try {
      const res = await fetch('/api/users/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Could not save profile.')

      // Update the shared auth state so the rest of the app (e.g. Navbar)
      // sees the fresh data immediately, without a page reload.
      login(token, data)
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="font-display text-4xl mb-2">Your Profile</h2>
      <p className="text-parchment/60 mb-8">
        {user.name} · {user.email} · <span className="text-gold capitalize">{user.role.replace('_', ' ')}</span>
      </p>

      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Age Group</label>
          <select
            value={form.age_group}
            onChange={updateField('age_group')}
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          >
            <option value="">Prefer not to say</option>
            <option value="18-24">18–24</option>
            <option value="25-34">25–34</option>
            <option value="35-44">35–44</option>
            <option value="45+">45+</option>
          </select>
        </div>

        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Interests</label>
          <input
            value={form.interests}
            onChange={updateField('interests')}
            placeholder="astrology, meditation, dream work…"
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Spiritual Goals</label>
          <textarea
            value={form.spiritual_goals}
            onChange={updateField('spiritual_goals')}
            rows={3}
            placeholder="What are you hoping to work through or understand?"
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Reading Preferences</label>
          <input
            value={form.reading_preferences}
            onChange={updateField('reading_preferences')}
            placeholder="tarot, palm"
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>

        {error && <p className="text-red-300 text-sm">{error}</p>}
        {saved && <p className="text-gold text-sm">Saved.</p>}

        <button type="submit" disabled={saving} className="btn-primary w-full">
          {saving ? 'Saving…' : 'Save Profile'}
        </button>
      </form>
    </div>
  )
}
