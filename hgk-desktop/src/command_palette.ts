/**
 * CCL Command Palette — Ctrl+K で起動するコマンドパレット
 *
 * kalon: ワークフローと CCL 式を「問い」のように手元に呼ぶ
 *
 * 機能:
 *   - Ctrl+K / Cmd+K でオーバーレイ表示
 *   - WF 名でフィルター打鍵 → 候補表示
 *   - CCL 式 (/ で始まる) を直接入力 → parse → 結果表示
 *   - Enter で WF 詳細 or CCL 実行
 */

import { api } from './api/client';
import type { WFSummary, CCLParseResponse } from './api/client';

// --- State ---

let paletteEl: HTMLElement | null = null;
let isOpen = false;
let wfCache: WFSummary[] = [];

// --- HTML ---

function createPaletteHTML(): string {
    return `
    <div class="cp-overlay" id="cp-overlay">
      <div class="cp-dialog">
        <div class="cp-input-wrapper">
          <span class="cp-icon">⌘</span>
          <input type="text" id="cp-input" class="cp-input" placeholder="Type a workflow name or CCL expression..." autocomplete="off" />
          <kbd class="cp-kbd">ESC</kbd>
        </div>
        <div class="cp-results" id="cp-results"></div>
        <div class="cp-footer">
          <span>↑↓ Navigate</span>
          <span>↵ Execute</span>
          <span>ESC Close</span>
        </div>
      </div>
    </div>
  `;
}

// --- Rendering ---

function renderWFItems(items: WFSummary[]): string {
    if (items.length === 0) {
        return '<div class="cp-empty">No matching workflows</div>';
    }
    return items.map((wf, i) => `
    <div class="cp-item ${i === 0 ? 'cp-item-active' : ''}" data-idx="${i}" data-name="${esc(wf.name)}" data-ccl="${esc(wf.ccl)}">
      <div class="cp-item-header">
        <span class="cp-item-name">/${esc(wf.name)}</span>
        ${wf.ccl ? `<span class="cp-item-ccl">${esc(wf.ccl)}</span>` : ''}
      </div>
      <div class="cp-item-desc">${esc(wf.description)}</div>
      ${wf.modes.length > 0 ? `<div class="cp-item-modes">${wf.modes.map(m => `<span class="cp-mode-tag">${esc(m)}</span>`).join('')}</div>` : ''}
    </div>
  `).join('');
}

function renderParseResult(res: CCLParseResponse): string {
    if (!res.success) {
        return `<div class="cp-parse-error">❌ ${esc(res.error ?? 'Parse failed')}</div>`;
    }
    return `
    <div class="cp-parse-result">
      <div class="cp-parse-header">✅ Parsed: <code>${esc(res.ccl)}</code></div>
      ${res.tree ? `<pre class="cp-parse-tree">${esc(res.tree)}</pre>` : ''}
      ${res.workflows.length > 0 ? `
        <div class="cp-parse-wfs">
          <strong>Workflows:</strong> ${res.workflows.map(w => `<span class="cp-mode-tag">${esc(w)}</span>`).join(' ')}
        </div>
      ` : ''}
      ${res.plan_template ? `<pre class="cp-parse-plan">${esc(res.plan_template)}</pre>` : ''}
    </div>
  `;
}

// --- Logic ---

