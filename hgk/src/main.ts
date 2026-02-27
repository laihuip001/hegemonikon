import { ROUTES, ROUTE_MAP, DEFAULT_ROUTE } from './route-config';
import { api } from './api/client';
import { recordView } from './telemetry';
import { initCommandPalette, setNavigateCallback } from './command_palette';
import { clearPolling, setCurrentRoute, getCurrentRoute, skeletonHTML, esc } from './utils';
import './styles.css';

// ─── Bootstrap ───────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  buildIconRail();
  buildTabNav();
  setupNavigation();
  setupSlidePanel();
  navigate(DEFAULT_ROUTE);
  // Start global badge polling
  void updateNotifBadge();
  setInterval(() => { void updateNotifBadge(); }, 60_000);
  // PKS auto-push on startup (fire-and-forget)
  void api.pksTriggerPush().catch(() => { /* silent */ });
  // CCL Command Palette — Ctrl+K
  initCommandPalette();
  setNavigateCallback(navigate);
  initKeyboardNav();
  initThemeToggle();
});

// ─── U1: Icon Rail (左端アイコンバー) ────────────────────────

// MECE 再設計 — HGK 認知フロー型 (η→K→Δ→ε→Ω)
// 軸: 対話(入力) → 知識(記憶) → 判断(処理) → 実行(出力) → 状態(管理)
const ICON_GROUPS = [
  {
    id: 'dialogue',
    icon: 'η',          // eta: 自然変換の単位 = 入力・対話の始点
    label: '対話',
    routes: ['orchestrator', 'chat', 'agents'],
    desc: 'AI との対話・指揮・エージェント操作 (入力層)',
  },
  {
    id: 'knowledge',
    icon: 'K',           // K-series (Kairos): 知識・文脈
    label: '知識',
    routes: ['search', 'gnosis', 'sophia', 'digestor', 'fep'],
    desc: '知識検索・論文・KI・消化・FEP理論 (記憶層)',
  },
  {
    id: 'judgement',
    icon: 'Δ',           // Delta-layer: 判断・批評
    label: '判断',
    routes: ['quality', 'postcheck', 'synteleia', 'synedrion', 'aristos'],
    desc: '品質検証・監査・判定 (処理層)',
  },
  {
    id: 'output',
    icon: 'ε',           // epsilon: 余単位 = 射出・具現化
    label: '可視化',
    routes: ['dashboard', 'graph', 'timeline'],
    desc: 'ダッシュボード・グラフ・タイムライン (出力層)',
  },
  {
    id: 'system',
    icon: 'Ω',           // Omega-layer: 全体統御
    label: '運用',
    routes: ['notifications', 'pks', 'devtools', 'desktop', 'settings'],
    desc: '通知・インフラ・DevTools・設定 (管理層)',
  },
];

let activeGroup = 'dialogue';
let expandedGroup: string | null = 'dialogue'; // Obsidian style
let isTabNavOpen = true; // Tab nav toggle

function buildIconRail(): void {
  const rail = document.getElementById('icon-rail');
  if (!rail) return;

  let html = '';
  for (const g of ICON_GROUPS) {
    const isActive = g.id === activeGroup;
    const isExpanded = g.id === expandedGroup;

    // Group icon button
    html += `<button class="rail-btn ${isActive ? 'active' : ''}" data-group="${g.id}" title="${g.label}: ${g.desc}" aria-label="${g.label}">
      <span class="rail-icon">${g.icon}</span>
    </button>`;

    // Obsidian-style: expanded sub-items below icon
    if (isExpanded) {
      html += `<div class="rail-sub-items">`;
      for (const rKey of g.routes) {
        const route = ROUTES.find(r => r.key === rKey);
        if (!route) continue;
        const isCurrent = rKey === getCurrentRoute();
        html += `<button class="rail-sub-btn ${isCurrent ? 'active' : ''}" data-route="${route.key}" title="${route.label}" aria-label="${route.label}">
          <span class="rail-sub-icon">${route.icon}</span>
        </button>`;
      }
      html += `</div>`;
    }
  }

  // Tab nav toggle at bottom
  html += `<div class="rail-spacer"></div>`;
  html += `<button class="rail-btn rail-toggle" title="${isTabNavOpen ? 'タブを閉じる' : 'タブを開く'}" aria-label="${isTabNavOpen ? 'タブを閉じる' : 'タブを開く'}">
    <span class="rail-icon">${isTabNavOpen ? '◀' : '▶'}</span>
  </button>`;

  rail.innerHTML = html;
}

