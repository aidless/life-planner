import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // 注：曾用自定义 manualChunks 按 react/antd 切分 vendor，
    // 但 rollup 跨 chunk 的 react 命名空间导出错位（antd-vendor 拿到 undefined.createContext），
    // 生产包全页报错。改回默认分包（正确性优先于 chunk 体积）。
    chunkSizeWarningLimit: 1500,
  },
})
