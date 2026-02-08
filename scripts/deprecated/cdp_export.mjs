#!/usr/bin/env node
/**
 * CDP Export - Antigravity セッション DOM エクスポート
 * 
 * Electron の /json/list ハングをバイパスし、
 * WebSocket + Target.getTargets で直接ターゲットを列挙する。
 * 
 * Usage:
 *   node scripts/cdp_export.mjs [--port 9223] [--list] [--export-all]
 */

import { WebSocket } from 'ws';  // Fallback below if not available
import http from 'http';
import fs from 'fs';
import path from 'path';

const CDP_PORT = parseInt(process.argv.find((_, i, a) => a[i - 1] === '--port') || '9223');
const MODE = process.argv.includes('--export-all') ? 'export' :
    process.argv.includes('--list') ? 'list' : 'list';
const OUTPUT_DIR = '/home/makaron8426/oikos/mneme/.hegemonikon/sessions';

// --- CDP Helper ---
function getVersion(port) {
    return new Promise((resolve, reject) => {
        const req = http.get(`http://127.0.0.1:${port}/json/version`, { timeout: 5000 }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    });
}

function cdpConnect(wsUrl) {
    return new Promise((resolve, reject) => {
        // Try native WebSocket first, then ws package
        let ws;
        try {
            ws = new WebSocket(wsUrl);
        } catch (e) {
            reject(new Error('WebSocket not available. Run: npm install ws'));
            return;
        }

        let msgId = 0;
        const pending = new Map();

        ws.on('open', () => {
            console.log('[OK] WebSocket connected');
            resolve({
                send(method, params = {}) {
                    return new Promise((res, rej) => {
                        const id = ++msgId;
                        pending.set(id, { resolve: res, reject: rej });
                        ws.send(JSON.stringify({ id, method, params }));
                        setTimeout(() => {
                            if (pending.has(id)) {
                                pending.delete(id);
                                rej(new Error(`Timeout: ${method}`));
                            }
                        }, 30000);
                    });
                },
                close() { ws.close(); },
                ws
            });
        });

        ws.on('message', (data) => {
            const msg = JSON.parse(data.toString());
            if (msg.id && pending.has(msg.id)) {
                const p = pending.get(msg.id);
                pending.delete(msg.id);
                if (msg.error) p.reject(new Error(JSON.stringify(msg.error)));
                else p.resolve(msg.result);
            }
        });

        ws.on('error', reject);
        ws.on('close', () => console.log('[INFO] WS closed'));

        setTimeout(() => reject(new Error('WS connection timeout')), 10000);
    });
}

// --- Main ---
async function main() {
    console.log(`[*] CDP Export - port ${CDP_PORT}`);

    // 1. Get browser WS URL
    let version;
    try {
        version = await getVersion(CDP_PORT);
        console.log(`[OK] Browser: ${version.Browser}`);
    } catch (e) {
        console.error(`[FAIL] Cannot reach CDP on port ${CDP_PORT}: ${e.message}`);
        console.error('  → Start Antigravity with: /usr/share/antigravity/antigravity --remote-debugging-port=9223');
        process.exit(1);
    }

    const wsUrl = version.webSocketDebuggerUrl;
    if (!wsUrl) {
        console.error('[FAIL] No webSocketDebuggerUrl in version response');
        process.exit(1);
    }

    // 2. Connect via WebSocket (bypasses /json/list)
    const cdp = await cdpConnect(wsUrl);

    // 3. Get all targets
    const { targetInfos } = await cdp.send('Target.getTargets');
    console.log(`[OK] Found ${targetInfos.length} targets`);

    // 4. Find jetski-agent pages (chat panel)
    const jetskiTargets = targetInfos.filter(t => t.url.includes('jetski-agent'));
    const pageTargets = targetInfos.filter(t => t.type === 'page');

    console.log('\n=== Targets ===');
    for (const t of targetInfos) {
        const marker = t.url.includes('jetski-agent') ? ' ★ JETSKI' : '';
        console.log(`  ${t.type.padEnd(15)} ${t.title.substring(0, 50).padEnd(50)} ${t.url.substring(0, 80)}${marker}`);
    }

    if (jetskiTargets.length === 0) {
        console.log('\n[!] No jetski-agent target found.');
        console.log('    Available page targets:');
        for (const t of pageTargets) {
            console.log(`      ${t.title.substring(0, 60)}  ${t.url.substring(0, 80)}`);
        }
        cdp.close();
        process.exit(0);
    }

    if (MODE === 'list') {
        console.log(`\n[OK] Found ${jetskiTargets.length} jetski-agent target(s)`);
        cdp.close();
        process.exit(0);
    }

    // 5. Export mode: attach to jetski-agent and extract conversations
    console.log(`\n[*] Exporting from ${jetskiTargets.length} jetski-agent target(s)...`);
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });

    for (const target of jetskiTargets) {
        console.log(`\n[*] Attaching to: ${target.title}`);

        // Attach to target
        const { sessionId } = await cdp.send('Target.attachToTarget', {
            targetId: target.targetId,
            flatten: true
        });

        // Enable Runtime
        await cdp.send('Runtime.enable', {}, sessionId);

        // Extract conversation list from DOM
        const convListResult = await cdp.send('Runtime.evaluate', {
            expression: `
        (function() {
          const buttons = document.querySelectorAll('button.select-none');
          return JSON.stringify(Array.from(buttons).map((btn, i) => {
            const span = btn.querySelector('span[data-testid], span.truncate');
            return {
              id: 'conv_' + i,
              title: span ? span.textContent.trim() : null
            };
          }).filter(c => c.title && c.title.length > 2));
        })()
      `,
            returnByValue: true
        });

        if (convListResult.result && convListResult.result.value) {
            const conversations = JSON.parse(convListResult.result.value);
            console.log(`[OK] Found ${conversations.length} conversations`);

            // Save conversation list
            const listFile = path.join(OUTPUT_DIR, `conversation_list_${new Date().toISOString().slice(0, 10)}.json`);
            fs.writeFileSync(listFile, JSON.stringify(conversations, null, 2));
            console.log(`[OK] Saved list: ${listFile}`);

            // Get full DOM of the current chat view
            const domResult = await cdp.send('Runtime.evaluate', {
                expression: `document.documentElement.outerHTML`,
                returnByValue: true
            });

            if (domResult.result && domResult.result.value) {
                const domFile = path.join(OUTPUT_DIR, `dom_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '')}.html`);
                fs.writeFileSync(domFile, domResult.result.value);
                console.log(`[OK] DOM saved: ${domFile} (${(domResult.result.value.length / 1024).toFixed(0)} KB)`);
            }
        } else {
            console.log('[!] Could not extract conversations');
            console.log('    Result:', JSON.stringify(convListResult).substring(0, 200));
        }

        // Detach
        await cdp.send('Target.detachFromTarget', { sessionId });
    }

    cdp.close();
    console.log('\n[✓] Export complete');
}

main().catch(e => {
    console.error(`[FATAL] ${e.message}`);
    process.exit(1);
});
