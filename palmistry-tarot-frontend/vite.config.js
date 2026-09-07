import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite is the tool that runs our dev server and bundles the app for production.
// It's faster than older tools (like Create React App) and is the current standard.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Any request our frontend makes to /api/* gets forwarded to our backend.
      // This avoids CORS headaches during local development.
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
