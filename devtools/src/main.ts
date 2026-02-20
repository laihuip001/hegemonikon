/**
 * HGK DevTools — Standalone IDE Application
 *
 * Premium IDE experience:
 *   - File Explorer with tree navigation
 *   - Code Viewer with line numbers + syntax hints
 *   - Terminal (command execution via Gateway)
 *   - AI Assistant (Cortex API ask_with_tools)
 *   - Tab management for multiple files
 *   - Status bar with connection status
 *
 * Backend: Gateway API (localhost:9696) via Vite proxy
 */

import './style.css';

// ─── Types ────────────────────────────────────────────────────

interface FileEntry {
    name: string;
    path: string;
    is_dir: boolean;
    size?: number;
    children?: number;
}

interface OpenTab {
    path: string;
    name: string;
    content: string;
    icon: string;
}

interface TermLine {
    type: 'cmd' | 'out' | 'err' | 'info';
    text: string;
}

interface AiMsg {
    role: 'user' | 'ai';
    text: string;
}

// ─── State ────────────────────────────────────────────────────

const API = '/api';
let cwd = '/home/makaron8426/oikos/hegemonikon';
let tabs: OpenTab[] = [];
let activeTabPath = '';
let termLines: TermLine[] = [];
let cmdHistory: string[] = [];
let cmdIdx = -1;
let aiMessages: AiMsg[] = [];
let activePanel: 'terminal' | 'ai' = 'terminal';
let panelCollapsed = false;
let gatewayOnline = false;

// ─── API ──────────────────────────────────────────────────────

async function apiListDir(path: string): Promise<FileEntry[]> {
    try {
        const r = await fetch(`${API}/files/list?path=${encodeURIComponent(path)}`);
        if (!r.ok) throw new Error(`${r.status}`);
        const d = await r.json();
        gatewayOnline = true;
        return d.entries || [];
    } catch {
        gatewayOnline = false;
        return [];
    }
}

async function apiReadFile(path: string): Promise<string> {
    try {
        const r = await fetch(`${API}/files/read?path=${encodeURIComponent(path)}`);
        if (!r.ok) throw new Error(`${r.status}`);
        const d = await r.json();
        return d.content || '';
    } catch {
        return '(ファイル読み込み失敗)';
    }
}

