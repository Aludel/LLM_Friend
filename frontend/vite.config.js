import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
  ],
  server: {
    // 必须显式绑 IPv4。Vite 默认 host: 'localhost'，Node 17+ 解析 localhost 时
    // 优先返回 ::1，于是开发服务器只监听 IPv6 回环；本机 IPv6 不通时浏览器
    // 访问 localhost 会直接 ERR_CONNECTION_REFUSED（后端绑的是 IPv4，所以只有前端挂）。
    host: '127.0.0.1',
  },
  build: {
    outDir: path.resolve(import.meta.dirname, '../backend/static/frontend'), // 打包到 Django static
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
