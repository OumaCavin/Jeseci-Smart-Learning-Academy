import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  build: {
    outDir: 'dist',
    manifest: true,
    rollupOptions: {
      input: 'src/client_runtime.js',
      output: {
        entryFileNames: 'client_runtime.js',
        chunkFileNames: 'chunks/[name].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
      '/walker': 'http://localhost:8000',
      '/function': 'http://localhost:8000',
      '/page': 'http://localhost:8000'
    }
  },
  
  optimizeDeps: {
    include: ['@jac-client/utils']
  }
});