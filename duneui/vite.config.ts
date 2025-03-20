import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/auth": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/documents": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/chat": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/docs": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/users": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/openapi.json": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      }
  }}
})
