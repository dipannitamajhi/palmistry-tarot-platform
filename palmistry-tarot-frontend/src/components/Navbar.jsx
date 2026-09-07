import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import NotificationBell from './NotificationBell.jsx'

// NavLink is like <a>, but it knows which page is currently active
// so we can highlight it in gold.
export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const linkClass = ({ isActive }) =>
    `transition-colors duration-200 ${isActive ? 'text-gold' : 'text-parchment/70 hover:text-parchment'}`

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="border-b border-lavender/15">
      <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between">
        <NavLink to="/" className="font-display text-2xl tracking-wide text-gold">
          Arcana
        </NavLink>
        <nav className="flex items-center gap-8 font-body text-sm uppercase tracking-widest">
          <NavLink to="/palm" className={linkClass}>Palm Reading</NavLink>
          <NavLink to="/tarot" className={linkClass}>Tarot Reading</NavLink>
          {user ? (
            <div className="flex items-center gap-4">
              <NavLink to="/history" className={linkClass}>History</NavLink>
              <NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
              {['administrator', 'tarot_reader', 'spiritual_consultant'].includes(user.role) && (
                <NavLink to="/admin/analytics" className={linkClass}>Analytics</NavLink>
              )}
              <NavLink to="/profile" className={linkClass}>Profile</NavLink>
              <span className="text-lavender normal-case tracking-normal text-xs">
                Hi, {user.name}
              </span>
              <NotificationBell />
              <button onClick={handleLogout} className="text-parchment/70 hover:text-gold">
                Log out
              </button>
            </div>
          ) : (
            <NavLink to="/login" className={linkClass}>Log In</NavLink>
          )}
        </nav>
      </div>
    </header>
  )
}
