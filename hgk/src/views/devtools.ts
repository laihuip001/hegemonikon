import './css/devtools.css';
/**
 * DevTools View — IDE Core Features in HGK APP
 *
 * Antigravity IDE のコア機能を HGK APP に統合:
 *   1. ファイルエクスプローラ (ツリー表示)
 *   2. コードビューア (シンタックスハイライトなし、行番号付き)
 *   3. ターミナル (コマンド実行)
 *   4. AI アシスタント (Cortex API ask_with_tools)
 *
 * すべて Gateway API (localhost:9696) 経由で実行。
 */

import { marked } from 'marked';

// ─── Types ───────────────────────────────────────────────────

interface FileEntry {
    name: string;
    path: string;
    is_dir: boolean;
    size?: number;
    children?: number;
}

interface TerminalLine {
    type: 'input' | 'output' | 'error';
    text: string;
    timestamp: Date;
}

// ─── State ───────────────────────────────────────────────────

const API = 'http://127.0.0.1:9696/api';
let currentPath = '/home/makaron8426/oikos/hegemonikon';
let pathHistory: string[] = [currentPath];
let openFilePath = '';
let openFileContent = '';
let terminalHistory: TerminalLine[] = [];
let cmdHistory: string[] = [];
let cmdHistoryIdx = -1;
let aiConversation: { role: 'user' | 'ai'; text: string }[] = [];
// Active tab tracked by DOM state (dt-tab-active class)

// ─── API Calls ───────────────────────────────────────────────