// ─── U2: Vertical Tab Nav (縦タブ) ──────────────────────────

function buildTabNav(): void {
  const nav = document.getElementById('tab-nav');
  if (!nav) return;

  // Toggle visibility
  nav.classList.toggle('collapsed', !isTabNavOpen);
  // Update grid
  const app = document.getElementById('app');
  if (app) {
    app.style.gridTemplateColumns = isTabNavOpen ? '48px 180px 1fr' : '48px 1fr';
  }

  if (!isTabNavOpen) {
    nav.innerHTML = '';
    return;
  }

  const group = ICON_GROUPS.find(g => g.id === activeGroup);
  if (!group) return;

  const tabs = group.routes.map(rKey => {
    const route = ROUTES.find(r => r.key === rKey);
    if (!route) return '';
    const isCurrent = rKey === getCurrentRoute();
    return `<button class="tab-btn ${isCurrent ? 'active' : ''}" data-route="${route.key}" aria-label="${route.label}">
      <span class="tab-icon">${route.icon}</span>
      <span class="tab-label">${route.label}</span>
    </button>`;
  }).join('');

  nav.innerHTML = `
    <h2 class="nav-brand">⬡ Hegemonikón</h2>
    <div class="tab-group-label">${group.icon} ${group.label}</div>
    ${tabs}
  `;
}

// ─── U3: Assistant Panel ────────────────────────────────────

function setupSlidePanel(): void {
  const trigger = document.getElementById('slide-trigger');
  const panel = document.getElementById('slide-panel');
  const closeBtn = document.getElementById('slide-panel-close');
  const clearBtn = document.getElementById('assistant-clear');
  const sendBtn = document.getElementById('assistant-send');
  const inputEl = document.getElementById('assistant-input') as HTMLTextAreaElement | null;
  const messagesEl = document.getElementById('assistant-messages');
  const navToggle = document.getElementById('tab-nav-toggle');

  /* ── Open/Close helpers ── */
  const openPanel = () => {
    panel?.classList.add('open');
    trigger?.classList.add('hidden');
  };
  const closePanel = () => {
    panel?.classList.remove('open');
    trigger?.classList.remove('hidden');
  };

  /* ── Trigger (right edge) ── */
  if (trigger) {
    trigger.addEventListener('mouseenter', () => trigger.classList.add('hover'));
    trigger.addEventListener('mouseleave', () => trigger.classList.remove('hover'));
    trigger.addEventListener('click', openPanel);
  }
  closeBtn?.addEventListener('click', closePanel);

  /* ── nav ◧ button opens assistant panel ── */
  navToggle?.addEventListener('click', openPanel);

  /* ── Clear ── */
  clearBtn?.addEventListener('click', () => {
    if (!messagesEl) return;
    messagesEl.innerHTML = `
      <div class="assistant-welcome">
        <div class="assistant-welcome-icon">⬡</div>
        <p class="assistant-welcome-text">Hegemonikón にようこそ。<br>何でも聞いてください。</p>
      </div>`;
  });

  /* ── Message rendering ── */
  const appendMessage = (role: 'user' | 'assistant', text: string) => {
    if (!messagesEl) return;
    // Remove welcome screen on first message
    messagesEl.querySelector('.assistant-welcome')?.remove();

    const div = document.createElement('div');
    div.className = `assistant-message assistant-message--${role}`;
    div.innerHTML = `
      <div class="assistant-message-bubble">${text.replace(/\n/g, '<br>')}</div>
      <div class="assistant-message-meta">${role === 'user' ? 'You' : '⬡'} · ${new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}</div>
    `;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  };

  const setThinking = (show: boolean) => {
    const existing = messagesEl?.querySelector('.assistant-thinking');
    if (show && !existing) {
      const div = document.createElement('div');
      div.className = 'assistant-message assistant-message--assistant assistant-thinking';
      div.innerHTML = `<div class="assistant-message-bubble"><span class="thinking-dots"><span></span><span></span><span></span></span></div>`;
      messagesEl?.appendChild(div);
      messagesEl && (messagesEl.scrollTop = messagesEl.scrollHeight);
    } else if (!show) {
      existing?.remove();
    }
  };

  /* ── Send ── */
  const sendMessage = async () => {
    if (!inputEl) return;
    const text = inputEl.value.trim();
    if (!text) return;

    appendMessage('user', text);
    inputEl.value = '';
    inputEl.style.height = 'auto';
    setThinking(true);

    try {
      // Use existing ochema API
      const res = await fetch('http://127.0.0.1:9696/api/ochema/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, model: 'MODEL_GEMINI_2_5_FLASH' }),
      });
      const data = await res.json() as { text?: string; error?: string };
      setThinking(false);
      appendMessage('assistant', data.text ?? data.error ?? '(応答なし)');
    } catch (e) {
      setThinking(false);
      appendMessage('assistant', `⚠️ バックエンドに接続できませんでした (port 9696)`);
    }
  };

  sendBtn?.addEventListener('click', () => { void sendMessage(); });

  /* ── Textarea auto-resize + Enter to send ── */
  inputEl?.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void sendMessage();
    }
  });
  inputEl?.addEventListener('input', () => {
    if (!inputEl) return;
    inputEl.style.height = 'auto';
    inputEl.style.height = `${Math.min(inputEl.scrollHeight, 120)}px`;
  });
}

