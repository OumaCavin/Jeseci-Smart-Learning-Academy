import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  // Restore standard Vite behavior
  build: {
    outDir: 'dist',
    manifest: true,  // Allows Vite to place it in .vite/manifest.json
    rollupOptions: {
      input: 'src/client_runtime.js'  // Correct entry point
      // Remove output config - let Vite handle filenames naturally
    }
  },

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});