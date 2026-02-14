import { defineConfig } from "vite";

const host = process.env.TAURI_DEV_HOST;

// https://vitejs.dev/config/
export default defineConfig(async () => ({
    // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
    //
    // 1. prevent vite from obscuring rust errors
    clearScreen: false,
    // 2. tauri expects a fixed port, fail if that port is not available
    server: {
        port: 1420,
        strictPort: true,
        host: host || false,
        hmr: host
            ? {
                protocol: "ws",
                host,
                port: 1421,
            }
            : undefined,
        watch: {
            // Avoid inotify watchers entirely — Firefox ESR consumes 90K+ FDs,
            // leaving none for chokidar. Polling is slower but stable.
            usePolling: true,
            interval: 1000,
            ignored: [
                "**/src-tauri/**",
                "**/node_modules/**",
                "**/.git/**",
            ],
        },
    },
}));