function esc(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

async function loadWorkflows(): Promise<void> {
    if (wfCache.length > 0) return;
    try {
        const res = await api.wfList();
        wfCache = res.workflows;
    } catch {
        wfCache = [];
    }
}

function filterWorkflows(query: string): WFSummary[] {
    const q = query.toLowerCase().replace(/^\//, '');
    if (!q) return wfCache.slice(0, 15);
    return wfCache.filter(wf =>
        wf.name.toLowerCase().includes(q) ||
        wf.description.toLowerCase().includes(q) ||
        wf.ccl.toLowerCase().includes(q)
    ).slice(0, 15);
}

let activeIdx = 0;

function updateActive(resultsEl: HTMLElement, delta: number): void {
    const items = resultsEl.querySelectorAll('.cp-item');
    if (items.length === 0) return;
    items[activeIdx]?.classList.remove('cp-item-active');
    activeIdx = Math.max(0, Math.min(items.length - 1, activeIdx + delta));
    items[activeIdx]?.classList.add('cp-item-active');
    (items[activeIdx] as HTMLElement)?.scrollIntoView({ block: 'nearest' });
}

async function handleInput(input: HTMLInputElement, resultsEl: HTMLElement): Promise<void> {
    const val = input.value.trim();

    // CCL expression (contains operators like +, >>, ~, etc.)
    if (val && /[+>~{(\\]/.test(val)) {
        resultsEl.innerHTML = '<div class="cp-loading">Parsing CCL...</div>';
        try {
            const res: CCLParseResponse = await api.cclParse(val);
            resultsEl.innerHTML = renderParseResult(res);
        } catch (e) {
            resultsEl.innerHTML = `<div class="cp-parse-error">❌ ${esc((e as Error).message)}</div>`;
        }
        return;
    }

    // Workflow filter
    const filtered = filterWorkflows(val);
    activeIdx = 0;
    resultsEl.innerHTML = renderWFItems(filtered);

    // Click handlers
    resultsEl.querySelectorAll('.cp-item').forEach(item => {
        item.addEventListener('click', () => {
            const name = (item as HTMLElement).dataset.name ?? '';
            selectWorkflow(name, resultsEl);
        });
    });
}

async function selectWorkflow(name: string, resultsEl: HTMLElement): Promise<void> {
    resultsEl.innerHTML = '<div class="cp-loading">Loading workflow...</div>';
    try {
        const detail = await api.wfDetail(name);
        resultsEl.innerHTML = `
      <div class="cp-wf-detail">
        <h3>/${esc(detail.name)}</h3>
        <p>${esc(detail.description)}</p>
        ${detail.ccl ? `<div class="cp-wf-ccl"><strong>CCL:</strong> <code>${esc(detail.ccl)}</code></div>` : ''}
        ${detail.modes.length > 0 ? `<div class="cp-wf-modes"><strong>Modes:</strong> ${detail.modes.map(m => `<span class="cp-mode-tag">${esc(m)}</span>`).join(' ')}</div>` : ''}
        ${detail.stages.length > 0 ? `
          <div class="cp-wf-stages">
            <strong>Stages:</strong>
            <ol>${detail.stages.map(s => `<li>${esc(s.name || s.description || '')}</li>`).join('')}</ol>
          </div>
        ` : ''}
      </div>
    `;
    } catch (e) {
        resultsEl.innerHTML = `<div class="cp-parse-error">❌ ${esc((e as Error).message)}</div>`;
    }
}

// --- Open / Close ---

export function openPalette(): void {
    if (isOpen) return;
    isOpen = true;

    // Inject HTML
    const container = document.createElement('div');
    container.innerHTML = createPaletteHTML();
    paletteEl = container.firstElementChild as HTMLElement;
    document.body.appendChild(paletteEl);

    const input = document.getElementById('cp-input') as HTMLInputElement;
    const resultsEl = document.getElementById('cp-results')!;
    const overlay = document.getElementById('cp-overlay')!;

    // Load WFs and show initial list
    void loadWorkflows().then(() => {
        void handleInput(input, resultsEl);
    });

    // Input handler (debounced)
    let debounceTimer: ReturnType<typeof setTimeout> | null = null;
    input.addEventListener('input', () => {
        if (debounceTimer) clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => void handleInput(input, resultsEl), 150);
    });

    // Keyboard navigation
    input.addEventListener('keydown', (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            closePalette();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            updateActive(resultsEl, 1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            updateActive(resultsEl, -1);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const activeItem = resultsEl.querySelector('.cp-item-active') as HTMLElement;
            if (activeItem) {
                const name = activeItem.dataset.name ?? '';
                void selectWorkflow(name, resultsEl);
            }
        }
    });

    // Click outside to close
    overlay.addEventListener('click', (e: MouseEvent) => {
        if (e.target === overlay) closePalette();
    });

    // Focus input
    requestAnimationFrame(() => input.focus());
}

export function closePalette(): void {
    if (!isOpen || !paletteEl) return;
    isOpen = false;
    paletteEl.remove();
    paletteEl = null;
    activeIdx = 0;
}

export function togglePalette(): void {
    isOpen ? closePalette() : openPalette();
}

// --- Global Keyboard Shortcut ---

export function initCommandPalette(): void {
    document.addEventListener('keydown', (e: KeyboardEvent) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            togglePalette();
        }
    });
}
