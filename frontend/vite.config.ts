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
        // P2-2: e2e 隔离允许经 E2E_API_PROXY 改写代理目标；缺省仍指 8001 生产后端。
        target: process.env.E2E_API_PROXY ?? 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
  build: {
    outDir: 'dist',
    // 生产包不带 sourcemap（曾占 6.3MB）；调试时可临时改回 true。
    sourcemap: false,
    // 注1：曾用自定义 manualChunks 按 react/antd 切分 vendor，
    // 但 rollup 跨 chunk 的 react 命名空间导出错位（antd-vendor 拿到 undefined.createContext），
    // 生产包全页报错。改回默认分包（正确性优先于 chunk 体积）。
    // 注2：入口 chunk min 体积 602KB 超 500KB 默认线，但实测 gzip 仅 194KB，
    // 路由已全量 React.lazy，antd 全命名导入（tree-shaken），此为 antd 应用正常下限，不再拆。
    chunkSizeWarningLimit: 1500,
  },
})
