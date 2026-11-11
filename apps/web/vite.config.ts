import tailwindcss from '@tailwindcss/vite';
import { reactRouter } from '@react-router/dev/vite';
import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  plugins: [tailwindcss(), reactRouter()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: {
    port: Number(process.env.PORT || 3000),
    strictPort: true,
    proxy: {
      '/api/v1': {
        target: new URL(process.env.API_INTERNAL_URL || 'http://127.0.0.1:8100/api/v1').origin,
        changeOrigin: false,
      },
    },
  },
});
