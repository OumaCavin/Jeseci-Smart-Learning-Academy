import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    // 1. Force manifest to be in the root of dist
    manifest: 'manifest.json', 
    rollupOptions: {
      input: 'src/client_runtime.js',
      output: {
        // 2. CRITICAL: Force the exact filename Jac expects
        entryFileNames: 'client_runtime.js', 
        // 3. Ensure chunks don't get hashed randomly
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