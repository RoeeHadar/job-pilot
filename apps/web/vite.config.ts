import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const apiTarget = loadEnv(mode, process.cwd(), '').VITE_API_TARGET || 'http://127.0.0.1:8000'
  return {
    plugins: [react()],
    server: {
      // Dedicated Job Pilot port — 5173/5180/5181 are often used by other projects
      port: 5190,
      strictPort: true,
      proxy: {
        '/api': apiTarget,
        '/health': apiTarget,
      },
    },
  }
})
