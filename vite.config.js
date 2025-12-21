import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  // Simplified config - client_runtime.js doesn't need complex workarounds
  build: {
    outDir: 'dist',
    manifest: 'manifest.json',
    rollupOptions: {
      // THE KEY FIX: Point back to the file Jac expects
      input: 'src/client_runtime.js',
      output: {
        entryFileNames: 'client_runtime.js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
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