import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function pythonVitePlugin() {
  return {
    name: 'python-vite-plugin',
    configureServer(server) {
      server.httpServer?.once('listening', () => {
        const address = server.httpServer?.address();
        if (address) {
          const protocol = server.config.server.https ? 'https' : 'http';
          let host = typeof address === 'string' ? address : address.address;
          if (host === '::' || host === '::1' || host === '0.0.0.0' || host === '127.0.0.1') {
            host = 'localhost';
          }
          const port = typeof address === 'string' ? '' : address.port;
          const url = `${protocol}://${host}:${port}`;
          fs.writeFileSync(path.resolve(__dirname, 'public/hot'), url);
        }
      });
    },
    buildStart() {
      const hotPath = path.resolve(__dirname, 'public/hot');
      if (fs.existsSync(hotPath)) {
        try {
          fs.unlinkSync(hotPath);
        } catch (e) {
          // Ignore errors
        }
      }
    }
  };
}

export default defineConfig({
  plugins: [
    tailwindcss(),
    pythonVitePlugin(),
  ],
  publicDir: false,
  build: {
    manifest: true,
    outDir: 'public/build',
    rollupOptions: {
      input: [
        'resources/js/app.js',
        'resources/css/app.css'
      ],
    },
  },
});
