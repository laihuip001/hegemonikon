import type { paths, components } from '../api-types';

const API_BASE = 'http://127.0.0.1:9696';

// Tauri 環境判定: __TAURI_INTERNALS__ 存在時のみ Tauri fetch を使用
let resolvedFetch: typeof globalThis.fetch | null = null;

async function getFetch(): Promise<typeof globalThis.fetch> {
    if (resolvedFetch) return resolvedFetch;
    if ((window as any).__TAURI_INTERNALS__) {
        try {
            const mod = await import('@tauri-apps/plugin-http');
            resolvedFetch = mod.fetch as unknown as typeof globalThis.fetch;
        } catch {
            resolvedFetch = globalThis.fetch;
        }
    } else {
        resolvedFetch = globalThis.fetch;
    }
    return resolvedFetch;
}

// Helper for type-safe fetch
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const fetchFn = await getFetch();
    const response = await fetchFn(`${API_BASE}${path}`, options);
    if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return response.json() as Promise<T>;
}

// --- Exported Types ---
export type HealthCheckResponse = paths['/api/status/health']['get']['responses']['200']['content']['application/json'];
export type HealthReportResponse = paths['/api/status']['get']['responses']['200']['content']['application/json'];
export type FEPStateResponse = paths['/api/fep/state']['get']['responses']['200']['content']['application/json'];
export type FEPStepRequest = components['schemas']['FEPStepRequest'];
export type FEPStepResponse = paths['/api/fep/step']['post']['responses']['200']['content']['application/json'];
export type FEPDashboardResponse = paths['/api/fep/dashboard']['get']['responses']['200']['content']['application/json'];
export type GnosisSearchResponse = paths['/api/gnosis/search']['get']['responses']['200']['content']['application/json'];
export type GnosisStatsResponse = paths['/api/gnosis/stats']['get']['responses']['200']['content']['application/json'];
export type DendronReportResponse = paths['/api/dendron/report']['get']['responses']['200']['content']['application/json'];
export type PostcheckResponse = paths['/api/postcheck/run']['post']['responses']['200']['content']['application/json'];
export type SELListResponse = paths['/api/postcheck/list']['get']['responses']['200']['content']['application/json'];

export const api = {
    // Status
    health: () => apiFetch<HealthCheckResponse>('/api/status/health'),
    status: () => apiFetch<HealthReportResponse>('/api/status'),

    // FEP
    fepState: () => apiFetch<FEPStateResponse>('/api/fep/state'),
    fepStep: (observation: number) => apiFetch<FEPStepResponse>('/api/fep/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ observation } satisfies FEPStepRequest),
    }),
    fepDashboard: () => apiFetch<FEPDashboardResponse>('/api/fep/dashboard'),

    // Gnōsis
    gnosisSearch: (q: string, limit = 10) =>
        apiFetch<GnosisSearchResponse>(`/api/gnosis/search?q=${encodeURIComponent(q)}&limit=${limit}`),
    gnosisStats: () => apiFetch<GnosisStatsResponse>('/api/gnosis/stats'),

    // Quality
    dendronReport: (detail: 'summary' | 'full' = 'summary') =>
        apiFetch<DendronReportResponse>(`/api/dendron/report?detail=${detail}`),

    // Postcheck
    postcheckList: () => apiFetch<SELListResponse>('/api/postcheck/list'),
    postcheckRun: (wfName: string, content: string, mode = '') =>
        apiFetch<PostcheckResponse>('/api/postcheck/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wf_name: wfName, content, mode }),
        }),

    // Graph
    graphNodes: () => apiFetch<GraphNode[]>('/api/graph/nodes'),
    graphEdges: () => apiFetch<GraphEdge[]>('/api/graph/edges'),
    graphFull: () => apiFetch<GraphFullResponse>('/api/graph/full'),
};

// --- Graph Types ---
export interface GraphNode {
    id: string;
    series: string;
    name: string;
    greek: string;
    meaning: string;
    workflow: string;
    type: string;
    color: string;
    position: { x: number; y: number; z: number };
}

export interface GraphEdge {
    id: string;
    pair: string;
    source: string;
    target: string;
    shared_coordinate: string;
    naturality: string;
    meaning: string;
    type: string;
}

export interface GraphFullResponse {
    nodes: GraphNode[];
    edges: GraphEdge[];
    meta: {
        total_nodes: number;
        total_edges: number;
        series: Record<string, { name: string; color: string; theorems: number }>;
        trigonon: { vertices: string[]; description: string };
        naturality: Record<string, string>;
    };
}
