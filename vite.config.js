import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [],
  build: {
    outDir: 'dist',
    manifest: 'manifest.json',
    rollupOptions: {
      input: 'app.jac',
      output: {
        entryFileNames: 'client_runtime.js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  },
  server: {
    port: 3000
  }
});
