import { defineConfig } from 'vite'
import { resolve } from 'path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
    base: "/static/",
    build: {
        manifest: true,
        outDir: resolve("./core/staticfiles"),
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'static/js/main.js')
            }
        }
    },
    plugins: [
        tailwindcss()
    ],
})
