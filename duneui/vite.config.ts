import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/google": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/documents": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/ollama": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      },
      "/gpt": {
        target: "http://localhost:8000", // Change to your backend URL
        changeOrigin: true,
        secure: false,
      }
  }}
})