// ─── Theme Toggle ────────────────────────────────────────────

function initThemeToggle(): void {
  const saved = localStorage.getItem('hgk-theme');
  if (saved === 'light' || saved === 'dark') {
    document.documentElement.setAttribute('data-theme', saved);
  }

  const isDark = () => document.documentElement.getAttribute('data-theme') !== 'light';

  const btn = document.createElement('button');
  btn.className = 'theme-toggle';
  btn.setAttribute('aria-label', 'Toggle theme');
  btn.setAttribute('title', 'テーマ切替 (Ctrl+Shift+T)');
  btn.textContent = isDark() ? '☀️' : '🌙';
  document.body.appendChild(btn);

  const toggle = () => {
    const next = isDark() ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('hgk-theme', next);
    btn.textContent = next === 'dark' ? '☀️' : '🌙';
  };

  btn.addEventListener('click', toggle);

  document.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
      e.preventDefault();
      toggle();
    }
  });
}

// ─── Keyboard Navigation (Ctrl+1‑9,0) ───────────────────────

function initKeyboardNav(): void {
  const keyRouteMap: Record<string, string> = {
    '1': 'dashboard',
    '2': 'notifications',
    '3': 'digestor',
    '4': 'search',
    '5': 'gnosis',
    '6': 'sophia',
    '7': 'pks',
    '8': 'timeline',
    '9': 'fep',
    '0': 'graph',
  };
  document.addEventListener('keydown', (e: KeyboardEvent) => {
    const el = e.target as HTMLElement;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable) return;
    if (!e.ctrlKey || e.shiftKey || e.altKey || e.metaKey) return;
    const route = keyRouteMap[e.key];
    if (route) {
      e.preventDefault();
      navigate(route);
    }
  });
}

