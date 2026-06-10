import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
  publicDir: false, // Disables copying of the public folder to avoid the recursion warning
  build: {
    manifest: true, // Generate manifest.json
    outDir: 'public/build', // Output directory for compiled assets
    rollupOptions: {
      input: {
        app: 'resources/js/app.js',
        'app.css': 'resources/css/app.css',
      },
    },
  },
  server: {
    // Ensure Vite dev server runs on a different port than FastAPI
    port: 5173,
    strictPort: true,
  },
  resolve: {
    alias: {
      '~': path.resolve(__dirname, './resources'),
    },
  },
});