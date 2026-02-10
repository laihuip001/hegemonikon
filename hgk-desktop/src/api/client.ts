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

    // Notifications (Sympatheia)
    notifications: (limit = 50, level?: string) =>
        apiFetch<Notification[]>(
            `/api/sympatheia/notifications?limit=${limit}${level ? `&level=${level}` : ''}`
        ),

    // PKS
    pksPush: () => apiFetch<PKSPushResponse>('/api/pks/push'),
    pksTriggerPush: (_k = 20) => apiFetch<PKSPushResponse>('/api/pks/push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    }),
    pksFeedback: (title: string, reaction: string, series = '') =>
        apiFetch<PKSFeedbackResponse>('/api/pks/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, reaction, series }),
        }),
    pksStats: () => apiFetch<PKSStatsResponse>('/api/pks/stats'),

    // Gnōsis Narrator
    gnosisPapers: (query = '', limit = 20) =>
        apiFetch<GnosisPapersResponse>(`/api/gnosis/papers?query=${encodeURIComponent(query)}&limit=${limit}`),
    gnosisNarrate: (title: string, fmt = 'deep_dive') =>
        apiFetch<GnosisNarrateResponse>('/api/gnosis/narrate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, fmt }),
        }),

    // CCL + Workflows
    cclParse: (ccl: string) =>
        apiFetch<CCLParseResponse>('/api/ccl/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ccl }),
        }),
    wfList: () => apiFetch<WFListResponse>('/api/wf/list'),
    wfDetail: (name: string) => apiFetch<WFDetailResponse>(`/api/wf/${encodeURIComponent(name)}`),
};

// --- Notification Types ---
export interface Notification {
    id: string;
    timestamp: string;
    source: string;
    level: 'INFO' | 'HIGH' | 'CRITICAL';
    title: string;
    body: string;
    data: Record<string, unknown>;
}

// --- PKS Types ---
export interface PKSNugget {
    title: string;
    abstract: string;
    source: string;
    relevance_score: number;
    url: string;
    authors: string;
    push_reason: string;
    serendipity_score: number;
    suggested_questions: string[];
}

export interface PKSPushResponse {
    timestamp: string;
    topics: string[];
    nuggets: PKSNugget[];
    total: number;
}

export interface PKSFeedbackResponse {
    timestamp: string;
    title: string;
    reaction: string;
    recorded: boolean;
}

export interface PKSStatsResponse {
    timestamp: string;
    series_stats: Record<string, { count: number; avg_score: number; threshold_adjustment: number }>;
    total_feedbacks: number;
}

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

// --- Gnōsis Narrator Types ---
export interface PaperCard {
    title: string;
    authors: string;
    abstract: string;
    source: string;
    topics: string[];
    relevance_score: number;
    question: string;  // kalon: この論文が投げかける問い
}

export interface GnosisPapersResponse {
    timestamp: string;
    papers: PaperCard[];
    total: number;
}

export interface NarrateSegment {
    speaker: string;
    content: string;
}

export interface GnosisNarrateResponse {
    timestamp: string;
    title: string;
    fmt: string;
    segments: NarrateSegment[];
    icon: string;
    generated: boolean;
}

// --- CCL Types ---
export interface CCLParseResponse {
    success: boolean;
    ccl: string;
    tree: string | null;
    workflows: string[];
    wf_paths: Record<string, string>;
    plan_template: string | null;
    error: string | null;
}

export interface WFSummary {
    name: string;
    description: string;
    ccl: string;
    modes: string[];
}

export interface WFListResponse {
    total: number;
    workflows: WFSummary[];
}

export interface WFDetailResponse {
    name: string;
    description: string;
    ccl: string;
    stages: Array<{ name?: string; description?: string }>;
    modes: string[];
    source_path: string | null;
    raw_content: string | null;
    metadata: Record<string, unknown>;
}
