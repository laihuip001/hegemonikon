/**
 * Route Configuration — Single Source of Truth
 *
 * index.html のナビと main.ts のルーティングを統一する設定。
 * ルート追加・変更はここだけで完結する。
 */

const renderDashboard = async () => {
    const { renderDashboard: render } = await import('./views/dashboard');
    await render();
};
const renderAgentManagerView = async () => {
    const { renderAgentManagerView: render } = await import('./views/agent-manager');
    await render();
};
const renderSearch = async () => {
    const { renderSearch: render } = await import('./views/search');
    await render();
};
const renderFep = async () => {
    const { renderFep: render } = await import('./views/fep');
    await render();
};
const renderGnosis = async () => {
    const { renderGnosis: render } = await import('./views/gnosis');
    await render();
};
const renderQuality = async () => {
    const { renderQuality: render } = await import('./views/quality');
    await render();
};
const renderPostcheck = async () => {
    const { renderPostcheck: render } = await import('./views/postcheck');
    await render();
};
// Three.js graph — lazy loaded to split the 700KB+ chunk
const renderGraph3D = async () => {
    const { renderGraph3D: render } = await import('./views/graph3d');
    await render();
};
const renderNotifications = async () => {
    const { renderNotifications: render } = await import('./views/notifications');
    await render();
};
const renderPKS = async () => {
    const { renderPKS: render } = await import('./views/pks');
    await render();
};
const renderSophiaView = async () => {
    const { renderSophiaView: render } = await import('./views/sophia');
    await render();
};
const renderTimelineView = async () => {
    const { renderTimelineView: render } = await import('./views/timeline');
    await render();
};
const renderSynteleiaView = async () => {
    const { renderSynteleiaView: render } = await import('./views/synteleia');
    await render();
};
const renderSynedrionView = async () => {
    const { renderSynedrionView: render } = await import('./views/synedrion');
    await render();
};
const renderDigestorView = async () => {
    const { renderDigestorView: render } = await import('./views/digestor');
    await render();
};
const renderDesktopDomView = async () => {
    const { renderDesktopDomView: render } = await import('./views/desktop-dom');
    await render();
};
const renderChatView = async () => {
    const { renderChatView: render } = await import('./views/chat');
    await render();
};
const renderAristosView = async () => {
    const { renderAristosView: render } = await import('./views/aristos');
    await render();
};
const renderSettingsView = async () => {
    const { renderSettingsView: render } = await import('./views/settings');
    await render();
};

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
    { key: 'aristos', label: 'Aristos', icon: '🧬', renderer: renderAristosView },
    { key: 'settings', label: 'Settings', icon: '⚙️', renderer: renderSettingsView },
];

// ─── Derived Maps ────────────────────────────────────────────

/** Route key → renderer lookup (for navigate()) */
export const ROUTE_MAP: Record<string, ViewRenderer> =
    Object.fromEntries(ROUTES.map(r => [r.key, r.renderer]));

/** Default route */
export const DEFAULT_ROUTE = 'dashboard';
