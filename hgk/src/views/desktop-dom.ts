import './css/desktop-dom.css';
// Desktop DOM View — AT-SPI2 Accessibility Tree Browser
// Displays desktop applications and their accessible element trees

import { invoke } from '@tauri-apps/api/core';
import { executeCCL } from '../desktop-ccl';

interface DesktopElement {
    app_name: string;
    role: string;
    name: string;
    route: string;
    bus_name?: string;
    object_path?: string;
    child_count: number;
    recommended_route: string;
}

interface A11yNode {
    name: string;
    role: string;
    path: string;
    children: A11yNode[];
}

interface FoundElement {
    name: string;
    role: string;
    path: string;
    bus_name: string;
    x: number;
    y: number;
    width: number;
    height: number;
}

export async function renderDesktopDomView(): Promise<void> {
    const app = document.getElementById('view-content');
    if (!app) return;

    app.innerHTML = `
    <div class="dd-container">
      <div class="section-header">
        <h2>🖥️ Desktop DOM</h2>
        <p class="section-subtitle">AT-SPI2 アクセシビリティツリー ブラウザ</p>
      </div>

      <div class="dd-toolbar">
        <button class="btn btn-primary" id="dd-refresh">🔄 リフレッシュ</button>
        <div class="dd-search">
          <input type="text" id="dd-search-role" placeholder="Role フィルタ (例: button)" class="input-field" />
          <input type="text" id="dd-search-name" placeholder="Name フィルタ (例: 保存)" class="input-field" />
          <button class="btn btn-secondary" id="dd-search-btn">🔍 検索</button>
        </div>
      </div>

      <div class="dd-layout">
        <div class="dd-panel dd-apps" id="dd-apps">
          <h3>📱 アプリケーション一覧</h3>
          <div id="dd-app-list" class="dd-list">読み込み中...</div>
        </div>
        <div class="dd-panel dd-tree" id="dd-tree">
          <h3>🌳 要素ツリー</h3>
          <div id="dd-tree-content" class="dd-tree-view">アプリを選択してください</div>
        </div>
        <div class="dd-panel dd-detail" id="dd-detail">
          <h3>📋 要素詳細</h3>
          <div id="dd-detail-content">要素を選択してください</div>
        </div>
      </div>

      </div>

      <div class="dd-panel dd-search-results" id="dd-search-results" style="display:none">
        <h3>🔍 検索結果</h3>
        <div id="dd-search-result-list"></div>
      </div>

      <div class="dd-panel dd-ccl-console">
        <h3>⚡ CCL コンソール</h3>
        <div class="dd-ccl-input">
          <input type="text" id="dd-ccl-expr" placeholder='@desktop{list} / @desktop{find, role="button"}' class="input-field" />
          <button class="btn btn-primary btn-sm" id="dd-ccl-run">▶ 実行</button>
        </div>
        <pre id="dd-ccl-output" class="dd-ccl-result">結果がここに表示されます</pre>
      </div>
    </div>
  `;

    // Load apps
    await loadApps();

    // Refresh button
    document.getElementById('dd-refresh')?.addEventListener('click', loadApps);

    // Search button
    document.getElementById('dd-search-btn')?.addEventListener('click', searchElements);

    // CCL console
    const cclRun = document.getElementById('dd-ccl-run');
    const cclInput = document.getElementById('dd-ccl-expr') as HTMLInputElement;
    const cclOutput = document.getElementById('dd-ccl-output');
    if (cclRun && cclInput && cclOutput) {
        cclRun.addEventListener('click', async () => {
            const expr = cclInput.value.trim();
            if (!expr) return;
            cclOutput.textContent = '実行中...';
            const result = await executeCCL(expr);
            cclOutput.textContent = JSON.stringify(result, null, 2);
            cclOutput.className = `dd-ccl-result ${result.success ? 'dd-ccl-ok' : 'dd-ccl-err'}`;
        });
        cclInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') cclRun.click();
        });
    }
}

