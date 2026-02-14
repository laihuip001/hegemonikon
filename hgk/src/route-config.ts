/**
 * Route Configuration — Single Source of Truth
 *
 * index.html のナビと main.ts のルーティングを統一する設定。
 * ルート追加・変更はここだけで完結する。
 */

import { renderDashboard } from './views/dashboard';
import { renderAgentManagerView } from './views/agent-manager';
import { renderSearch } from './views/search';
import { renderFep } from './views/fep';
import { renderGnosis } from './views/gnosis';
import { renderQuality } from './views/quality';
import { renderPostcheck } from './views/postcheck';
import { renderGraph3D } from './views/graph3d';
import { renderNotifications } from './views/notifications';
import { renderPKS } from './views/pks';
import { renderSophiaView } from './views/sophia';
import { renderTimelineView } from './views/timeline';
import { renderSynteleiaView } from './views/synteleia';
import { renderSynedrionView } from './views/synedrion';
import { renderDigestorView } from './views/digestor';
import { renderDesktopDomView } from './views/desktop-dom';
import { renderChatView } from './views/chat';

// ─── Types ───────────────────────────────────────────────────

export type ViewRenderer = () => Promise<void>;

export interface RouteConfig {
    key: string;
    label: string;
    icon: string;
    renderer: ViewRenderer;
}

// ─── Route Definitions ───────────────────────────────────────

export const ROUTES: RouteConfig[] = [
    { key: 'dashboard', label: 'Dashboard', icon: '📊', renderer: renderDashboard },
    { key: 'agents', label: 'Agents', icon: '🤖', renderer: renderAgentManagerView },
    { key: 'search', label: 'Search', icon: '🔍', renderer: renderSearch },
    { key: 'fep', label: 'FEP Agent', icon: '🧠', renderer: renderFep },
    { key: 'gnosis', label: 'Gnōsis', icon: '📖', renderer: renderGnosis },
    { key: 'quality', label: 'Quality', icon: '✅', renderer: renderQuality },
    { key: 'postcheck', label: 'Postcheck', icon: '🔄', renderer: renderPostcheck },
    { key: 'graph', label: 'Graph', icon: '🔮', renderer: renderGraph3D },
    { key: 'notifications', label: 'Notifications', icon: '🔔', renderer: renderNotifications },
    { key: 'pks', label: 'PKS', icon: '📡', renderer: renderPKS },
    { key: 'sophia', label: 'Sophia KI', icon: '📚', renderer: renderSophiaView },
    { key: 'timeline', label: 'Timeline', icon: '📅', renderer: renderTimelineView },
    { key: 'synteleia', label: 'Synteleia', icon: '🛡️', renderer: renderSynteleiaView },
    { key: 'synedrion', label: 'Synedrion', icon: '🔭', renderer: renderSynedrionView },
    { key: 'digestor', label: 'Digestor', icon: '🧬', renderer: renderDigestorView },
    { key: 'desktop', label: 'Desktop', icon: '🖥️', renderer: renderDesktopDomView },
    { key: 'chat', label: 'Chat', icon: '💬', renderer: renderChatView },
];

// ─── Derived Maps ────────────────────────────────────────────

/** Route key → renderer lookup (for navigate()) */
export const ROUTE_MAP: Record<string, ViewRenderer> =
    Object.fromEntries(ROUTES.map(r => [r.key, r.renderer]));

/** Default route */
export const DEFAULT_ROUTE = 'dashboard';
