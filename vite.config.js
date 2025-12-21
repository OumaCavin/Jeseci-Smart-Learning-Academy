import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [],
  build: {
    outDir: 'dist',
    manifest: false,
    rollupOptions: {
      input: 'src/client_runtime.js'
    }
  }
});