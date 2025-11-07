import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        react(),
        tailwindcss()
    ],
    server: {
        port: 9007, // 指定端口号
        host: true, // 允许外部访问
        open: true  // 自动打开浏览器
    }
})