import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',       // Standard output directory
    manifest: 'manifest.json', // Force manifest to root (Fixes "No bundle found")
    rollupOptions: {
      // Explicitly tell Vite where to start (Fixes "index.html" error)
      input: 'src/main.js',
      output: {
        // Force the output to be a predictable filename to bypass hash lookup failures
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