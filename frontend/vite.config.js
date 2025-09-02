import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { host: true, port: 8080 },
  resolve: {
    alias: { '@': '/src' } // no 'path' import needed
  }
})
