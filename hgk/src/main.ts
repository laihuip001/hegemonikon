import { api } from './api/client';
import { renderGraph3D } from './views/graph3d';
import { renderAgentManagerView } from './views/agent-manager';
import { renderChatView } from './views/chat';
import { renderDesktopDomView } from './views/desktop-dom';
import { renderDashboard } from './views/dashboard';
import { renderFep } from './views/fep';
import { renderGnosis } from './views/gnosis';
import { renderQuality } from './views/quality';
import { renderPostcheck } from './views/postcheck';
import { renderNotifications } from './views/notifications';
import { renderPKS } from './views/pks';
import { renderSophiaView } from './views/sophia';
import { renderSearch } from './views/search';
import { renderTimelineView } from './views/timeline';
import { renderSynteleiaView } from './views/synteleia';
import { renderSynedrionView } from './views/synedrion';
import { renderDigestorView } from './views/digestor';
import { recordView } from './telemetry';
import { initCommandPalette } from './command_palette';
import { clearPolling, setCurrentRoute, skeletonHTML, esc } from './utils';
import './styles.css';

// ─── Router ──────────────────────────────────────────────────

type ViewRenderer = () => Promise<void>;
const routes: Record<string, ViewRenderer> = {
  'dashboard': renderDashboard,
  'agents': renderAgentManagerView,
  'search': renderSearch,
  'fep': renderFep,
  'gnosis': renderGnosis,
  'quality': renderQuality,
  'postcheck': renderPostcheck,
  'graph': renderGraph3D,
  'notifications': renderNotifications,
  'pks': renderPKS,
  'sophia': renderSophiaView,
  'timeline': renderTimelineView,
  'synteleia': renderSynteleiaView,
  'synedrion': renderSynedrionView,
  'digestor': renderDigestorView,
  'chat': renderChatView,
  'desktop': renderDesktopDomView,
};

let currentRoute = '';

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  navigate('dashboard');
  // Start global badge polling
  void updateNotifBadge();
  setInterval(() => { void updateNotifBadge(); }, 60_000);
  // PKS auto-push on startup (fire-and-forget)
  void api.pksTriggerPush().catch(() => { /* silent */ });
  // CCL Command Palette — Ctrl+K
  initCommandPalette();
  initKeyboardNav();
  initThemeToggle();
});

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
  document.querySelectorAll('nav button').forEach(btn => {
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
    const notifBtn = document.querySelector('nav button[data-route="notifications"]');
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
  if (route === currentRoute) return;
  currentRoute = route;
  setCurrentRoute(route);
  clearPolling();
  recordView(route);

  document.querySelectorAll('nav button').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-route') === route);
  });

  const app = document.getElementById('view-content');
  if (!app) return;

  app.classList.remove('view-enter');
  app.classList.add('view-exit');

  setTimeout(() => {
    app.classList.remove('view-exit');
    app.innerHTML = skeletonHTML();
    app.classList.add('view-enter');

    const renderer = routes[route];
    if (renderer) {
      renderer().then(() => {
        app.classList.remove('view-enter');
        void app.offsetWidth;
        app.classList.add('view-enter');
      }).catch((err: Error) => {
        app.innerHTML = `<div class="card status-error">Error: ${esc(err.message)}</div>`;
      });
    }
  }, 120);
}
