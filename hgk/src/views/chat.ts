import './css/interactive.css';
/**
 * Chat View — Gemini API via Backend Proxy
 * HGK Desktop Chat UI: LLM との対話パネル
 * API calls go through mekhane.api (localhost:9696) for security.
 * Falls back to direct Gemini API if backend is unavailable.
 */

import { marked } from 'marked';

// ─── Types ───────────────────────────────────────────────────

interface ChatMessage {
    role: 'user' | 'model';
    content: string;
    timestamp: Date;
    model?: string;
}

interface GeminiContent {
    role: string;
    parts: { text: string }[];
}

interface GeminiResponse {
    candidates?: {
        content: {
            parts: { text: string }[];
            role: string;
        };
        finishReason: string;
    }[];
    error?: { message: string; code: number };
}

// ─── State ───────────────────────────────────────────────────

let messages: ChatMessage[] = [];
let currentModel = 'gemini-3-pro-preview';
let isStreaming = false;
let apiKey = '';
let systemInstruction = 'あなたは Hegemonikón の認知支援AIです。日本語で応答してください。簡潔かつ正確に。';

const MODELS: Record<string, string> = {
    'cortex-gemini': '🆓 Cortex Gemini (無課金 2MB)',
    'gemini-3-pro-preview': 'Gemini 3 Pro Preview',
    'gemini-3-flash-preview': 'Gemini 3 Flash Preview',
    'gemini-2.5-pro': 'Gemini 2.5 Pro',
    'gemini-2.5-flash': 'Gemini 2.5 Flash',
    'gemini-2.0-flash': 'Gemini 2.0 Flash',
};

const API_BACKEND = 'http://127.0.0.1:9696/api';
const API_GEMINI_DIRECT = 'https://generativelanguage.googleapis.com/v1beta/models';
let useBackend = true; // try backend first, fallback to direct

// ─── API ─────────────────────────────────────────────────────

async function loadApiKey(): Promise<string> {
    if (apiKey) return apiKey;
    // 1. Vite env variable (from .env.local)
    const envKey = (import.meta as unknown as { env?: Record<string, string> }).env?.VITE_GOOGLE_API_KEY;
    if (envKey) {
        apiKey = envKey;
        return apiKey;
    }
    // 2. localStorage
    const stored = localStorage.getItem('hgk-gemini-api-key');
    if (stored) {
        apiKey = stored;
        return apiKey;
    }
    // 3. Backend proxy (fallback)
    try {
        const res = await fetch('http://127.0.0.1:9696/api/config/gemini-key');
        if (res.ok) {
            const data = await res.json();
            if (data.key) {
                apiKey = data.key;
                localStorage.setItem('hgk-gemini-api-key', apiKey);
                return apiKey;
            }
        }
    } catch { /* silent */ }
    return '';
}

function buildContents(msgs: ChatMessage[]): GeminiContent[] {
    return msgs.map(m => ({
        role: m.role === 'user' ? 'user' : 'model',
        parts: [{ text: m.content }],
    }));
}

async function readSSEStream(
    response: Response,
    assistantMsg: ChatMessage,
): Promise<string> {
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullText = '';

    if (reader) {
        let buffer = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue;
                try {
                    const chunk: GeminiResponse = JSON.parse(jsonStr);
                    const text = chunk.candidates?.[0]?.content?.parts?.[0]?.text ?? '';
                    if (text) {
                        fullText += text;
                        assistantMsg.content = fullText;
                        const msgBodies = document.querySelectorAll('.chat-msg-body');
                        const lastBody = msgBodies[msgBodies.length - 1];
                        if (lastBody) {
                            lastBody.innerHTML = marked.parse(fullText) as string;
                            const container = document.getElementById('chat-messages');
                            if (container) container.scrollTop = container.scrollHeight;
                        }
                    }
                } catch { /* skip malformed chunk */ }
            }
        }
    }

    if (!fullText) {
        assistantMsg.content = '(応答なし)';
    }

    saveHistory();
    renderMessages();
    return fullText;
}

