/**
 * E2E Test Fixtures — Playwright route mock for API independence
 *
 * Intercepts all API calls to 127.0.0.1:9696 and returns
 * deterministic mock responses. Enables tests to run without backend.
 */

import { Page } from '@playwright/test';

// --- Mock Data ---

const MOCK_HEALTH = {
    status: 'ok',
    version: '0.1.0-test',
    uptime: 42,
};

const MOCK_WF_LIST = {
    workflows: [
        { name: 'noe', description: 'Noēsis — 深い認識', ccl: '/noe+', modes: ['L3'] },
        { name: 'dia', description: 'Krisis — 判定', ccl: '/dia', modes: ['L2'] },
        { name: 'bou', description: 'Boulēsis — 意志', ccl: '/bou+', modes: ['L3'] },
        { name: 'ene', description: 'Energeia — 行為', ccl: '/ene+', modes: ['L3'] },
        { name: 'zet', description: 'Zētēsis — 探求', ccl: '/zet', modes: ['L2'] },
    ],
};

const MOCK_GNOSIS_STATS = {
    total_papers: 128,
    total_chunks: 2048,
    sources: ['arxiv', 'semantic_scholar'],
};

const MOCK_DASHBOARD = {
    status: 'ok',
    stats: {
        total_theorems: 24,
        total_relations: 72,
        total_workflows: 45,
    },
};

const MOCK_TIMELINE_STATS = {
    total: 42,
    by_type: { handoff: 15, doxa: 12, workflow: 10, kalon: 5 },
    handoff: 15, doxa: 12, workflow: 10, kalon: 5,
    latest_handoff: '2026-02-15',
};

const MOCK_QUOTA = {
    models: [],
    error: null,
};

const MOCK_GRAPH_FULL = {
    nodes: [
        { id: 'T1', series: 'O', name: 'Theorem 1', greek: 'Alpha', meaning: 'Beginning', workflow: 'noe', type: 'Pure', color: '#00d4ff', position: { x: 0, y: 0, z: 0 } },
        { id: 'T2', series: 'S', name: 'Theorem 2', greek: 'Beta', meaning: 'Flow', workflow: 'dia', type: 'Applied', color: '#10b981', position: { x: 10, y: 10, z: 10 } }
    ],
    edges: [
        { id: 'E1', pair: 'T1-T2', source: 'T1', target: 'T2', shared_coordinate: 'X', naturality: 'experiential', meaning: 'Connection', type: 'standard' }
    ],
    meta: {
        total_nodes: 2,
        total_edges: 1,
        series: { 'O': { name: 'Origin', color: '#00d4ff', theorems: 1 }, 'S': { name: 'Stream', color: '#10b981', theorems: 1 } },
        trigonon: { vertices: ['T1', 'T2'], description: 'Simple test' },
        naturality: { experiential: 'Blue' }
    }
};

// --- Route Mock Setup ---

export async function setupApiMock(page: Page): Promise<void> {
    await page.route('**/api/**', async (route) => {
        const url = route.request().url();
        const path = new URL(url).pathname;

        // Match known API endpoints
        const mocks: Record<string, unknown> = {
            '/api/health': MOCK_HEALTH,
            '/api/health/report': { status: 'ok', checks: [] },
            '/api/wf/list': MOCK_WF_LIST,
            '/api/gnosis/stats': MOCK_GNOSIS_STATS,
            '/api/dashboard': MOCK_DASHBOARD,
            '/api/timeline/stats': MOCK_TIMELINE_STATS,
            '/api/quota': MOCK_QUOTA,
            '/api/notifications': { notifications: [], unread: 0 },
            '/api/pks/status': { status: 'idle', last_push: null },
            '/api/sophia/stats': { total_kis: 0, categories: [] },
            '/api/synteleia/agents': { agents: [] },
            '/api/synedrion/perspectives': { perspectives: [] },
            '/api/digestor/status': { status: 'idle', last_run: null },
            '/api/aristos/status': { status: 'idle' },
            '/api/sentinel/latest': { status: 'no_report' },
            '/api/graph/full': MOCK_GRAPH_FULL,
            '/api/link-graph/full': { nodes: [], edges: [], meta: { total_nodes: 0, total_edges: 0, source_type_counts: {}, projection_counts: {}, projection_map: {} } },
        };

        // Exact match
        if (mocks[path]) {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify(mocks[path]),
            });
            return;
        }

        // Prefix match for dynamic endpoints
        for (const [prefix, data] of Object.entries(mocks)) {
            if (path.startsWith(prefix)) {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify(data),
                });
                return;
            }
        }

        // Fallback: return empty 200
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ status: 'ok' }),
        });
    });
}

/**
 * Setup API mock that returns 500 for all endpoints.
 * Used for offline/error resilience testing.
 */
export async function setupApiError(page: Page): Promise<void> {
    await page.route('http://127.0.0.1:9696/**', async (route) => {
        await route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Backend unavailable' }),
        });
    });
}
