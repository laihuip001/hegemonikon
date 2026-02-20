/**
 * Route Configuration — Single Source of Truth
 *
 * index.html のナビと main.ts のルーティングを統一する設定。
 * ルート追加・変更はここだけで完結する。
 */

import { renderDashboard } from './views/dashboard';

// ─── Types ───────────────────────────────────────────────────

export type ViewRenderer = () => Promise<void>;

export interface RouteConfig {
    key: string;
    label: string;
    icon: string;
    renderer: ViewRenderer;
}

// ─── Lazy Loading Helper ─────────────────────────────────────

/**
 * Creates a lazy-loaded renderer.
 * Splits code into separate chunks loaded only when the route is visited.
 */
function lazy(importer: () => Promise<any>, exportName: string): ViewRenderer {
    return async () => {
        const mod = await importer();
        const renderer = mod[exportName] as ViewRenderer;
        if (!renderer) {
            throw new Error(`Module does not export '${exportName}'`);
        }
        await renderer();
    };
}

// ─── Route Definitions ───────────────────────────────────────

export const ROUTES: RouteConfig[] = [
    { key: 'dashboard', label: 'Dashboard', icon: '📊', renderer: renderDashboard },
    { key: 'orchestrator', label: 'Orchestrator', icon: '🎯', renderer: lazy(() => import('./views/orchestrator'), 'renderOrchestratorView') },
    { key: 'agents', label: 'Agents', icon: '🤖', renderer: lazy(() => import('./views/agent-manager'), 'renderAgentManagerView') },
    { key: 'search', label: 'Search', icon: '🔍', renderer: lazy(() => import('./views/search'), 'renderSearch') },
    { key: 'fep', label: 'FEP Agent', icon: '🧠', renderer: lazy(() => import('./views/fep'), 'renderFep') },
    { key: 'gnosis', label: 'Gnōsis', icon: '📖', renderer: lazy(() => import('./views/gnosis'), 'renderGnosis') },
    { key: 'quality', label: 'Quality', icon: '✅', renderer: lazy(() => import('./views/quality'), 'renderQuality') },
    { key: 'postcheck', label: 'Postcheck', icon: '🔄', renderer: lazy(() => import('./views/postcheck'), 'renderPostcheck') },
    { key: 'graph', label: 'Graph', icon: '🔮', renderer: lazy(() => import('./views/graph3d'), 'renderGraph3D') },
    { key: 'notifications', label: 'Notifications', icon: '🔔', renderer: lazy(() => import('./views/notifications'), 'renderNotifications') },
    { key: 'pks', label: 'PKS', icon: '📡', renderer: lazy(() => import('./views/pks'), 'renderPKS') },
    { key: 'sophia', label: 'Sophia KI', icon: '📚', renderer: lazy(() => import('./views/sophia'), 'renderSophiaView') },
    { key: 'timeline', label: 'Timeline', icon: '📅', renderer: lazy(() => import('./views/timeline'), 'renderTimelineView') },
    { key: 'synteleia', label: 'Synteleia', icon: '🛡️', renderer: lazy(() => import('./views/synteleia'), 'renderSynteleiaView') },
    { key: 'synedrion', label: 'Synedrion', icon: '🔭', renderer: lazy(() => import('./views/synedrion'), 'renderSynedrionView') },
    { key: 'digestor', label: 'Digestor', icon: '🧬', renderer: lazy(() => import('./views/digestor'), 'renderDigestorView') },
    { key: 'desktop', label: 'Desktop', icon: '🖥️', renderer: lazy(() => import('./views/desktop-dom'), 'renderDesktopDomView') },
    { key: 'chat', label: 'Chat', icon: '💬', renderer: lazy(() => import('./views/chat'), 'renderChatView') },
    { key: 'devtools', label: 'DevTools', icon: '🛠️', renderer: lazy(() => import('./views/devtools'), 'renderDevToolsView') },
    { key: 'aristos', label: 'Aristos', icon: '🧬', renderer: lazy(() => import('./views/aristos'), 'renderAristosView') },
    { key: 'settings', label: 'Settings', icon: '⚙️', renderer: lazy(() => import('./views/settings'), 'renderSettingsView') },
];

// ─── Derived Maps ────────────────────────────────────────────

/** Route key → renderer lookup (for navigate()) */
export const ROUTE_MAP: Record<string, ViewRenderer> =
    Object.fromEntries(ROUTES.map(r => [r.key, r.renderer]));

/** Default route */
export const DEFAULT_ROUTE = 'dashboard';