async function sendDirectFallback(
    assistantMsg: ChatMessage,
    contents: GeminiContent[],
    generationConfig: Record<string, unknown>,
    sysInstr?: { parts: { text: string }[] },
): Promise<string> {
    const key = await loadApiKey();
    if (!key) {
        messages.splice(-2, 2);
        throw new Error('API キーが設定されていません。バックエンドも利用不可。設定ボタンから入力してください。');
    }

    const url = `${API_GEMINI_DIRECT}/${currentModel}:streamGenerateContent?alt=sse&key=${key}`;
    const body: Record<string, unknown> = { contents, generationConfig };
    if (sysInstr) body.systemInstruction = sysInstr;

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const errText = await response.text();
        let errMsg = `API Error ${response.status}`;
        try {
            const errJson = JSON.parse(errText);
            errMsg = errJson.error?.message || errMsg;
        } catch { /* use default */ }
        messages.splice(-2, 2);
        throw new Error(errMsg);
    }

    return readSSEStream(response, assistantMsg);
}

async function sendToGemini(userMessage: string): Promise<string> {
    // Add user message
    messages.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
    });

    // Add placeholder assistant message for streaming
    const assistantMsg: ChatMessage = {
        role: 'model',
        content: '',
        timestamp: new Date(),
        model: currentModel,
    };
    messages.push(assistantMsg);
    renderMessages();

    const contents = buildContents(messages.slice(0, -1)); // exclude empty placeholder
    const generationConfig = { temperature: 0.7, maxOutputTokens: 8192 };
    const sysInstr = systemInstruction
        ? { parts: [{ text: systemInstruction }] }
        : undefined;

    let response: Response;

    if (useBackend) {
        // Backend proxy — API key managed server-side
        try {
            response = await fetch(`${API_BACKEND}/chat/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: currentModel,
                    contents,
                    generation_config: generationConfig,
                    system_instruction: sysInstr,
                }),
            });
        } catch {
            // Backend unreachable — fallback to direct
            console.warn('[Chat] Backend unreachable, falling back to direct API');
            useBackend = false;
            return sendDirectFallback(assistantMsg, contents, generationConfig, sysInstr);
        }
    } else {
        // Direct fallback
        return sendDirectFallback(assistantMsg, contents, generationConfig, sysInstr);
    }

    if (!response.ok) {
        const errText = await response.text();
        let errMsg = `API Error ${response.status}`;
        try {
            const errJson = JSON.parse(errText);
            errMsg = errJson.error?.message || errMsg;
        } catch { /* use default */ }
        // Remove user + placeholder messages on failure
        messages.splice(-2, 2);
        throw new Error(errMsg);
    }

    return readSSEStream(response, assistantMsg);
}

// ─── Rendering ───────────────────────────────────────────────

function esc(s: string): string {
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function formatTime(d: Date): string {
    return d.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
}

function renderMessage(msg: ChatMessage, index: number): string {
    const isUser = msg.role === 'user';
    const rendered = isUser ? esc(msg.content) : (marked.parse(msg.content) as string);
    const modelTag = msg.model ? `<span class="chat-model-tag">${esc(MODELS[msg.model] || msg.model)}</span>` : '';

    return `
    <div class="chat-msg ${isUser ? 'chat-msg-user' : 'chat-msg-assistant'}" data-idx="${index}">
      <div class="chat-msg-header">
        <span class="chat-msg-role">${isUser ? '👤 You' : '🤖 AI'}</span>
        ${modelTag}
        <span class="chat-msg-time">${formatTime(msg.timestamp)}</span>
        <button class="chat-msg-delete" title="削除" data-idx="${index}">✕</button>
      </div>
      <div class="chat-msg-body">${rendered}</div>
    </div>
  `;
}

function renderMessages(): void {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    if (messages.length === 0) {
        container.innerHTML = `
      <div class="chat-empty">
        <div class="chat-empty-icon">💬</div>
        <div class="chat-empty-title">Hegemonikón Chat</div>
        <div class="chat-empty-subtitle">Gemini と対話を始めましょう</div>
        <div class="chat-empty-hints">
          <span class="chat-hint">HGK の現在の方向性は？</span>
          <span class="chat-hint">FEP を簡単に説明して</span>
          <span class="chat-hint">CCL の @helm を解説</span>
        </div>
      </div>
    `;
        return;
    }

    container.innerHTML = messages.map((m, i) => renderMessage(m, i)).join('');
    container.scrollTop = container.scrollHeight;

    // F7: Bind delete buttons
    container.querySelectorAll('.chat-msg-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const idx = parseInt((btn as HTMLElement).dataset.idx ?? '-1', 10);
            if (idx >= 0 && idx < messages.length) {
                messages.splice(idx, 1);
                saveHistory();
                renderMessages();
            }
        });
    });

    // Bind hint chip clicks
    container.querySelectorAll('.chat-hint').forEach(chip => {
        chip.addEventListener('click', () => {
            const input = document.getElementById('chat-input') as HTMLTextAreaElement | null;
            if (input && !isStreaming) {
                input.value = chip.textContent ?? '';
                void handleSend();
            }
        });
    });

    // F6: Add copy buttons to code blocks
    addCopyButtons(container);
}

function addCopyButtons(container: HTMLElement): void {
    container.querySelectorAll('pre').forEach(pre => {
        if (pre.querySelector('.code-copy-btn')) return; // already has button
        const btn = document.createElement('button');
        btn.className = 'code-copy-btn';
        btn.textContent = '📋';
        btn.title = 'コピー';
        btn.addEventListener('click', () => {
            const code = pre.querySelector('code')?.textContent ?? pre.textContent ?? '';
            void navigator.clipboard.writeText(code).then(() => {
                btn.textContent = '✓';
                setTimeout(() => { btn.textContent = '📋'; }, 1500);
            });
        });
        pre.style.position = 'relative';
        pre.appendChild(btn);
    });
}

// F4: Persistence
function saveHistory(): void {
    try {
        const data = messages.map(m => ({
            ...m,
            timestamp: m.timestamp.toISOString(),
        }));
        localStorage.setItem('hgk-chat-history', JSON.stringify(data));
    } catch { /* quota exceeded — silent */ }
}

function loadHistory(): void {
    try {
        const raw = localStorage.getItem('hgk-chat-history');
        if (!raw) return;
        const data = JSON.parse(raw) as Array<ChatMessage & { timestamp: string }>;
        messages = data.map(m => ({
            ...m,
            timestamp: new Date(m.timestamp),
        }));
    } catch { /* corrupt data — silent */ }
}

function setLoading(loading: boolean): void {
    isStreaming = loading;
    const btn = document.getElementById('chat-send-btn') as HTMLButtonElement | null;
    const input = document.getElementById('chat-input') as HTMLTextAreaElement | null;
    if (btn) {
        btn.disabled = loading;
        btn.textContent = loading ? '⏳' : '送信';
    }
    if (input) {
        input.disabled = loading;
    }

    // Show/hide typing indicator
    const indicator = document.getElementById('chat-typing');
    if (indicator) {
        indicator.style.display = loading ? 'flex' : 'none';
    }
}

// ─── Event Handlers ──────────────────────────────────────────

async function handleSend(retryText?: string): Promise<void> {
    const input = document.getElementById('chat-input') as HTMLTextAreaElement | null;
    const text = retryText ?? input?.value.trim() ?? '';
    if (!text || isStreaming) return;

    if (input && !retryText) {
        input.value = '';
        input.style.height = 'auto';
    }
    setLoading(true);

    try {
        await sendToGemini(text);
    } catch (err) {
        const messagesDiv = document.getElementById('chat-messages');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-msg chat-msg-error';
        const errMsg = esc((err as Error).message);
        errorDiv.innerHTML = `
            <div class="chat-msg-body">⚠️ ${errMsg}</div>
            <button class="btn btn-sm btn-outline chat-retry-btn" style="margin-top:0.5rem;">🔄 再送</button>
        `;
        messagesDiv?.appendChild(errorDiv);
        // F5: retry button
        errorDiv.querySelector('.chat-retry-btn')?.addEventListener('click', () => {
            errorDiv.remove();
            void handleSend(text);
        });
        if (messagesDiv) messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } finally {
        setLoading(false);
    }
}

function handleKeyDown(e: KeyboardEvent): void {
    // Enter to send, Shift+Enter for newline
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        void handleSend();
    }
}

function autoResize(textarea: HTMLTextAreaElement): void {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
}

function showApiKeyDialog(): void {
    const existing = document.getElementById('chat-apikey-dialog');
    if (existing) existing.remove();

    const dialog = document.createElement('div');
    dialog.id = 'chat-apikey-dialog';
    dialog.className = 'chat-dialog-overlay';
    dialog.innerHTML = `
    <div class="chat-dialog">
      <h3>⚙️ Chat 設定</h3>
      <label style="color: var(--text-secondary); font-size: 0.85rem; display:block; margin-bottom:0.25rem;">🔑 Gemini API キー</label>
      <input type="password" id="apikey-input" class="input" 
        placeholder="AIzaSy..." value="${esc(apiKey)}" 
        style="width: 100%; margin-bottom: 0.75rem;" />
      <label style="color: var(--text-secondary); font-size: 0.85rem; display:block; margin-bottom:0.25rem;">📝 システムプロンプト</label>
      <textarea id="sysprompt-input" class="input" rows="4"
        style="width: 100%; resize: vertical; margin-bottom: 0.75rem; font-family: inherit;">${esc(systemInstruction)}</textarea>
      <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
        <button id="apikey-cancel" class="btn btn-outline">キャンセル</button>
        <button id="apikey-save" class="btn">保存</button>
      </div>
    </div>
  `;
    document.body.appendChild(dialog);

    document.getElementById('apikey-cancel')?.addEventListener('click', () => dialog.remove());
    document.getElementById('apikey-save')?.addEventListener('click', () => {
        const input = document.getElementById('apikey-input') as HTMLInputElement;
        const sysInput = document.getElementById('sysprompt-input') as HTMLTextAreaElement;
        const key = input.value.trim();
        if (key) {
            apiKey = key;
            localStorage.setItem('hgk-gemini-api-key', key);
        }
        systemInstruction = sysInput.value;
        localStorage.setItem('hgk-chat-sysprompt', systemInstruction);
        dialog.remove();
        updateConnectionStatus(!!apiKey);
    });

    (document.getElementById('apikey-input') as HTMLInputElement)?.focus();
}

function updateConnectionStatus(connected: boolean): void {
    const statusEl = document.getElementById('chat-status');
    if (!statusEl) return;
    statusEl.innerHTML = connected
        ? `<span class="status-dot ok"></span> ${esc(MODELS[currentModel] || currentModel)}`
        : '<span class="status-dot error"></span> 未接続';
}

function handleClear(): void {
    messages = [];
    localStorage.removeItem('hgk-chat-history');
    renderMessages();
}

// ─── Main View ───────────────────────────────────────────────

export async function renderChatView(): Promise<void> {
    const app = document.getElementById('view-content');
    if (!app) return;

    // Load API key, history, and system prompt
    await loadApiKey();
    if (messages.length === 0) loadHistory();
    const savedSysPrompt = localStorage.getItem('hgk-chat-sysprompt');
    if (savedSysPrompt !== null) systemInstruction = savedSysPrompt;

    const modelOptions = Object.entries(MODELS)
        .map(([id, name]) => `<option value="${id}" ${id === currentModel ? 'selected' : ''}>${esc(name)}</option>`)
        .join('');

    app.innerHTML = `
    <div class="chat-container">
      <div class="chat-header">
        <div class="chat-header-left">
          <h1 style="margin:0; font-size:1.2rem;">💬 Chat</h1>
          <span id="chat-status" class="chat-status">
            ${apiKey
            ? `<span class="status-dot ok"></span> ${esc(MODELS[currentModel] || currentModel)}`
            : '<span class="status-dot error"></span> 未接続'}
          </span>
        </div>
        <div class="chat-header-right">
          <select id="chat-model-select" class="input chat-model-select">
            ${modelOptions}
          </select>
          <button id="chat-settings-btn" class="btn btn-sm btn-outline" title="API キー設定">⚙️</button>
          <button id="chat-clear-btn" class="btn btn-sm btn-outline" title="履歴クリア">🗑️</button>
        </div>
      </div>

      <div id="chat-messages" class="chat-messages"></div>

      <div id="chat-typing" class="chat-typing" style="display:none;">
        <div class="chat-typing-dots">
          <span></span><span></span><span></span>
        </div>
        <span>応答を生成中...</span>
      </div>

      <div class="chat-input-area">
        <textarea id="chat-input" class="input chat-textarea" 
          placeholder="メッセージを入力... (Enter で送信、Shift+Enter で改行)"
          rows="1"></textarea>
        <button id="chat-send-btn" class="btn chat-send-btn">送信</button>
      </div>
    </div>
  `;

    // Render initial state
    renderMessages();

    // Event bindings
    const input = document.getElementById('chat-input') as HTMLTextAreaElement;
    const sendBtn = document.getElementById('chat-send-btn')!;
    const modelSelect = document.getElementById('chat-model-select') as HTMLSelectElement;
    const settingsBtn = document.getElementById('chat-settings-btn')!;
    const clearBtn = document.getElementById('chat-clear-btn')!;

    input.addEventListener('keydown', handleKeyDown);
    input.addEventListener('input', () => autoResize(input));
    sendBtn.addEventListener('click', () => void handleSend());
    settingsBtn.addEventListener('click', showApiKeyDialog);
    clearBtn.addEventListener('click', handleClear);

    modelSelect.addEventListener('change', () => {
        currentModel = modelSelect.value;
        updateConnectionStatus(!!apiKey);
    });

    // Focus input
    input.focus();
}
