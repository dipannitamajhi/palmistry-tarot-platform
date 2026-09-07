import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

// Wrap any page's element with this to require login:
//   <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
// If there's no logged-in user once loading finishes, we redirect instead
// of rendering the protected page at all.
export default function RequireAuth({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <p className="text-center text-parchment/50 py-16">Loading…</p>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}
