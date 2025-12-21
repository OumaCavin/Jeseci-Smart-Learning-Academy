import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    // 1. Force manifest to be in the root of dist (Fixes 'No bundle found')
    manifest: 'manifest.json', 
    rollupOptions: {
      // 2. Point to the file Jac generates
      input: 'src/client_runtime.js',
      output: {
        // 3. Force simple filenames (Fixes path mismatches)
        entryFileNames: 'client_runtime.js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  }
});