async function loadApps(): Promise<void> {
    const list = document.getElementById('dd-app-list');
    if (!list) return;

    try {
        const elements: DesktopElement[] = await invoke('list_desktop');
        list.innerHTML = elements
            .sort((a, b) => b.child_count - a.child_count)
            .map(el => `
        <div class="dd-app-item ${el.child_count > 0 ? 'dd-app-active' : 'dd-app-empty'}"
             data-bus="${el.bus_name || ''}" data-path="${el.object_path || ''}">
          <span class="dd-app-name">${escHtml(el.app_name)}</span>
          <span class="dd-app-meta">
            <span class="dd-route-badge dd-route-${el.recommended_route.toLowerCase()}">${el.recommended_route}</span>
            <span class="dd-child-count">${el.child_count} 子</span>
          </span>
        </div>
      `).join('');

        // Click handlers
        list.querySelectorAll('.dd-app-item').forEach(item => {
            item.addEventListener('click', () => {
                const bus = item.getAttribute('data-bus') || '';
                const path = item.getAttribute('data-path') || '';
                if (bus && path) {
                    list.querySelectorAll('.dd-app-item').forEach(i => i.classList.remove('selected'));
                    item.classList.add('selected');
                    void loadTree(bus, path);
                }
            });
        });
    } catch (e) {
        list.innerHTML = `<div class="dd-error">❌ AT-SPI2 接続エラー: ${escHtml(String(e))}</div>`;
    }
}

async function loadTree(busName: string, objectPath: string): Promise<void> {
    const content = document.getElementById('dd-tree-content');
    if (!content) return;
    content.innerHTML = '読み込み中...';

    try {
        const nodes: A11yNode[] = await invoke('get_element_tree', {
            busName, path: objectPath, maxDepth: 4
        });
        content.innerHTML = renderTreeNodes(nodes, busName, 0);

        // Click handlers for tree nodes
        content.querySelectorAll('.dd-node').forEach(node => {
            node.addEventListener('click', (e) => {
                e.stopPropagation();
                const bus = node.getAttribute('data-bus') || '';
                const path = node.getAttribute('data-path') || '';
                const name = node.getAttribute('data-name') || '';
                const role = node.getAttribute('data-role') || '';
                content.querySelectorAll('.dd-node').forEach(n => n.classList.remove('selected'));
                node.classList.add('selected');
                void showDetail(bus, path, name, role);
            });
        });
    } catch (e) {
        content.innerHTML = `<div class="dd-error">❌ ツリー取得エラー: ${escHtml(String(e))}</div>`;
    }
}

function renderTreeNodes(nodes: A11yNode[], busName: string, depth: number): string {
    return nodes.map(n => {
        const indent = depth * 16;
        const hasChildren = n.children.length > 0;
        const label = n.name || `(${n.role})`;
        const roleClass = getRoleClass(n.role);

        return `
      <div class="dd-node ${roleClass}" style="padding-left: ${indent}px"
           data-bus="${busName}" data-path="${n.path}"
           data-name="${escAttr(n.name)}" data-role="${escAttr(n.role)}">
        <span class="dd-node-icon">${getRoleIcon(n.role)}</span>
        <span class="dd-node-label">${escHtml(label)}</span>
        <span class="dd-node-role">${escHtml(n.role)}</span>
      </div>
      ${hasChildren ? renderTreeNodes(n.children, busName, depth + 1) : ''}
    `;
    }).join('');
}

async function showDetail(busName: string, path: string, name: string, role: string): Promise<void> {
    const detail = document.getElementById('dd-detail-content');
    if (!detail) return;

    detail.innerHTML = `
    <div class="dd-detail-info">
      <div class="dd-detail-row"><strong>名前:</strong> ${escHtml(name || '(なし)')}</div>
      <div class="dd-detail-row"><strong>ロール:</strong> ${escHtml(role)}</div>
      <div class="dd-detail-row"><strong>パス:</strong> <code>${escHtml(path)}</code></div>
      <div class="dd-detail-row"><strong>バス:</strong> <code>${escHtml(busName)}</code></div>
      <div class="dd-detail-row" id="dd-extents">📐 座標取得中...</div>
      <div class="dd-detail-row" id="dd-actions">⚡ アクション取得中...</div>
    </div>
    <div class="dd-detail-buttons">
      <button class="btn btn-primary btn-sm" id="dd-btn-click">🎯 クリック</button>
      <button class="btn btn-secondary btn-sm" id="dd-btn-focus">🔍 フォーカス</button>
    </div>
  `;

    // Get extents
    try {
        const ext: { x: number; y: number; width: number; height: number } = await invoke('desktop_get_extents', {
            busName, objectPath: path
        });
        const extDiv = document.getElementById('dd-extents');
        if (extDiv) {
            extDiv.innerHTML = `📐 <strong>位置:</strong> (${ext.x}, ${ext.y}) サイズ: ${ext.width}×${ext.height}`;
        }
    } catch { /* silent */ }

    // Get actions
    try {
        const actions: string[] = await invoke('desktop_list_actions', {
            busName, objectPath: path
        });
        const actDiv = document.getElementById('dd-actions');
        if (actDiv) {
            actDiv.innerHTML = actions.length > 0
                ? `⚡ <strong>アクション:</strong> ${actions.map(a => `<span class="dd-action-badge">${escHtml(a)}</span>`).join(' ')}`
                : '⚡ アクションなし';
        }
    } catch { /* silent */ }

    // Click button — uses xdotool via click_at_element
    document.getElementById('dd-btn-click')?.addEventListener('click', async () => {
        try {
            await invoke('desktop_click', {
                busName, objectPath: path, x: null, y: null
            });
        } catch (e) {
            console.warn('Click failed:', e);
        }
    });

    // Focus button
    document.getElementById('dd-btn-focus')?.addEventListener('click', async () => {
        try {
            await invoke('desktop_focus', { busName, objectPath: path });
        } catch (e) {
            console.warn('Focus failed:', e);
        }
    });
}