async function apiListDir(path: string): Promise<FileEntry[]> {
    try {
        const res = await fetch(`${API}/files/list?path=${encodeURIComponent(path)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data.entries || data;
    } catch {
        // Fallback: ask_with_tools to list directory
        try {
            const res = await fetch(`${API}/ochema/ask_with_tools`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `list_directory ツールで ${path} の内容を一覧してください。JSON 配列で name, is_dir, size を返してください。`,
                    model: 'gemini-2.0-flash',
                    max_iterations: 1,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                // Try to parse entries from response
                const text = data.text || data.response || '';
                const match = text.match(/\[[\s\S]*\]/);
                if (match) return JSON.parse(match[0]);
            }
        } catch { /* silent */ }
        return [];
    }
}

async function apiReadFile(path: string): Promise<string> {
    try {
        const res = await fetch(`${API}/files/read?path=${encodeURIComponent(path)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data.content || data.text || '';
    } catch {
        try {
            const res = await fetch(`${API}/ochema/ask_with_tools`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `read_file ツールで ${path} の内容を読み取り、そのまま返してください。`,
                    model: 'gemini-2.0-flash',
                    max_iterations: 1,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                return data.text || data.response || '(読み込みエラー)';
            }
        } catch { /* silent */ }
        return '(ファイル読み込み失敗)';
    }
}

async function apiRunCommand(cmd: string, cwd: string): Promise<string> {
    try {
        const res = await fetch(`${API}/terminal/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd, cwd }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data.output || data.stdout || '';
    } catch {
        try {
            const res = await fetch(`${API}/ochema/ask_with_tools`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `run_command ツールで以下を実行してください:\nコマンド: ${cmd}\nディレクトリ: ${cwd}\n結果をそのまま返してください。`,
                    model: 'gemini-2.0-flash',
                    max_iterations: 1,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                return data.text || data.response || '(実行エラー)';
            }
        } catch { /* silent */ }
        return '(コマンド実行失敗)';
    }
}

async function apiAskWithTools(message: string, model: string): Promise<string> {
    try {
        const res = await fetch(`${API}/ochema/ask_with_tools`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                model,
                max_iterations: 10,
                system_instruction: 'あなたは Hegemonikón の開発アシスタントです。日本語で応答。ツールを使ってファイル読み書き・コマンド実行が可能です。',
            }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data.text || data.response || '(応答なし)';
    } catch (e) {
        return `エラー: ${(e as Error).message}`;
    }
}

// ─── Helpers ─────────────────────────────────────────────────

function esc(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function fileIcon(entry: FileEntry): string {
    if (entry.is_dir) return '📁';
    const ext = entry.name.split('.').pop()?.toLowerCase() || '';
    const icons: Record<string, string> = {
        py: '🐍', ts: '📘', js: '📒', json: '📋', md: '📝',
        yaml: '⚙️', yml: '⚙️', css: '🎨', html: '🌐',
        sh: '💻', toml: '📦', txt: '📄', rs: '🦀',
    };
    return icons[ext] || '📄';
}

function formatSize(bytes?: number): string {
    if (bytes === undefined || bytes === null) return '';
    if (bytes === 0) return '0B';
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}K`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}M`;
}

function basename(path: string): string {
    return path.split('/').filter(Boolean).pop() || '/';
}

function normalizePath(p: string): string {
    const parts = p.split('/').filter(Boolean);
    const out: string[] = [];
    for (const seg of parts) {
        if (seg === '..') out.pop();
        else if (seg !== '.') out.push(seg);
    }
    return '/' + out.join('/');
}

const HOME_DIR = '/home/makaron8426/oikos/hegemonikon';
let prevCwd = HOME_DIR;

const BINARY_EXTS = new Set([
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico', 'webp', 'svg',
    'woff', 'woff2', 'ttf', 'eot', 'otf',
    'zip', 'gz', 'tar', 'bz2', 'xz', '7z',
    'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'mp3', 'mp4', 'wav', 'avi', 'mov',
    'pyc', 'pyo', 'so', 'dll', 'exe', 'bin',
]);

function isBinary(name: string): boolean {
    const ext = name.split('.').pop()?.toLowerCase() || '';
    return BINARY_EXTS.has(ext);
}

const MAX_DISPLAY_LINES = 5000;

// ─── Render: File Explorer ───────────────────────────────────

async function renderFileTree(): Promise<void> {
    const panel = document.getElementById('dt-file-panel');
    if (!panel) return;

    panel.innerHTML = '<div class="dt-loading">📂 読み込み中...</div>';
    const entries = await apiListDir(currentPath);

    // Sort: dirs first, then by name
    entries.sort((a, b) => {
        if (a.is_dir !== b.is_dir) return a.is_dir ? -1 : 1;
        return a.name.localeCompare(b.name);
    });

    // Breadcrumb
    const parts = currentPath.split('/').filter(Boolean);
    const breadcrumb = parts.map((p, i) => {
        const fullPath = '/' + parts.slice(0, i + 1).join('/');
        return `<span class="dt-breadcrumb-item" data-path="${fullPath}">${esc(p)}</span>`;
    }).join('<span class="dt-breadcrumb-sep">/</span>');

    panel.innerHTML = `
        <div class="dt-breadcrumb">
            <span class="dt-breadcrumb-item" data-path="/">🏠</span>
            <span class="dt-breadcrumb-sep">/</span>
            ${breadcrumb}
        </div>
        <div class="dt-file-list">
            ${entries.length === 0 ? '<div class="dt-empty">空のディレクトリ</div>' :
            entries.map(e => `
                <div class="dt-file-entry ${e.is_dir ? 'dt-dir' : 'dt-file'} ${currentPath + '/' + e.name === openFilePath ? 'dt-file-active' : ''}"
                     data-path="${esc(currentPath + '/' + e.name)}" data-is-dir="${e.is_dir}">
                    <span class="dt-file-icon">${fileIcon(e)}</span>
                    <span class="dt-file-name">${esc(e.name)}</span>
                    <span class="dt-file-meta">${e.is_dir ? '' : formatSize(e.size)}</span>
                </div>
            `).join('')}
        </div>
    `;

    // Bind events
    panel.querySelectorAll('.dt-file-entry').forEach(el => {
        el.addEventListener('click', () => {
            const path = (el as HTMLElement).dataset.path || '';
            const isDir = (el as HTMLElement).dataset.isDir === 'true';
            if (isDir) {
                currentPath = path;
                pathHistory.push(path);
                void renderFileTree();
            } else {
                void openFile(path);
            }
        });
    });

    panel.querySelectorAll('.dt-breadcrumb-item').forEach(el => {
        el.addEventListener('click', () => {
            const path = (el as HTMLElement).dataset.path || '/';
            currentPath = path;
            pathHistory.push(path);
            void renderFileTree();
        });
    });
}

// ─── Render: Code Viewer ─────────────────────────────────────

async function openFile(path: string): Promise<void> {
    openFilePath = path;
    const viewer = document.getElementById('dt-code-viewer');
    if (!viewer) return;

    const name = basename(path);

    // Binary file check
    if (isBinary(name)) {
        const ext = name.split('.').pop()?.toLowerCase() || '';
        const isImage = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext);
        viewer.innerHTML = `
            <div class="dt-viewer-header">
                <span class="dt-viewer-filename">${fileIcon({ name, path, is_dir: false })} ${esc(name)}</span>
                <span class="dt-viewer-path">${esc(path)}</span>
                <span class="dt-viewer-info">${isImage ? '画像ファイル' : 'バイナリファイル'}</span>
            </div>
            <div class="dt-viewer-empty">
                <div style="font-size:3rem">${isImage ? '🖼️' : '📦'}</div>
                <div style="font-weight:600;margin-top:0.5rem">${isImage ? '画像プレビュー未対応' : 'バイナリファイル'}</div>
                <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:0.25rem">
                    このファイルはテキストとして表示できません
                </div>
            </div>
        `;
        document.querySelectorAll('.dt-file-entry').forEach(el => {
            el.classList.toggle('dt-file-active', (el as HTMLElement).dataset.path === path);
        });
        return;
    }

    viewer.innerHTML = `<div class="dt-loading">📖 ${esc(name)} を読み込み中...</div>`;
    openFileContent = await apiReadFile(path);

    const allLines = openFileContent.split('\n');
    const truncated = allLines.length > MAX_DISPLAY_LINES;
    const lines = truncated ? allLines.slice(0, MAX_DISPLAY_LINES) : allLines;
    const lineNums = lines.map((_, i) => `<span>${i + 1}</span>`).join('\n');
    const code = lines.map(l => esc(l)).join('\n');

    const truncMsg = truncated
        ? `<div class="dt-truncation-notice">⚠️ ${allLines.length} 行中 ${MAX_DISPLAY_LINES} 行を表示</div>`
        : '';

    viewer.innerHTML = `
        <div class="dt-viewer-header">
            <span class="dt-viewer-filename">${fileIcon({ name, path, is_dir: false })} ${esc(name)}</span>
            <span class="dt-viewer-path">${esc(path)}</span>
            <span class="dt-viewer-info">${allLines.length} 行 | ${formatSize(openFileContent.length)}</span>
            <button class="btn btn-sm btn-outline dt-copy-btn" title="コピー">📋</button>
        </div>
        ${truncMsg}
        <div class="dt-code-container">
            <pre class="dt-line-numbers">${lineNums}</pre>
            <pre class="dt-code"><code>${code}</code></pre>
        </div>
    `;

    viewer.querySelector('.dt-copy-btn')?.addEventListener('click', () => {
        void navigator.clipboard.writeText(openFileContent).then(() => {
            const btn = viewer.querySelector('.dt-copy-btn')!;
            btn.textContent = '✓';
            setTimeout(() => { btn.textContent = '📋'; }, 1500);
        });
    });

    // Sync scroll between line numbers and code
    const codeEl = viewer.querySelector('.dt-code');
    const numsEl = viewer.querySelector('.dt-line-numbers');
    if (codeEl && numsEl) {
        codeEl.addEventListener('scroll', () => {
            numsEl.scrollTop = codeEl.scrollTop;
        });
    }

    // Highlight active file in list
    document.querySelectorAll('.dt-file-entry').forEach(el => {
        el.classList.toggle('dt-file-active', (el as HTMLElement).dataset.path === path);
    });
}

// ─── Render: Terminal ────────────────────────────────────────

function renderTerminal(): void {
    const panel = document.getElementById('dt-terminal-panel');
    if (!panel) return;

    panel.innerHTML = `
        <div class="dt-term-output" id="dt-term-output">
            ${terminalHistory.length === 0
            ? '<div class="dt-term-welcome">💻 ターミナル — コマンドを入力して Enter<br><span style="color:var(--text-secondary)">cwd: ${esc(currentPath)}</span></div>'
            : terminalHistory.map(l => `<div class="dt-term-line dt-term-${l.type}">${l.type === 'input' ? '<span class="dt-term-prompt">$ </span>' : ''}${esc(l.text)}</div>`).join('')
        }
        </div>
        <div class="dt-term-input-area">
            <span class="dt-term-prompt-icon">$</span>
            <input type="text" id="dt-term-input" class="dt-term-input" placeholder="コマンドを入力..." autocomplete="off" />
        </div>
    `;

    const input = document.getElementById('dt-term-input') as HTMLInputElement;
    const output = document.getElementById('dt-term-output')!;
    output.scrollTop = output.scrollHeight;

    input?.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const cmd = input.value.trim();
            if (!cmd) return;
            input.value = '';
            cmdHistory.unshift(cmd);
            cmdHistoryIdx = -1;

            // Handle cd
            if (cmd === 'cd' || cmd.startsWith('cd ')) {
                const target = cmd === 'cd' ? '~' : cmd.slice(3).trim();
                let newCwd: string;
                if (target === '~' || target === '') {
                    newCwd = HOME_DIR;
                } else if (target === '-') {
                    newCwd = prevCwd;
                } else if (target.startsWith('/')) {
                    newCwd = target;
                } else if (target.startsWith('~')) {
                    newCwd = HOME_DIR + target.slice(1);
                } else {
                    newCwd = currentPath + '/' + target;
                }
                newCwd = normalizePath(newCwd);
                prevCwd = currentPath;
                currentPath = newCwd;
                terminalHistory.push({ type: 'input', text: cmd, timestamp: new Date() });
                terminalHistory.push({ type: 'output', text: `cd → ${currentPath}`, timestamp: new Date() });
                renderTerminal();
                void renderFileTree();
                return;
            }

            // Handle clear
            if (cmd === 'clear') {
                terminalHistory = [];
                renderTerminal();
                return;
            }

            terminalHistory.push({ type: 'input', text: cmd, timestamp: new Date() });
            renderTerminal();

            const result = await apiRunCommand(cmd, currentPath);
            if (result.trim()) {
                terminalHistory.push({ type: 'output', text: result, timestamp: new Date() });
            } else {
                terminalHistory.push({ type: 'output', text: '(完了 — 出力なし)', timestamp: new Date() });
            }
            renderTerminal();
            document.getElementById('dt-term-input')?.focus();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (cmdHistoryIdx < cmdHistory.length - 1) {
                cmdHistoryIdx++;
                input.value = cmdHistory[cmdHistoryIdx] ?? '';
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (cmdHistoryIdx > 0) {
                cmdHistoryIdx--;
                input.value = cmdHistory[cmdHistoryIdx] ?? '';
            } else {
                cmdHistoryIdx = -1;
                input.value = '';
            }
        }
    });

    input?.focus();
}

// ─── Render: AI Assistant ────────────────────────────────────

function renderAI(): void {
    const panel = document.getElementById('dt-ai-panel');
    if (!panel) return;

    panel.innerHTML = `
        <div class="dt-ai-messages" id="dt-ai-messages">
            ${aiConversation.length === 0
            ? `<div class="dt-ai-welcome">
                    <div style="font-size:2rem">🤖</div>
                    <div style="font-weight:600">AI アシスタント</div>
                    <div style="color:var(--text-secondary);font-size:0.85rem">Cortex API (ask_with_tools) — ファイル操作・コマンド実行可能</div>
                    <div class="dt-ai-hints">
                        <span class="dt-ai-hint">ochema のテストを実行して</span>
                        <span class="dt-ai-hint">tools.py の構造を教えて</span>
                        <span class="dt-ai-hint">最新の git log を見せて</span>
                    </div>
                </div>`
            : aiConversation.map(m => `
                <div class="dt-ai-msg dt-ai-msg-${m.role}">
                    <div class="dt-ai-msg-role">${m.role === 'user' ? '👤' : '🤖'}</div>
                    <div class="dt-ai-msg-body">${m.role === 'user' ? esc(m.text) : (marked.parse(m.text) as string)}</div>
                </div>
            `).join('')
        }
        </div>
        <div class="dt-ai-input-area">
            <textarea id="dt-ai-input" class="dt-ai-input" placeholder="AI に指示... (Enter で送信、Shift+Enter で改行)" rows="1"></textarea>
            <button id="dt-ai-send" class="btn dt-ai-send-btn">送信</button>
        </div>
    `;

    const msgContainer = document.getElementById('dt-ai-messages')!;
    msgContainer.scrollTop = msgContainer.scrollHeight;

    const input = document.getElementById('dt-ai-input') as HTMLTextAreaElement;
    const sendBtn = document.getElementById('dt-ai-send')!;

    const send = async () => {
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        input.style.height = 'auto';

        aiConversation.push({ role: 'user', text });
        aiConversation.push({ role: 'ai', text: '⏳ 考え中...' });
        renderAI();

        const result = await apiAskWithTools(text, 'gemini-3-pro-preview');
        const last = aiConversation[aiConversation.length - 1];
        if (last) last.text = result;
        renderAI();
    };

    input?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            void send();
        }
    });
    input?.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 150) + 'px';
    });
    sendBtn?.addEventListener('click', () => void send());

    // Hint clicks
    panel.querySelectorAll('.dt-ai-hint').forEach(hint => {
        hint.addEventListener('click', () => {
            if (input) {
                input.value = hint.textContent ?? '';
                void send();
            }
        });
    });

    input?.focus();
}

// ─── Tab Switching ───────────────────────────────────────────

function switchTab(tab: 'files' | 'terminal' | 'ai'): void {
    document.querySelectorAll('.dt-tab').forEach(t =>
        t.classList.toggle('dt-tab-active', (t as HTMLElement).dataset.tab === tab)
    );

    const panelIds = ['dt-file-panel', 'dt-terminal-panel', 'dt-ai-panel'];
    panelIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });

    const panelId = `dt-${tab === 'files' ? 'file' : tab}-panel`;
    const activePanel = document.getElementById(panelId);
    if (activePanel) activePanel.style.display = 'flex';

    if (tab === 'terminal') renderTerminal();
    if (tab === 'ai') renderAI();
}

// ─── Main Render ─────────────────────────────────────────────

export async function renderDevToolsView(): Promise<void> {
    const app = document.getElementById('view-content');
    if (!app) return;

    app.innerHTML = `
        <div class="dt-container">
            <div class="dt-sidebar">
                <div class="dt-tabs">
                    <button class="dt-tab dt-tab-active" data-tab="files">📁 Files</button>
                    <button class="dt-tab" data-tab="terminal">💻 Terminal</button>
                    <button class="dt-tab" data-tab="ai">🤖 AI</button>
                </div>
                <div id="dt-file-panel" class="dt-panel" style="display:flex"></div>
                <div id="dt-terminal-panel" class="dt-panel" style="display:none"></div>
                <div id="dt-ai-panel" class="dt-panel" style="display:none"></div>
            </div>
            <div class="dt-main">
                <div id="dt-code-viewer" class="dt-code-viewer">
                    <div class="dt-viewer-empty">
                        <div style="font-size:3rem">📝</div>
                        <div style="font-weight:600;margin-top:0.5rem">DevTools</div>
                        <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:0.25rem">
                            ファイルを選択して表示<br>
                            Ctrl+\` でターミナル | Ctrl+I で AI
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Tab events
    document.querySelectorAll('.dt-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab((tab as HTMLElement).dataset.tab as 'files' | 'terminal' | 'ai');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e: KeyboardEvent) => {
        const target = e.target as HTMLElement;
        if (target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA') return;
        if (e.ctrlKey && e.key === '`') {
            e.preventDefault();
            switchTab('terminal');
        }
        if (e.ctrlKey && e.key === 'i') {
            e.preventDefault();
            switchTab('ai');
        }
    });

    // Load file tree
    await renderFileTree();
}