function setupNavigation(): void {
  // Icon Rail: group switching + Obsidian-style expand
  document.getElementById('icon-rail')?.addEventListener('click', (e) => {
    const railBtn = (e.target as HTMLElement).closest('.rail-btn');
    const subBtn = (e.target as HTMLElement).closest('.rail-sub-btn');

    // Sub-item click → navigate directly
    if (subBtn) {
      const route = subBtn.getAttribute('data-route');
      if (route) navigate(route);
      return;
    }

    if (!railBtn) return;

    // Toggle button
    if (railBtn.classList.contains('rail-toggle')) {
      isTabNavOpen = !isTabNavOpen;
      buildIconRail();
      buildTabNav();
      setupTabClickHandlers();
      return;
    }

    const group = railBtn.getAttribute('data-group');
    if (!group) return;

    if (group === expandedGroup) {
      // Click same group → toggle collapse
      expandedGroup = null;
    } else {
      expandedGroup = group;
    }
    activeGroup = group;
    buildIconRail();
    buildTabNav();
    setupTabClickHandlers();

    // Navigate to first route in group if changing group
    const groupDef = ICON_GROUPS.find(g => g.id === group);
    if (groupDef && groupDef.routes.length > 0) {
      const currentRoute = getCurrentRoute();
      if (!groupDef.routes.includes(currentRoute)) {
        navigate(groupDef.routes[0]);
      }
    }
  });

  setupTabClickHandlers();
}

function setupTabClickHandlers(): void {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const route = btn.getAttribute('data-route');
      if (route) navigate(route);
    });
  });
}

// ─── Nav Badge (CRITICAL count) ──────────────────────────────

async function updateNotifBadge(): Promise<void> {
  try {
    const criticals = await api.notifications(100, 'CRITICAL');
    const count = criticals.length;
    const notifBtn = document.querySelector('.tab-btn[data-route="notifications"]');
    if (!notifBtn) return;
    const existing = notifBtn.querySelector('.nav-badge');
    if (existing) existing.remove();
    if (count > 0) {
      const badge = document.createElement('span');
      badge.className = 'nav-badge';
      badge.textContent = String(count);
      notifBtn.appendChild(badge);
    }
  } catch { /* silent */ }
}

// ─── Navigation ──────────────────────────────────────────────

function navigate(route: string): void {
  if (route === getCurrentRoute()) return;
  setCurrentRoute(route);
  clearPolling();
  recordView(route);

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-route') === route);
  });

  // Also highlight the correct icon rail group
  const group = ICON_GROUPS.find(g => g.routes.includes(route));
  if (group && group.id !== activeGroup) {
    activeGroup = group.id;
    buildIconRail();
    buildTabNav();
    setupTabClickHandlers();
  }

  const app = document.getElementById('view-content');
  if (!app) return;

  app.classList.remove('view-enter');
  app.classList.add('view-exit');

  setTimeout(() => {
    app.classList.remove('view-exit');
    app.innerHTML = skeletonHTML();
    app.classList.add('view-enter');

    const renderer = ROUTE_MAP[route];
    if (renderer) {
      const timeout = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('応答がタイムアウトしました (10秒)')), 10000)
      );
      Promise.race([renderer(), timeout]).then(() => {
        app.classList.remove('view-enter');
        void app.offsetWidth;
        app.classList.add('view-enter');
      }).catch((err: Error) => {
        const routeLabel = ROUTES.find(r => r.key === route)?.label ?? route;
        app.innerHTML = `
          <div class="error-boundary">
            <div class="error-boundary-icon">⚠️</div>
            <h2>${esc(routeLabel)} を読み込めませんでした</h2>
            <p class="error-boundary-detail">${esc(err.message)}</p>
            <div class="error-boundary-actions">
              <button class="btn error-retry-btn" id="error-retry">再試行</button>
              <button class="btn btn-ghost" id="error-dashboard">Dashboard へ戻る</button>
            </div>
          </div>`;
        document.getElementById('error-retry')?.addEventListener('click', () => {
          setCurrentRoute('');  // force re-navigate
          navigate(route);
        });
        document.getElementById('error-dashboard')?.addEventListener('click', () => {
          setCurrentRoute('');
          navigate('dashboard');
        });
      });
    }
  }, 120);
}
