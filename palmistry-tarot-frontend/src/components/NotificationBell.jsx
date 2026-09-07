import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'

const TYPE_LABEL = {
  daily_guidance: 'Daily guidance',
  reading_reminder: 'Reminder',
  insight_update: 'Insight update',
  spiritual_growth_alert: 'Growth alert',
  platform_announcement: 'Announcement',
}

export default function NotificationBell() {
  const { token } = useAuth()
  const [open, setOpen] = useState(false)
  const [items, setItems] = useState([])
  const boxRef = useRef(null)

  async function load() {
    if (!token) return
    try {
      const res = await fetch('/api/notifications/me', { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setItems(await res.json())
    } catch { /* silent — the feed just stays empty until next poll */ }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 60000) // refresh every minute
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  useEffect(() => {
    function onClickOutside(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  async function markRead(id) {
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)))
    try {
      await fetch(`/api/notifications/${id}/read`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } })
    } catch { /* best-effort */ }
  }

  if (!token) return null
  const unreadCount = items.filter((n) => !n.is_read).length

  return (
    <div className="relative" ref={boxRef}>
      <button onClick={() => setOpen((o) => !o)} className="relative text-parchment/70 hover:text-gold" aria-label="Notifications">
        <span className="text-lg">🔔</span>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-2 bg-gold text-midnight text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 mt-3 w-80 max-h-96 overflow-y-auto bg-plum border border-lavender/30 rounded-lg shadow-xl z-50 normal-case tracking-normal">
          <div className="px-4 py-3 border-b border-lavender/20 text-xs uppercase tracking-widest text-lavender">Notifications</div>
          {items.length === 0 && <p className="px-4 py-6 text-sm text-parchment/50 text-center">Nothing new right now.</p>}
          {items.map((n) => (
            <button
              key={n.id}
              onClick={() => !n.is_read && !n.is_announcement && markRead(n.id)}
              className={`block w-full text-left px-4 py-3 border-b border-lavender/10 last:border-0 ${n.is_read ? 'opacity-60' : ''}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] uppercase tracking-widest text-gold">{TYPE_LABEL[n.type] || n.type}</span>
                {!n.is_read && !n.is_announcement && <span className="w-1.5 h-1.5 rounded-full bg-gold" />}
              </div>
              <p className="text-sm text-parchment font-medium">{n.title}</p>
              <p className="text-xs text-parchment/60 mt-0.5">{n.message}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
