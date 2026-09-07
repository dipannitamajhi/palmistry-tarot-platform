import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  function updateField(field) {
    return (e) => setForm({ ...form, [field]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const registerRes = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const registerData = await registerRes.json()
      if (!registerRes.ok) throw new Error(registerData.detail || 'Registration failed.')

      // Registering doesn't log you in by itself (the backend just creates
      // the account) — so we immediately log in right after, to save the
      // user a second form.
      const loginRes = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email, password: form.password }),
      })
      const loginData = await loginRes.json()
      if (!loginRes.ok) throw new Error(loginData.detail || 'Login after registration failed.')

      login(loginData.access_token, loginData.user)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto">
      <h2 className="font-display text-4xl mb-8 text-center">Create Account</h2>
      <form onSubmit={handleSubmit} className="card space-y-4">
        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Name</label>
          <input
            required
            value={form.name}
            onChange={updateField('name')}
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>
        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Email</label>
          <input
            type="email"
            required
            value={form.email}
            onChange={updateField('email')}
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>
        <div>
          <label className="text-xs uppercase tracking-widest text-lavender">Password</label>
          <input
            type="password"
            required
            minLength={6}
            value={form.password}
            onChange={updateField('password')}
            className="w-full mt-1 bg-midnight border border-lavender/30 rounded-lg px-3 py-2 focus:outline-none focus:border-gold"
          />
        </div>
        {error && <p className="text-red-300 text-sm">{error}</p>}
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? 'Creating account…' : 'Register'}
        </button>
      </form>
      <p className="text-center text-sm text-parchment/60 mt-4">
        Already have an account? <Link to="/login" className="text-gold hover:underline">Sign in</Link>
      </p>
    </div>
  )
}
