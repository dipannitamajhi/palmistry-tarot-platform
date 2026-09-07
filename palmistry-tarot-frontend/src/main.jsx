import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

// This is the actual starting point of the app. Vite loads this file first.
// BrowserRouter enables page navigation (Home -> Palm Reading -> Tarot Reading)
// without full page reloads, which is how modern single-page apps work.
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