async function apiRunCmd(cmd: string): Promise<{ output: string; code: number }> {
    try {
        const r = await fetch(`${API}/terminal/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd, cwd }),
        });
        if (!r.ok) throw new Error(`${r.status}`);
        const d = await r.json();
        return { output: d.output || '', code: d.returncode ?? 0 };
    } catch {
        return { output: '(コマンド実行失敗 — Gateway 未接続)', code: -1 };
    }
}

async function apiAsk(msg: string): Promise<string> {
    try {
        const r = await fetch(`${API}/ochema/ask_with_tools`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg,
                model: 'gemini-2.0-flash',
                max_iterations: 10,
                system_instruction: 'Hegemonikón 開発アシスタント。日本語応答。ファイル操作・コマンド実行可能。',
            }),
        });
        if (!r.ok) throw new Error(`${r.status}`);
        const d = await r.json();
        return d.text || '(応答なし)';
    } catch (e) {
        return `エラー: ${(e as Error).message}`;
    }
}

// ─── Helpers ──────────────────────────────────────────────────

function h(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function fileIcon(name: string, isDir: boolean): string {
    if (isDir) return '📁';
    const ext = name.split('.').pop()?.toLowerCase() || '';
    const m: Record<string, string> = {
        py: '🐍', ts: '📘', js: '📒', json: '📋', md: '📝',
        yaml: '⚙️', yml: '⚙️', css: '🎨', html: '🌐',
        sh: '💻', toml: '📦', txt: '📄', rs: '🦀',
        lock: '🔒', png: '🖼️', jpg: '🖼️', svg: '🖼️',
    };
    return m[ext] || '📄';
}

function fmtSize(b?: number): string {
    if (b === undefined || b === null) return '';
    if (b === 0) return '0B';
    if (b < 1024) return `${b}B`;
    if (b < 1048576) return `${(b / 1024).toFixed(1)}K`;
    return `${(b / 1048576).toFixed(1)}M`;
}

function basename(p: string): string {
    return p.split('/').filter(Boolean).pop() || '/';
}

function normalizePath(p: string): string {
    const parts = p.split('/').filter(Boolean);
    const out: string[] = [];
    for (const seg of parts) {
        if (seg === '..') {
            out.pop();
        } else if (seg !== '.') {
            out.push(seg);
        }
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

// ─── Render: App Shell ────────────────────────────────────────

function renderApp(): void {
    const app = document.getElementById('app')!;
    app.innerHTML = `
    <div class="ide">
      <div class="ide-toolbar">
        <div class="ide-toolbar-logo">
          ⚡ <span>HGK DevTools</span>
        </div>
        <div class="ide-toolbar-actions">
          <button class="btn btn-sm" id="btn-refresh" title="更新">🔄</button>
          <button class="btn btn-sm" id="btn-home" title="ホームに戻る">🏠</button>
        </div>
      </div>

      <div class="ide-body">
        <div class="sidebar" id="sidebar">
          <div class="sidebar-header">
            <svg viewBox="0 0 16 16" fill="currentColor"><path d="M1.75 1A1.75 1.75 0 000 2.75v10.5C0 14.216.784 15 1.75 15H6v-2H1.75a.25.25 0 01-.25-.25V5H6V3H1.75a.25.25 0 01-.25-.25V2.75c0-.138.112-.25.25-.25h5a.25.25 0 01.25.25V5h2V2.75c0-.138.112-.25.25-.25h5c.138 0 .25.112.25.25v.25H16V2.75A1.75 1.75 0 0014.25 1z"/></svg>
            EXPLORER
          </div>
          <div class="breadcrumb" id="breadcrumb"></div>
          <div class="sidebar-tree" id="file-tree"></div>
        </div>

        <div class="resize-handle" id="resize-sidebar"></div>

        <div class="main">
          <div class="tab-bar" id="tab-bar"></div>
          <div class="editor-area" id="editor-area"></div>

          <div class="bottom-panels" id="bottom-panels">
            <div class="panel-tabs">
              <button class="panel-tab active" data-panel="terminal">
                <span class="panel-tab-icon">💻</span> Terminal
              </button>
              <button class="panel-tab" data-panel="ai">
                <span class="panel-tab-icon">🤖</span> AI Assistant
              </button>
              <button class="panel-toggle" id="panel-toggle">▼</button>
            </div>
            <div class="panel-body" id="panel-body">
              <div class="terminal" id="terminal-panel"></div>
              <div class="ai-panel" id="ai-panel" style="display:none"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="statusbar">
        <div class="statusbar-section">
          <span class="statusbar-dot ${gatewayOnline ? '' : 'offline'}" id="status-dot"></span>
          <span id="status-text">${gatewayOnline ? 'Gateway Connected' : 'Gateway Offline'}</span>
        </div>
        <div class="statusbar-section" id="status-file"></div>
        <div class="statusbar-right">
          <div class="statusbar-section" id="status-cwd">📁 ${basename(cwd)}</div>
          <div class="statusbar-section">HGK DevTools v1.0</div>
        </div>
      </div>
    </div>
  `;

    bindEvents();
    renderTree();
    renderTabs();
    renderEditor();
    renderTerminal();
    renderAI();
}

// ─── Render: File Tree ────────────────────────────────────────

async function renderTree(): Promise<void> {
    const tree = document.getElementById('file-tree')!;
    const bc = document.getElementById('breadcrumb')!;

    // Breadcrumb
    const parts = cwd.split('/').filter(Boolean);
    bc.innerHTML = parts.map((p, i) => {
        const full = '/' + parts.slice(0, i + 1).join('/');
        return `<span class="breadcrumb-item" data-path="${full}">${h(p)}</span>`;
    }).join('<span class="breadcrumb-sep">›</span>');

    bc.querySelectorAll('.breadcrumb-item').forEach(el => {
        el.addEventListener('click', () => {
            cwd = (el as HTMLElement).dataset.path || '/';
            renderTree();
            updateStatus();
        });
    });

    tree.innerHTML = '<div class="tree-loading">読み込み中<span class="loading-dots"></span></div>';
    const entries = await apiListDir(cwd);

    // Update connection status
    const dot = document.getElementById('status-dot');
    const txt = document.getElementById('status-text');
    if (dot) dot.className = `statusbar-dot ${gatewayOnline ? '' : 'offline'}`;
    if (txt) txt.textContent = gatewayOnline ? 'Gateway Connected' : 'Gateway Offline';

    entries.sort((a, b) => {
        if (a.is_dir !== b.is_dir) return a.is_dir ? -1 : 1;
        return a.name.localeCompare(b.name);
    });

    if (!entries.length) {
        tree.innerHTML = '<div class="tree-empty">空のディレクトリ</div>';
        return;
    }

    tree.innerHTML = entries.map(e => `
    <div class="tree-item ${activeTabPath === e.path ? 'selected' : ''}"
         data-path="${h(e.path)}" data-dir="${e.is_dir}">
      <span class="tree-icon">${fileIcon(e.name, e.is_dir)}</span>
      <span class="tree-name ${e.is_dir ? 'is-dir' : ''}">${h(e.name)}</span>
      <span class="tree-meta">${e.is_dir ? '' : fmtSize(e.size)}</span>
    </div>
  `).join('');

    tree.querySelectorAll('.tree-item').forEach(el => {
        el.addEventListener('click', () => {
            const path = (el as HTMLElement).dataset.path || '';
            const isDir = (el as HTMLElement).dataset.dir === 'true';
            if (isDir) {
                cwd = path;
                renderTree();
                updateStatus();
            } else {
                openFile(path);
            }
        });
    });
}

// ─── Open File in Tab ─────────────────────────────────────────

async function openFile(path: string): Promise<void> {
    // Check if already open
    const existing = tabs.find(t => t.path === path);
    if (existing) {
        activeTabPath = path;
        renderTabs();
        renderEditor();
        highlightTree();
        return;
    }

    const name = basename(path);
    const icon = fileIcon(name, false);

    // Binary file check
    if (isBinary(name)) {
        const ext = name.split('.').pop()?.toLowerCase() || '';
        const isImage = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext);
        const content = isImage
            ? `[画像ファイル: ${name}]\n\nプレビューは未対応です。\nパス: ${path}`
            : `[バイナリファイル: ${name}]\n\nこのファイルはテキストとして表示できません。\nパス: ${path}`;
        tabs.push({ path, name, content, icon });
        activeTabPath = path;
        renderTabs();
        renderEditor();
        highlightTree();
        updateStatus();
        return;
    }

    const content = await apiReadFile(path);
    tabs.push({ path, name, content, icon });
    activeTabPath = path;

    renderTabs();
    renderEditor();
    highlightTree();
    updateStatus();
}

function closeTab(path: string): void {
    tabs = tabs.filter(t => t.path !== path);
    if (activeTabPath === path) {
        activeTabPath = tabs.length ? tabs[tabs.length - 1].path : '';
    }
    renderTabs();
    renderEditor();
    highlightTree();
    updateStatus();
}

// ─── Render: Tabs ─────────────────────────────────────────────

function renderTabs(): void {
    const bar = document.getElementById('tab-bar')!;
    if (!tabs.length) {
        bar.innerHTML = '';
        return;
    }

    bar.innerHTML = tabs.map(t => `
    <div class="tab ${t.path === activeTabPath ? 'active' : ''}" data-path="${h(t.path)}">
      <span class="tab-icon">${t.icon}</span>
      <span class="tab-name">${h(t.name)}</span>
      <span class="tab-close" data-close="${h(t.path)}">✕</span>
    </div>
  `).join('');

    bar.querySelectorAll('.tab').forEach(el => {
        el.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;
            if (target.classList.contains('tab-close')) {
                closeTab(target.dataset.close || '');
            } else {
                activeTabPath = (el as HTMLElement).dataset.path || '';
                renderTabs();
                renderEditor();
                highlightTree();
                updateStatus();
            }
        });
    });
}

// ─── Render: Editor ───────────────────────────────────────────

function renderEditor(): void {
    const area = document.getElementById('editor-area')!;
    const tab = tabs.find(t => t.path === activeTabPath);

    if (!tab) {
        area.innerHTML = `
      <div class="editor-welcome">
        <div class="editor-welcome-icon">⚡</div>
        <h2>HGK DevTools</h2>
        <p>Hegemonikón 統合開発環境</p>
        <div class="editor-shortcuts">
          <div class="editor-shortcut"><kbd>Ctrl</kbd>+<kbd>\`</kbd> Terminal</div>
          <div class="editor-shortcut"><kbd>Ctrl</kbd>+<kbd>I</kbd> AI</div>
        </div>
      </div>
    `;
        return;
    }

    const allLines = tab.content.split('\n');
    const truncated = allLines.length > MAX_DISPLAY_LINES;
    const lines = truncated ? allLines.slice(0, MAX_DISPLAY_LINES) : allLines;
    const nums = lines.map((_, i) => `<span>${i + 1}</span>`).join('');
    const code = lines.map(l => h(l)).join('\n');

    const truncMsg = truncated
        ? `<div class="editor-truncated">⚠️ ${allLines.length} 行中 ${MAX_DISPLAY_LINES} 行を表示 (パフォーマンス制限)</div>`
        : '';

    area.innerHTML = `
    ${truncMsg}
    <div class="code-container">
      <div class="line-numbers">${nums}</div>
      <pre class="code-content">${code}</pre>
    </div>
  `;

    // Sync scroll between line numbers and code
    const codeEl = area.querySelector('.code-content');
    const numsEl = area.querySelector('.line-numbers');
    if (codeEl && numsEl) {
        codeEl.addEventListener('scroll', () => {
            numsEl.scrollTop = codeEl.scrollTop;
        });
    }
}

// ─── Render: Terminal ─────────────────────────────────────────

function renderTerminal(): void {
    const panel = document.getElementById('terminal-panel')!;

    panel.innerHTML = `
    <div class="terminal-output" id="term-output">
      ${termLines.length === 0
            ? `<div class="term-line term-info">HGK DevTools Terminal — cwd: ${h(cwd)}</div>`
            : termLines.map(l => {
                if (l.type === 'cmd') {
                    return `<div class="term-line term-cmd"><span class="term-prompt">❯ </span>${h(l.text)}</div>`;
                }
                return `<div class="term-line term-${l.type}">${h(l.text)}</div>`;
            }).join('')
        }
    </div>
    <div class="terminal-input">
      <span class="terminal-prompt">❯</span>
      <input type="text" id="term-input" placeholder="コマンドを入力..." autocomplete="off" spellcheck="false" />
    </div>
  `;

    const output = document.getElementById('term-output')!;
    output.scrollTop = output.scrollHeight;

    const input = document.getElementById('term-input') as HTMLInputElement;
    input?.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const cmd = input.value.trim();
            if (!cmd) return;
            input.value = '';
            cmdHistory.unshift(cmd);
            cmdIdx = -1;

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
                    newCwd = cwd + '/' + target;
                }
                newCwd = normalizePath(newCwd);
                prevCwd = cwd;
                cwd = newCwd;
                termLines.push({ type: 'cmd', text: cmd });
                termLines.push({ type: 'info', text: `cd → ${cwd}` });
                renderTerminal();
                renderTree();
                updateStatus();
                return;
            }

            // Handle clear
            if (cmd === 'clear') {
                termLines = [];
                renderTerminal();
                return;
            }

            termLines.push({ type: 'cmd', text: cmd });
            renderTerminal();

            const result = await apiRunCmd(cmd);
            if (result.output.trim()) {
                termLines.push({
                    type: result.code !== 0 ? 'err' : 'out',
                    text: result.output.trimEnd(),
                });
            } else if (result.code === 0) {
                termLines.push({ type: 'info', text: '(完了 — 出力なし)' });
            } else {
                termLines.push({ type: 'err', text: `(終了コード: ${result.code})` });
            }
            renderTerminal();
            document.getElementById('term-input')?.focus();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (cmdIdx < cmdHistory.length - 1) {
                cmdIdx++;
                input.value = cmdHistory[cmdIdx] ?? '';
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (cmdIdx > 0) {
                cmdIdx--;
                input.value = cmdHistory[cmdIdx] ?? '';
            } else {
                cmdIdx = -1;
                input.value = '';
            }
        }
    });

    input?.focus();
}

