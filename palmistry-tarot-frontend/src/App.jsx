import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import RequireAuth from './components/RequireAuth.jsx'
import Navbar from './components/Navbar.jsx'
import Home from './pages/Home.jsx'
import PalmReading from './pages/PalmReading.jsx'
import TarotReading from './pages/TarotReading.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Profile from './pages/Profile.jsx'
import History from './pages/History.jsx'
import Dashboard from './pages/Dashboard.jsx'
import AdminAnalytics from './pages/AdminAnalytics.jsx'

// App.jsx is the "map" of the site. Each <Route> says:
// "when the URL matches this path, show this page component."
// AuthProvider wraps everything so any page can call useAuth() to check
// who's logged in, without us passing that data down manually.
export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-12">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/palm" element={<PalmReading />} />
            <Route path="/tarot" element={<TarotReading />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/profile"
              element={
                <RequireAuth>
                  <Profile />
                </RequireAuth>
              }
            />
            <Route
              path="/history"
              element={
                <RequireAuth>
                  <History />
                </RequireAuth>
              }
            />
            <Route
              path="/dashboard"
              element={
                <RequireAuth>
                  <Dashboard />
                </RequireAuth>
              }
            />
            <Route
              path="/admin/analytics"
              element={
                <RequireAuth>
                  <AdminAnalytics />
                </RequireAuth>
              }
            />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  )
}
