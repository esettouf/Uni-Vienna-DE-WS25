import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    // Proxy API requests to Flask backend
    proxy: {
      '/graphql': {
        target: 'http://backend:5000',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true,
      }
    }
  }
})
