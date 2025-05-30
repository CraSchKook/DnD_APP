import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1', // или '0.0.0.0' если хочешь открыть в сети
    port: 5173,         // можешь указать другой, если этот занят
    strictPort: true    // если порт занят — выдаст ошибку, а не подберёт случайный
  }
})
