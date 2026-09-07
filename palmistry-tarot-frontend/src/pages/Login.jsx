import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault() // stops the browser's default full-page-reload form submit
    setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Login failed.')
      }

      login(data.access_token, data.user)
      navigate('/') // send them to the home page once logged in
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto">
      <h2 className="font-display text-4xl mb-8 text-center">Welcome Back</h2>
      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>
        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Password</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>
        {error && <p className="text-red-300 text-sm">{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? 'Signing in…' : 'Sign In'}
        </button>
      </form>
      <p className="text-center text-sm text-parchment/60 mt-4">
        No account? <Link to="/register" className="text-gold hover:underline">Register</Link>
      </p>
    </div>
  )
}
