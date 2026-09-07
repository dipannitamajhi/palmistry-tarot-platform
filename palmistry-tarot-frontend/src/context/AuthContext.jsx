import { createContext, useContext, useState, useEffect } from 'react'

// React Context lets any component in the tree read "who's logged in?"
// without passing that data down manually through every parent component
// (called "prop drilling"). We wrap <App /> in this provider once.
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // localStorage persists across browser refreshes/tabs — a normal,
  // supported choice for a real deployed app like this one (this only
  // becomes unsafe inside Claude's in-chat preview artifacts, which is a
  // different, sandboxed environment — not the case here).
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Whenever we have a token but no user yet (e.g. page was just refreshed),
  // ask the backend who this token belongs to.
  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }
    fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then(setUser)
      .catch(() => {
        setToken(null)
        localStorage.removeItem('token')
      })
      .finally(() => setLoading(false))
  }, [token])

  function login(newToken, newUser) {
    localStorage.setItem('token', newToken)
    setToken(newToken)
    setUser(newUser)
  }

  function logout() {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// A small custom hook so components just call useAuth() instead of
// importing useContext + AuthContext everywhere.
export function useAuth() {
  return useContext(AuthContext)
}
