/**
 * Orchestrator View — AI 指揮台 (F4 MVP)
 *
 * 3-pane layout:
 *   Left:   File tree browser (read-only)
 *   Center: Chat with AI (Ochema ask_with_tools)
 *   Right:  Changes panel (git status + diff) + Terminal log
 */

import { api, type FileEntry, type GitFileStatus } from '../api/client';
import './orchestrator.css';

// ─── State ──────────────────────────────────────────────────
interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    model?: string;
    thinking?: string;
}

let chatHistory: ChatMessage[] = [];
let expandedDirs: Set<string> = new Set();
let selectedFile: string | null = null;
let isLoading = false;
let currentModel = 'gemini-2.0-flash';
let terminalLog: string[] = [];
let changedFiles: GitFileStatus[] = [];
let activeDiff = '';
let rightTab: 'changes' | 'terminal' | 'file' = 'changes';

// ─── Utilities ──────────────────────────────────────────────
function esc(s: string): string {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

function timeStr(d: Date): string {
    return d.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
}

function getFileIcon(name: string): string {
    if (name.endsWith('.ts') || name.endsWith('.tsx')) return '🟦';
    if (name.endsWith('.py')) return '🐍';
    if (name.endsWith('.md')) return '📄';
    if (name.endsWith('.json')) return '📋';
    if (name.endsWith('.css')) return '🎨';
    if (name.endsWith('.html')) return '🌐';
    if (name.endsWith('.yaml') || name.endsWith('.yml')) return '⚙️';
    if (name.endsWith('.rs')) return '🦀';
    if (name.endsWith('.sh')) return '📜';
    return '📃';
}

function getStatusIcon(status: string): string {
    switch (status) {
        case 'modified': return '<span class="orch-status-badge orch-status-modified">M</span>';
        case 'added': return '<span class="orch-status-badge orch-status-added">A</span>';
        case 'deleted': return '<span class="orch-status-badge orch-status-deleted">D</span>';
        case 'untracked': return '<span class="orch-status-badge orch-status-untracked">?</span>';
        default: return '<span class="orch-status-badge">·</span>';
    }
}

// ─── Diff Renderer ──────────────────────────────────────────
function renderDiffBlock(diff: string): string {
    if (!diff.trim()) return '<div class="orch-diff-empty">変更なし</div>';

    const lines = diff.split('\n');
    let html = '<div class="orch-diff-content">';
    let lineNum = 0;

    for (const line of lines) {
        lineNum++;
        if (line.startsWith('+++') || line.startsWith('---')) {
            html += `<div class="orch-diff-line orch-diff-meta">${esc(line)}</div>`;
        } else if (line.startsWith('@@')) {
            html += `<div class="orch-diff-line orch-diff-hunk">${esc(line)}</div>`;
        } else if (line.startsWith('+')) {
            html += `<div class="orch-diff-line orch-diff-add">${esc(line)}</div>`;
        } else if (line.startsWith('-')) {
            html += `<div class="orch-diff-line orch-diff-del">${esc(line)}</div>`;
        } else {
            html += `<div class="orch-diff-line">${esc(line) || '&nbsp;'}</div>`;
        }
    }
    html += '</div>';
    return html;
}

// ─── Chat Renderer ──────────────────────────────────────────
function renderMessage(msg: ChatMessage): string {
    const isUser = msg.role === 'user';
    const bubbleClass = isUser ? 'orch-msg-user' : 'orch-msg-assistant';
    const icon = isUser ? '👤' : '🤖';

    // Parse code blocks in assistant messages
    let content = esc(msg.content);
    // Convert ```...``` blocks to <pre><code>
    content = content.replace(/```(\w*)\n([\s\S]*?)```/g, (_m, lang, code) =>
        `<pre class="orch-code-block"><code class="language-${lang || 'text'}">${code}</code></pre>`
    );
    // Convert inline `code` to <code>
    content = content.replace(/`([^`]+)`/g, '<code class="orch-inline-code">$1</code>');
    // Convert newlines
    content = content.replace(/\n/g, '<br>');

    let thinkingHtml = '';
    if (msg.thinking && msg.thinking.trim()) {
        thinkingHtml = `
            <details class="orch-thinking">
                <summary>💭 思考過程</summary>
                <div class="orch-thinking-content">${esc(msg.thinking).replace(/\n/g, '<br>')}</div>
            </details>`;
    }

    return `
        <div class="orch-message ${bubbleClass}">
            <div class="orch-msg-header">
                <span class="orch-msg-icon">${icon}</span>
                <span class="orch-msg-time">${timeStr(msg.timestamp)}</span>
                ${msg.model ? `<span class="orch-msg-model">${esc(msg.model)}</span>` : ''}
            </div>
            <div class="orch-msg-body">${content}</div>
            ${thinkingHtml}
        </div>`;
}

// ─── File Tree Renderer ─────────────────────────────────────
async function loadDir(path: string): Promise<FileEntry[]> {
    try {
        const resp = await api.filesList(path);
        return resp.entries;
    } catch {
        return [];
    }
}

async function renderFileTree(container: HTMLElement, basePath: string, depth = 0): Promise<void> {
    const entries = await loadDir(basePath);
    let html = '';

    for (const entry of entries) {
        const indent = depth * 16;
        const isExpanded = expandedDirs.has(entry.path);
        const isSelected = selectedFile === entry.path;

        if (entry.is_dir) {
            html += `
                <div class="orch-tree-item ${isSelected ? 'selected' : ''}"
                     style="padding-left: ${indent + 8}px"
                     data-path="${esc(entry.path)}" data-is-dir="true">
                    <span class="orch-tree-arrow ${isExpanded ? 'expanded' : ''}">▶</span>
                    <span class="orch-tree-icon">📁</span>
                    <span class="orch-tree-name">${esc(entry.name)}</span>
                    ${entry.children ? `<span class="orch-tree-count">${entry.children}</span>` : ''}
                </div>
                ${isExpanded ? `<div class="orch-tree-children" data-parent="${esc(entry.path)}"></div>` : ''}`;
        } else {
            html += `
                <div class="orch-tree-item ${isSelected ? 'selected' : ''}"
                     style="padding-left: ${indent + 24}px"
                     data-path="${esc(entry.path)}" data-is-dir="false">
                    <span class="orch-tree-icon">${getFileIcon(entry.name)}</span>
                    <span class="orch-tree-name">${esc(entry.name)}</span>
                    ${entry.size ? `<span class="orch-tree-size">${(entry.size / 1024).toFixed(1)}KB</span>` : ''}
                </div>`;
        }
    }

    container.innerHTML = html;

    // Attach click handlers
    container.querySelectorAll('.orch-tree-item').forEach(item => {
        item.addEventListener('click', async () => {
            const path = item.getAttribute('data-path')!;
            const isDir = item.getAttribute('data-is-dir') === 'true';

            if (isDir) {
                if (expandedDirs.has(path)) {
                    expandedDirs.delete(path);
                } else {
                    expandedDirs.add(path);
                }
                // Re-render tree from root
                const treeRoot = document.getElementById('orch-file-tree')!;
                await renderFileTree(treeRoot, '/home/makaron8426/oikos/hegemonikon');
            } else {
                selectedFile = path;
                await showFileContent(path);
            }
        });
    });

    // Recursively render expanded children
    for (const dir of expandedDirs) {
        const childContainer = container.querySelector(`[data-parent="${dir}"]`) as HTMLElement | null;
        if (childContainer) {
            await renderFileTree(childContainer, dir, depth + 1);
        }
    }
}

async function showFileContent(path: string): Promise<void> {
    rightTab = 'file';
    const rightPanel = document.getElementById('orch-right-panel')!;
    if (!rightPanel) return;

    try {
        const resp = await api.filesRead(path);
        const filename = path.split('/').pop() || path;
        rightPanel.innerHTML = `
            <div class="orch-right-header">
                <div class="orch-right-tabs">
                    <button class="orch-tab" data-tab="changes">Changes</button>
                    <button class="orch-tab" data-tab="terminal">Terminal</button>
                    <button class="orch-tab active" data-tab="file">📄 ${esc(filename)}</button>
                </div>
            </div>
            <div class="orch-file-viewer">
                <pre class="orch-file-content"><code>${esc(resp.content)}</code></pre>
            </div>`;
        attachRightTabHandlers();
    } catch (err) {
        rightPanel.innerHTML = `<div class="orch-error">ファイルを開けません: ${esc(String(err))}</div>`;
    }
}

// ─── Changes Panel ──────────────────────────────────────────
async function loadChanges(): Promise<void> {
    try {
        const resp = await api.gitStatus();
        changedFiles = resp.files;
    } catch {
        changedFiles = [];
    }
}

function renderChangesPanel(): string {
    if (changedFiles.length === 0) {
        return '<div class="orch-empty-state">✨ 変更はありません</div>';
    }

    let html = `<div class="orch-changes-header">
        <span class="orch-changes-count">${changedFiles.length} ファイル変更</span>
    </div><div class="orch-changes-list">`;

    for (const f of changedFiles) {
        const filename = f.path.split('/').pop() || f.path;
        html += `
            <div class="orch-change-item" data-path="${esc(f.path)}">
                ${getStatusIcon(f.status)}
                <span class="orch-change-name" title="${esc(f.path)}">${esc(filename)}</span>
                <button class="orch-diff-btn" aria-label="ファイルの差分を表示" data-path="${esc(f.path)}" title="差分を表示">📋</button>
            </div>`;
    }
    html += '</div>';

    if (activeDiff) {
        html += `<div class="orch-diff-viewer">${renderDiffBlock(activeDiff)}</div>`;
    }

    return html;
}

function renderTerminalPanel(): string {
    if (terminalLog.length === 0) {
        return '<div class="orch-empty-state">📟 ターミナル出力はまだありません</div>';
    }
    return `<div class="orch-terminal-log"><pre>${terminalLog.map(l => esc(l)).join('\n')}</pre></div>`;
}

// ─── Right Panel ────────────────────────────────────────────
function updateRightPanel(): void {
    const panel = document.getElementById('orch-right-panel');
    if (!panel) return;

    const tabsHtml = `
        <div class="orch-right-header">
            <div class="orch-right-tabs">
                <button class="orch-tab ${rightTab === 'changes' ? 'active' : ''}" data-tab="changes">
                    Changes ${changedFiles.length > 0 ? `<span class="orch-badge">${changedFiles.length}</span>` : ''}
                </button>
                <button class="orch-tab ${rightTab === 'terminal' ? 'active' : ''}" data-tab="terminal">Terminal</button>
            </div>
        </div>`;

    let contentHtml = '';
    if (rightTab === 'changes') {
        contentHtml = renderChangesPanel();
    } else if (rightTab === 'terminal') {
        contentHtml = renderTerminalPanel();
    }

    panel.innerHTML = tabsHtml + `<div class="orch-right-content">${contentHtml}</div>`;
    attachRightTabHandlers();
    attachDiffHandlers();
}

function attachRightTabHandlers(): void {
    document.querySelectorAll('.orch-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.getAttribute('data-tab') as 'changes' | 'terminal' | 'file';
            if (tab === 'file') return; // file tab is contextual
            rightTab = tab;
            updateRightPanel();
        });
    });
}

function attachDiffHandlers(): void {
    document.querySelectorAll('.orch-diff-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const path = btn.getAttribute('data-path')!;
            try {
                const resp = await api.gitDiff(undefined, path);
                activeDiff = resp.diff;
                updateRightPanel();
            } catch (err) {
                activeDiff = `Error: ${err}`;
                updateRightPanel();
            }
        });
    });
}

// ─── Chat Logic ─────────────────────────────────────────────
async function sendMessage(text: string): Promise<void> {
    if (!text.trim() || isLoading) return;

    const userMsg: ChatMessage = {
        role: 'user',
        content: text.trim(),
        timestamp: new Date(),
    };
    chatHistory.push(userMsg);
    isLoading = true;
    updateChatArea();

    // System instruction for AI
    const systemPrompt = `あなたは Hegemonikón プロジェクトの AI アシスタントです。
ユーザーの指示に基づいてファイルの読み書き、コード修正、テスト実行などを行います。
作業ディレクトリは /home/makaron8426/oikos/hegemonikon です。
日本語で応答してください。`;

    try {
        const resp = await api.orchestratorChat(text.trim(), currentModel, systemPrompt);

        const assistantMsg: ChatMessage = {
            role: 'assistant',
            content: resp.text,
            timestamp: new Date(),
            model: resp.model,
            thinking: resp.thinking,
        };
        chatHistory.push(assistantMsg);

        // Add to terminal log
        terminalLog.push(`[${timeStr(new Date())}] AI Response received (${resp.model})`);

        // Refresh changes after AI action
        await loadChanges();
        updateRightPanel();
    } catch (err) {
        const errorMsg: ChatMessage = {
            role: 'system',
            content: `エラー: ${err}`,
            timestamp: new Date(),
        };
        chatHistory.push(errorMsg);
        terminalLog.push(`[${timeStr(new Date())}] Error: ${err}`);
    } finally {
        isLoading = false;
        updateChatArea();
    }
}

function updateChatArea(): void {
    const chatArea = document.getElementById('orch-chat-messages');
    if (!chatArea) return;

    let html = '';
    if (chatHistory.length === 0) {
        html = `
            <div class="orch-welcome">
                <div class="orch-welcome-icon">🎯</div>
                <h2>AI 指揮台</h2>
                <p>AI に作業指示を送信しましょう。ファイル操作、コード修正、テスト実行が可能です。</p>
                <div class="orch-suggestions">
                    <button class="orch-suggestion" data-msg="テストを実行して結果を教えて">🧪 テスト実行</button>
                    <button class="orch-suggestion" data-msg="直近の git log を5件表示して">📋 Git ログ</button>
                    <button class="orch-suggestion" data-msg="プロジェクトの構造を教えて">🗂️ 構造確認</button>
                </div>
            </div>`;
    } else {
        html = chatHistory.map(renderMessage).join('');
    }

    if (isLoading) {
        html += `
            <div class="orch-message orch-msg-assistant orch-loading">
                <div class="orch-msg-header">
                    <span class="orch-msg-icon">🤖</span>
                    <span class="orch-msg-time">${timeStr(new Date())}</span>
                </div>
                <div class="orch-msg-body">
                    <div class="orch-typing">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>`;
    }

    chatArea.innerHTML = html;
    chatArea.scrollTop = chatArea.scrollHeight;

    // Attach suggestion handlers
    chatArea.querySelectorAll('.orch-suggestion').forEach(btn => {
        btn.addEventListener('click', () => {
            const msg = btn.getAttribute('data-msg')!;
            const input = document.getElementById('orch-chat-input') as HTMLTextAreaElement;
            if (input) {
                input.value = msg;
                sendMessage(msg);
                input.value = '';
            }
        });
    });
}

// ─── Model Selector ─────────────────────────────────────────
const MODELS = [
    { id: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash', icon: '⚡' },
    { id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash', icon: '🔥' },
    { id: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro', icon: '💎' },
    { id: 'gemini-3-pro-preview', label: 'Gemini 3 Pro', icon: '🚀' },
];

// ─── Main Renderer ──────────────────────────────────────────
export async function renderOrchestratorView(): Promise<void> {
    const app = document.getElementById('view-content')!;

    app.innerHTML = `
        <div class="orch-container">
            <!-- Left: File Tree -->
            <div class="orch-left-panel">
                <div class="orch-panel-header">
                    <span class="orch-panel-title">📁 Files</span>
                </div>
                <div class="orch-file-tree-wrapper">
                    <div id="orch-file-tree" class="orch-file-tree">
                        <div class="orch-loading-tree">読込中...</div>
                    </div>
                </div>
            </div>

            <!-- Center: Chat -->
            <div class="orch-center-panel">
                <div class="orch-chat-header">
                    <div class="orch-model-select">
                        <select id="orch-model-selector" class="orch-select">
                            ${MODELS.map(m =>
        `<option value="${m.id}" ${m.id === currentModel ? 'selected' : ''}>
                                    ${m.icon} ${m.label}
                                </option>`
    ).join('')}
                        </select>
                    </div>
                    <div class="orch-chat-actions">
                        <button id="orch-clear-chat" class="orch-icon-btn" aria-label="チャット履歴をクリア" title="チャットをクリア">🗑️</button>
                    </div>
                </div>
                <div id="orch-chat-messages" class="orch-chat-messages"></div>
                <div class="orch-chat-input-area">
                    <textarea id="orch-chat-input" class="orch-chat-input"
                              placeholder="AI に指示を送る... (Enter で送信、Shift+Enter で改行)"
                              rows="2"></textarea>
                    <button id="orch-send-btn" class="orch-send-btn" aria-label="メッセージを送信" title="送信">
                        <span class="orch-send-icon">➤</span>
                    </button>
                </div>
            </div>

            <!-- Right: Changes / Terminal -->
            <div id="orch-right-panel" class="orch-right-panel">
                <div class="orch-loading-tree">読込中...</div>
            </div>
        </div>

        <!-- Status Bar -->
        <div class="orch-status-bar">
            <span class="orch-status-indicator orch-status-connected"></span>
            <span>Connected</span>
            <span class="orch-status-sep">·</span>
            <span id="orch-status-model">${MODELS.find(m => m.id === currentModel)?.label || currentModel}</span>
            <span class="orch-status-sep">·</span>
            <span id="orch-status-changes">0 files changed</span>
        </div>`;

    // ─── Event Handlers ─────────────────────────────────────
    const input = document.getElementById('orch-chat-input') as HTMLTextAreaElement;
    const sendBtn = document.getElementById('orch-send-btn')!;
    const modelSelect = document.getElementById('orch-model-selector') as HTMLSelectElement;
    const clearBtn = document.getElementById('orch-clear-chat')!;

    // Send on Enter (not Shift+Enter)
    input.addEventListener('keydown', (e: KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input.value);
            input.value = '';
        }
    });

    // Send button
    sendBtn.addEventListener('click', () => {
        sendMessage(input.value);
        input.value = '';
    });

    // Model selector
    modelSelect.addEventListener('change', () => {
        currentModel = modelSelect.value;
        const label = MODELS.find(m => m.id === currentModel)?.label || currentModel;
        const statusModel = document.getElementById('orch-status-model');
        if (statusModel) statusModel.textContent = label;
    });

    // Clear chat
    clearBtn.addEventListener('click', () => {
        chatHistory = [];
        updateChatArea();
    });

    // ─── Initialize ─────────────────────────────────────────
    // Load file tree
    const treeRoot = document.getElementById('orch-file-tree')!;
    await renderFileTree(treeRoot, '/home/makaron8426/oikos/hegemonikon');

    // Load changes
    await loadChanges();
    updateRightPanel();
    updateChatArea();

    // Update status bar
    const statusChanges = document.getElementById('orch-status-changes');
    if (statusChanges) {
        statusChanges.textContent = `${changedFiles.length} files changed`;
    }
}