// ─── Render: AI ───────────────────────────────────────────────

function renderAI(): void {
    const panel = document.getElementById('ai-panel')!;

    panel.innerHTML = `
    <div class="ai-messages" id="ai-messages">
      ${aiMessages.length === 0
            ? `<div class="ai-welcome">
            <div class="ai-welcome-icon">🤖</div>
            <h3>AI アシスタント</h3>
            <div style="color:var(--text-muted);font-size:12px">Cortex API — ファイル操作 + コマンド実行</div>
            <div class="ai-hints">
              <span class="ai-hint">このプロジェクトの構成を教えて</span>
              <span class="ai-hint">テストを実行して</span>
              <span class="ai-hint">git log を見せて</span>
            </div>
          </div>`
            : aiMessages.map(m => `
            <div class="ai-msg ai-msg-${m.role}">
              <div class="ai-msg-avatar">${m.role === 'user' ? '👤' : '🤖'}</div>
              <div class="ai-msg-body">${m.role === 'user' ? h(m.text) : formatAiText(m.text)}</div>
            </div>
          `).join('')
        }
    </div>
    <div class="ai-input-area">
      <textarea id="ai-input" class="ai-input" placeholder="AI に質問... (Enter で送信)" rows="1"></textarea>
      <button id="ai-send" class="btn btn-primary btn-sm">送信</button>
    </div>
  `;

    const msgs = document.getElementById('ai-messages')!;
    msgs.scrollTop = msgs.scrollHeight;

    const input = document.getElementById('ai-input') as HTMLTextAreaElement;
    const sendBtn = document.getElementById('ai-send')!;

    const send = async () => {
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        input.style.height = 'auto';

        aiMessages.push({ role: 'user', text });
        aiMessages.push({ role: 'ai', text: '考え中...' });
        renderAI();

        const result = await apiAsk(text);
        const last = aiMessages[aiMessages.length - 1];
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
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });

    sendBtn?.addEventListener('click', () => void send());

    panel.querySelectorAll('.ai-hint').forEach(hint => {
        hint.addEventListener('click', () => {
            if (input) {
                input.value = hint.textContent ?? '';
                void send();
            }
        });
    });
}

