import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

const STAFF_ROLES = ['administrator', 'tarot_reader', 'spiritual_consultant']
const ASSIGNABLE_ROLES = ['user', 'tarot_reader', 'spiritual_consultant', 'administrator']

export default function AdminAnalytics() {
  const { token, user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [announceTitle, setAnnounceTitle] = useState('')
  const [announceMessage, setAnnounceMessage] = useState('')
  const [announceStatus, setAnnounceStatus] = useState(null)

  // NEW: state for the "User management" table (this was missing before)
  const [users, setUsers] = useState(null)
  const [userError, setUserError] = useState(null)

  // isAdmin controls whether the user-management table is shown at all —
  // only Administrators are allowed to change roles, not Tarot Readers
  // or Spiritual Consultants.
  const isAdmin = user?.role === 'administrator'

  useEffect(() => {
    if (!user || !STAFF_ROLES.includes(user.role)) return
    fetch('/api/dashboard/platform/analytics', { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error('Could not load analytics.'))))
      .then(setData)
      .catch((err) => setError(err.message))
  }, [token, user])

  // NEW: load the user list for the management table (admins only)
  useEffect(() => {
    if (!isAdmin) return
    fetch('/api/admin/users', { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error('Could not load users.'))))
      .then(setUsers)
      .catch((err) => setUserError(err.message))
  }, [token, isAdmin])

  // NEW: the function that was referenced (changeRole) but never defined
  async function changeRole(userId, role) {
    setUserError(null)
    try {
      const res = await fetch(`/api/admin/users/${userId}/role`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ role }),
      })
      if (!res.ok) throw new Error('Could not update that user\'s role.')
      const updated = await res.json()
      // Update just that one row in the table instead of re-fetching everything
      setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)))
    } catch (err) {
      setUserError(err.message)
    }
  }

  async function postAnnouncement(e) {
    e.preventDefault()
    setAnnounceStatus(null)
    try {
      const res = await fetch('/api/notifications/announcement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ title: announceTitle, message: announceMessage }),
      })
      if (!res.ok) throw new Error('Could not post the announcement.')
      setAnnounceTitle('')
      setAnnounceMessage('')
      setAnnounceStatus('Announcement posted — every user will see it in their notification feed.')
    } catch (err) {
      setAnnounceStatus(err.message)
    }
  }

  if (!user || !STAFF_ROLES.includes(user.role)) {
    return (
      <div className="max-w-2xl mx-auto">
        <h2 className="font-display text-4xl mb-2">Platform Analytics</h2>
        <p className="text-parchment/60">
          This page is available to Tarot Readers, Spiritual Consultants, and Administrators only.
        </p>
      </div>
    )
  }

  if (error) return <p className="text-red-300">{error}</p>
  if (!data) return <p className="text-parchment/50">Loading platform analytics…</p>

  const maxDaily = Math.max(1, ...data.readings_last_30_days.map((d) => d.count))
  const maxTheme = Math.max(1, ...data.top_themes.map((t) => t.count))

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="font-display text-4xl mb-2">Platform Analytics</h2>
      <p className="text-parchment/60 mb-8">
        Reading volume, engagement, and interpretation mix across all users.
      </p>

      <div className="grid sm:grid-cols-3 gap-4 mb-8">
        <Metric label="Total readings" value={data.totals.total_readings} />
        <Metric label="Total users" value={data.totals.total_users} />
        <Metric label="Active readers" value={data.totals.users_with_at_least_one_reading} />
        <Metric label="Palm readings" value={data.readings_by_type.find((t) => t.type === 'palm')?.count ?? 0} />
        <Metric label="Tarot readings" value={data.readings_by_type.find((t) => t.type === 'tarot')?.count ?? 0} />
        <Metric label="Avg. insight score" value={data.average_insight_score ?? '—'} />
      </div>

      <div className="card mb-6">
        <h3 className="font-display text-2xl text-gold mb-1">Readings — last 30 days</h3>
        <p className="text-xs text-parchment/50 mb-4">
          {data.totals.ai_generated_readings} AI-generated · {data.totals.deterministic_readings} deterministic
        </p>
        <div className="flex items-end gap-[3px] h-32">
          {data.readings_last_30_days.map((d) => (
            <div
              key={d.date}
              title={`${d.date}: ${d.count}`}
              className="flex-1 bg-gold/70 hover:bg-gold rounded-t"
              style={{ height: `${(d.count / maxDaily) * 100}%`, minHeight: d.count > 0 ? '3px' : '1px' }}
            />
          ))}
        </div>
        <div className="flex justify-between text-[10px] text-parchment/40 mt-2">
          <span>{data.readings_last_30_days[0]?.date}</span>
          <span>{data.readings_last_30_days[data.readings_last_30_days.length - 1]?.date}</span>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-display text-2xl text-gold mb-4">Top themes</h3>
          {data.top_themes.length ? (
            <ul className="space-y-2">
              {data.top_themes.map((t) => (
                <li key={t.theme}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-parchment/80">{t.theme}</span>
                    <span className="text-parchment/50">{t.count}</span>
                  </div>
                  <div className="h-2 bg-lavender/10 rounded">
                    <div className="h-2 bg-lavender rounded" style={{ width: `${(t.count / maxTheme) * 100}%` }} />
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-parchment/50 text-sm">No themes recorded yet.</p>
          )}
        </div>

        <div className="card">
          <h3 className="font-display text-2xl text-gold mb-4">Users by role</h3>
          <ul className="space-y-3">
            {data.users_by_role.map((r) => (
              <li key={r.role} className="flex justify-between text-sm border-b border-lavender/15 pb-2">
                <span className="uppercase tracking-widest text-xs text-lavender">{r.role.replace('_', ' ')}</span>
                <span>{r.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* User management table — Administrators only, matches spec section 4.10 */}
      {isAdmin && (
        <div className="card mt-6">
          <h3 className="font-display text-2xl text-gold mb-1">User management</h3>
          <p className="text-xs text-parchment/50 mb-4">
            Assign staff roles (Tarot Reader, Spiritual Consultant, Administrator).
          </p>
          {userError && <p className="text-red-300 text-sm mb-3">{userError}</p>}
          {!users ? (
            <p className="text-parchment/50 text-sm">Loading users…</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-widest text-parchment/50 border-b border-lavender/15">
                    <th className="py-2 pr-4">Name</th>
                    <th className="py-2 pr-4">Email</th>
                    <th className="py-2 pr-4">Role</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b border-lavender/10">
                      <td className="py-2 pr-4">{u.name}</td>
                      <td className="py-2 pr-4 text-parchment/60">{u.email}</td>
                      <td className="py-2 pr-4">
                        <select
                          value={u.role}
                          onChange={(e) => changeRole(u.id, e.target.value)}
                          disabled={u.id === user.id}
                          className="bg-plum border border-lavender/30 rounded px-2 py-1 text-xs"
                        >
                          {ASSIGNABLE_ROLES.map((r) => (
                            <option key={r} value={r}>{r.replace('_', ' ')}</option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <div className="card mt-6">
        <h3 className="font-display text-2xl text-gold mb-1">Post a platform announcement</h3>
        <p className="text-xs text-parchment/50 mb-4">
          Delivered to every user's notification feed (spec section 11 — Platform announcements).
        </p>
        <form onSubmit={postAnnouncement} className="space-y-3 max-w-lg">
          <input
            value={announceTitle}
            onChange={(e) => setAnnounceTitle(e.target.value)}
            placeholder="Title"
            required
            className="w-full bg-plum border border-lavender/30 rounded-lg px-3 py-2 text-sm"
          />
          <textarea
            value={announceMessage}
            onChange={(e) => setAnnounceMessage(e.target.value)}
            placeholder="Message"
            required
            rows={3}
            className="w-full bg-plum border border-lavender/30 rounded-lg px-3 py-2 text-sm"
          />
          <button type="submit" className="btn-primary">Post announcement</button>
          {announceStatus && <p className="text-xs text-parchment/60">{announceStatus}</p>}
        </form>
      </div>
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div className="card text-center">
      <p className="font-display text-4xl text-gold">{value}</p>
      <p className="text-xs uppercase tracking-widest text-parchment/60 mt-2">{label}</p>
    </div>
  )
}