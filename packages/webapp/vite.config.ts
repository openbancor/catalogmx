import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
    },
  },
  resolve: {
    alias: {
      catalogmx: resolve(__dirname, '../typescript/src'),
    },
  },
  optimizeDeps: {
    exclude: ['better-sqlite3'],
  },
  define: {
    'process.env': {},
  },
});
