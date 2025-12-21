import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      // THE FIX: Map the missing package to our local file
      '@jac-client/utils': path.resolve(__dirname, 'src/jac_utils.js')
    }
  },

  esbuild: {
    loader: "jsx",
    include: /src\/.*\.js?$/,
    exclude: []
  },

  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.js': 'jsx',
      },
    },
  },

  build: {
    outDir: 'dist',
    manifest: 'manifest.json',
    rollupOptions: {
      input: 'src/main.js',
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