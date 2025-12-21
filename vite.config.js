import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    manifest: 'manifest.json', // Explicit path for jac-client compatibility
    rollupOptions: {
      input: 'src/client_runtime.js'
    }
  }
});