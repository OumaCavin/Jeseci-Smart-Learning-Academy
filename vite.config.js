import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    manifest: true, // In Vite 4, this defaults to 'dist/manifest.json' (Correct for Jac)
    rollupOptions: {
      input: 'src/client_runtime.js'
    }
  }
});