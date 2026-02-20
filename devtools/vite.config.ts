import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        port: 3000,
        host: true,
        proxy: {
            '/api': {
                target: 'http://localhost:9696',
                changeOrigin: true,
            },
        },
    },
});