async function searchElements(): Promise<void> {
    const roleInput = document.getElementById('dd-search-role') as HTMLInputElement;
    const nameInput = document.getElementById('dd-search-name') as HTMLInputElement;
    const resultsDiv = document.getElementById('dd-search-results');
    const resultList = document.getElementById('dd-search-result-list');
    if (!resultsDiv || !resultList) return;

    const selectedApp = document.querySelector('.dd-app-item.selected');
    if (!selectedApp) {
        resultList.innerHTML = '<div class="dd-error">先にアプリを選択してください</div>';
        resultsDiv.style.display = 'block';
        return;
    }

    const busName = selectedApp.getAttribute('data-bus') || '';
    const objectPath = selectedApp.getAttribute('data-path') || '';
    const role = roleInput.value.trim() || undefined;
    const name = nameInput.value.trim() || undefined;

    resultList.innerHTML = '検索中...';
    resultsDiv.style.display = 'block';

    try {
        const results: FoundElement[] = await invoke('desktop_find_elements', {
            busName, objectPath, role: role || null, name: name || null, maxDepth: 4
        });

        resultList.innerHTML = results.length === 0
            ? '<div class="dd-empty">該当なし</div>'
            : results.map(el => `
        <div class="dd-search-item">
          <span class="dd-node-icon">${getRoleIcon(el.role)}</span>
          <span class="dd-node-label">${escHtml(el.name || '(無名)')}</span>
          <span class="dd-node-role">${escHtml(el.role)}</span>
          <span class="dd-coords">${el.width > 0 ? `(${el.x},${el.y}) ${el.width}×${el.height}` : '不可視'}</span>
        </div>
      `).join('');
    } catch (e) {
        resultList.innerHTML = `<div class="dd-error">❌ 検索エラー: ${escHtml(String(e))}</div>`;
    }
}

function getRoleIcon(role: string): string {
    const icons: Record<string, string> = {
        'application': '📱', 'frame': '🪟', 'panel': '📦',
        'push button': '🔘', 'toggle button': '🔁', 'button': '🔘',
        'text': '📝', 'entry': '✏️', 'label': '🏷️',
        'menu': '📋', 'menu item': '📌', 'menu bar': '📋',
        'check box': '☑️', 'radio button': '🔘',
        'list': '📜', 'list item': '📌', 'tree': '🌳',
        'tab': '📑', 'table': '📊', 'heading': '📰',
        'scroll bar': '📏', 'separator': '➖',
        'image': '🖼️', 'icon': '🎭',
    };
    return icons[role.toLowerCase()] || '▪️';
}

function getRoleClass(role: string): string {
    if (['push button', 'toggle button', 'button'].includes(role.toLowerCase())) return 'dd-role-button';
    if (['text', 'entry', 'paragraph'].includes(role.toLowerCase())) return 'dd-role-text';
    if (['frame', 'window', 'dialog'].includes(role.toLowerCase())) return 'dd-role-frame';
    if (['panel', 'filler', 'section'].includes(role.toLowerCase())) return 'dd-role-panel';
    return '';
}

function escHtml(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function escAttr(s: string): string {
    return s.replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;');
}