function formatAiText(text: string): string {
    // Simple markdown-like formatting
    return text
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

// ─── Helpers ──────────────────────────────────────────────────

function highlightTree(): void {
    document.querySelectorAll('.tree-item').forEach(el => {
        el.classList.toggle('selected', (el as HTMLElement).dataset.path === activeTabPath);
    });
}

function updateStatus(): void {
    const fileEl = document.getElementById('status-file');
    const cwdEl = document.getElementById('status-cwd');
    if (fileEl) {
        const tab = tabs.find(t => t.path === activeTabPath);
        fileEl.textContent = tab ? `${tab.name} — ${tab.content.split('\n').length} 行` : '';
    }
    if (cwdEl) cwdEl.textContent = `📁 ${basename(cwd)}`;
}

function switchPanel(panel: 'terminal' | 'ai'): void {
    activePanel = panel;
    const termEl = document.getElementById('terminal-panel');
    const aiEl = document.getElementById('ai-panel');
    if (termEl) termEl.style.display = panel === 'terminal' ? 'flex' : 'none';
    if (aiEl) aiEl.style.display = panel === 'ai' ? 'flex' : 'none';

    document.querySelectorAll('.panel-tab').forEach(t => {
        t.classList.toggle('active', (t as HTMLElement).dataset.panel === panel);
    });

    if (panel === 'terminal') {
        renderTerminal();
    } else {
        renderAI();
    }
}

function togglePanel(): void {
    panelCollapsed = !panelCollapsed;
    const body = document.getElementById('panel-body');
    const toggle = document.getElementById('panel-toggle');
    if (body) body.classList.toggle('collapsed', panelCollapsed);
    if (toggle) toggle.textContent = panelCollapsed ? '▲' : '▼';
}

// ─── Events ───────────────────────────────────────────────────

function bindEvents(): void {
    // Panel tabs
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const panel = (tab as HTMLElement).dataset.panel as 'terminal' | 'ai';
            if (panel) switchPanel(panel);
        });
    });

    document.getElementById('panel-toggle')?.addEventListener('click', togglePanel);
    document.getElementById('btn-refresh')?.addEventListener('click', () => renderTree());
    document.getElementById('btn-home')?.addEventListener('click', () => {
        cwd = '/home/makaron8426/oikos/hegemonikon';
        renderTree();
        updateStatus();
    });

    // Sidebar resize
    const resizeHandle = document.getElementById('resize-sidebar');
    const sidebar = document.getElementById('sidebar');
    if (resizeHandle && sidebar) {
        let dragging = false;
        resizeHandle.addEventListener('mousedown', (e) => {
            dragging = true;
            resizeHandle.classList.add('active');
            e.preventDefault();
        });
        document.addEventListener('mousemove', (e) => {
            if (!dragging) return;
            const w = Math.max(180, Math.min(500, e.clientX));
            sidebar.style.width = w + 'px';
        });
        document.addEventListener('mouseup', () => {
            dragging = false;
            resizeHandle.classList.remove('active');
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        const target = e.target as HTMLElement;
        if (target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA') return;

        if (e.ctrlKey && e.key === '`') {
            e.preventDefault();
            if (panelCollapsed) togglePanel();
            switchPanel('terminal');
        }
        if (e.ctrlKey && e.key === 'i') {
            e.preventDefault();
            if (panelCollapsed) togglePanel();
            switchPanel('ai');
        }
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            const sb = document.getElementById('sidebar');
            const rh = document.getElementById('resize-sidebar');
            if (sb) {
                const hidden = sb.style.display === 'none';
                sb.style.display = hidden ? 'flex' : 'none';
                if (rh) rh.style.display = hidden ? 'block' : 'none';
            }
        }
        if (e.ctrlKey && e.key === 'w') {
            e.preventDefault();
            if (activeTabPath) closeTab(activeTabPath);
        }
    });
}

// ─── Boot ─────────────────────────────────────────────────────

renderApp();
