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

// --- Timeline Types ---
export interface TimelineEvent {
    id: string;
    type: 'handoff' | 'doxa' | 'workflow' | 'kalon';
    title: string;
    date: string;
    summary: string;
    filename: string;
    size_bytes: number;
    mtime: string;
}
export interface TimelineEventsResponse {
    events: TimelineEvent[];
    total: number;
    offset: number;
    limit: number;
    has_more: boolean;
}
export interface TimelineEventDetail extends TimelineEvent {
    content: string;
}
export interface TimelineStatsResponse {
    total: number;
    by_type: { handoff: number; doxa: number; workflow: number; kalon: number };
    latest_handoff: string | null;
}

// --- Kalon Types ---
export interface KalonJudgeResponse {
    concept: string;
    verdict: string;
    label: string;
    g_test: boolean;
    f_test: boolean;
    timestamp: string;
    filename: string;
}
export interface KalonJudgment {
    concept: string;
    verdict: string;
    filename: string;
    mtime: string;
}
export interface KalonHistoryResponse {
    judgments: KalonJudgment[];
    total: number;
}

// --- Synteleia Types ---
export interface SynteleiaIssue {
    agent: string;
    code: string;
    severity: string;
    message: string;
    location?: string;
    suggestion?: string;
}
export interface SynteleiaAgentResult {
    agent_name: string;
    passed: boolean;
    confidence: number;
    issues: SynteleiaIssue[];
}
export interface SynteleiaAuditResponse {
    passed: boolean;
    summary: string;
    critical_count: number;
    high_count: number;
    total_issues: number;
    agent_results: SynteleiaAgentResult[];
    report: string;
    wbc_alerted: boolean;
}
export interface SynteleiaAgentInfo {
    name: string;
    description: string;
    layer: string;
}

// --- Digestor Types ---
export interface DigestCandidate {
    title: string;
    source: string;
    url: string;
    score: number;
    matched_topics: string[];
    rationale: string;
    suggested_templates: Array<{ id: string; score: number }>;
}
export interface DigestReport {
    timestamp: string;
    source: string;
    total_papers: number;
    candidates_selected: number;
    dry_run: boolean;
    candidates: DigestCandidate[];
    filename: string;
}
export interface DigestReportListResponse {
    reports: DigestReport[];
    total: number;
}

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

    // Link Graph
    linkGraphFull: (sourceType?: string) =>
        apiFetch<LinkGraphFullResponse>(
            `/api/link-graph/full${sourceType ? `?source_type=${encodeURIComponent(sourceType)}` : ''}`
        ),
    linkGraphStats: () => apiFetch<LinkGraphStatsResponse>('/api/link-graph/stats'),
    linkGraphNeighbors: (nodeId: string, hops = 2) =>
        apiFetch<LinkGraphNeighborsResponse>(`/api/link-graph/neighbors/${encodeURIComponent(nodeId)}?hops=${hops}`),

    // CCL + Workflows
    cclParse: (ccl: string) =>
        apiFetch<CCLParseResponse>('/api/ccl/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ccl }),
        }),
    wfList: () => apiFetch<WFListResponse>('/api/wf/list'),
    wfDetail: (name: string) => apiFetch<WFDetailResponse>(`/api/wf/${encodeURIComponent(name)}`),

    // Symploke 統合検索
    symplokeSearch: (q: string, k = 10, sources = 'handoff,sophia,kairos,gnosis,chronos') =>
        apiFetch<SymplokeSearchResponse>(
            `/api/symploke/search?q=${encodeURIComponent(q)}&k=${k}&sources=${encodeURIComponent(sources)}`
        ),
    symplokeStats: () => apiFetch<SymplokeStatsResponse>('/api/symploke/stats'),

    // Timeline
    timelineEvents: (limit = 50, offset = 0, type?: string) => {
        let url = `/api/timeline/events?limit=${limit}&offset=${offset}`;
        if (type) url += `&event_type=${type}`;
        return apiFetch<TimelineEventsResponse>(url);
    },
    timelineEvent: (id: string) => apiFetch<TimelineEventDetail>(`/api/timeline/event/${id}`),
    timelineStats: () => apiFetch<TimelineStatsResponse>('/api/timeline/stats'),

    // Kalon
    kalonJudge: (concept: string, g_test: boolean, f_test: boolean, notes = '') =>
        apiFetch<KalonJudgeResponse>('/api/kalon/judge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ concept, g_test, f_test, notes }),
        }),
    kalonHistory: (limit = 50) =>
        apiFetch<KalonHistoryResponse>(`/api/kalon/history?limit=${limit}`),

    // Synteleia
    synteleiaAudit: (content: string, targetType = 'generic', withL2 = false, source?: string) =>
        apiFetch<SynteleiaAuditResponse>('/api/synteleia/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, target_type: targetType, with_l2: withL2, source }),
        }),
    synteleiaQuick: (content: string, targetType = 'generic') =>
        apiFetch<SynteleiaAuditResponse>('/api/synteleia/audit-quick', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, target_type: targetType }),
        }),
    synteleiaAgents: () => apiFetch<SynteleiaAgentInfo[]>('/api/synteleia/agents'),

    // Digestor
    digestorReports: (limit = 10) =>
        apiFetch<DigestReportListResponse>(`/api/digestor/reports?limit=${limit}`),
    digestorLatest: () =>
        apiFetch<DigestReport | null>('/api/digestor/latest'),
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

// --- Link Graph Types ---
export interface LinkGraphNode {
    id: string;
    title: string;
    source_type: string;
    projected_series: string;
    projected_theorem: string;
    degree: number;
    backlink_count: number;
    community: number;
    orbit_angle: number;
    orbit_radius: number;
}

export interface LinkGraphEdge {
    source: string;
    target: string;
    type: string;
}

export interface LinkGraphFullResponse {
    nodes: LinkGraphNode[];
    edges: LinkGraphEdge[];
    meta: {
        total_nodes: number;
        total_edges: number;
        source_type_counts: Record<string, number>;
        projection_counts: Record<string, number>;
        projection_map: Record<string, string>;
    };
}

export interface LinkGraphStatsResponse {
    total_nodes: number;
    total_edges: number;
    bridge_nodes: string[];
    source_type_counts: Record<string, number>;
    projection_counts: Record<string, number>;
}

export interface LinkGraphNeighborsResponse {
    node_id: string;
    hops: number;
    neighbors: Array<{
        id: string;
        title: string;
        source_type: string;
        projected_series: string;
        projected_theorem: string;
        degree: number;
    }>;
    total: number;
    error?: string;
}

// ─── Sophia KI Types ─────────────────────────────────────

export interface KIListItem {
    id: string;
    title: string;
    source_type: string;
    updated: string;
    created: string;
    size_bytes: number;
}

export interface KIDetail {
    id: string;
    title: string;
    content: string;
    source_type: string;
    updated: string;
    created: string;
    size_bytes: number;
    backlinks: string[];
}

export interface KICreateRequest {
    title: string;
    content?: string;
    source_type?: string;
}

export interface KIUpdateRequest {
    title?: string;
    content?: string;
}

export interface KIListResponse {
    items: KIListItem[];
    total: number;
}

export interface KISearchResult {
    id: string;
    title: string;
    snippet: string;
    line_number: number;
}

export interface KISearchResponse {
    query: string;
    results: KISearchResult[];
    total: number;
}

// ─── Symploke 統合検索 Types ─────────────────────────────

export interface SymplokeSearchResultItem {
    id: string;
    source: string; // "handoff" | "sophia" | "kairos" | "gnosis" | "chronos"
    score: number;
    title: string;
    snippet: string;
    metadata: Record<string, unknown>;
}

export interface SymplokeSearchResponse {
    query: string;
    results: SymplokeSearchResultItem[];
    total: number;
    sources_searched: string[];
}

export interface SymplokeStatsResponse {
    handoff_count: number;
    sophia_index_exists: boolean;
    kairos_index_exists: boolean;
    persona_exists: boolean;
    boot_axes_available: string[];
}

// ─── Sophia KI API Methods ───────────────────────────────

export async function kiList(): Promise<KIListResponse> {
    return apiFetch<KIListResponse>('/api/sophia/ki');
}

export async function kiGet(id: string): Promise<KIDetail> {
    return apiFetch<KIDetail>(`/api/sophia/ki/${encodeURIComponent(id)}`);
}

export async function kiCreate(req: KICreateRequest): Promise<KIDetail> {
    return apiFetch<KIDetail>('/api/sophia/ki', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
    });
}

export async function kiUpdate(id: string, req: KIUpdateRequest): Promise<KIDetail> {
    return apiFetch<KIDetail>(`/api/sophia/ki/${encodeURIComponent(id)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
    });
}

export async function kiDelete(id: string): Promise<{ status: string; id: string }> {
    return apiFetch<{ status: string; id: string }>(`/api/sophia/ki/${encodeURIComponent(id)}`, {
        method: 'DELETE',
    });
}

export async function kiSearch(query: string, limit = 20): Promise<KISearchResponse> {
    return apiFetch<KISearchResponse>(`/api/sophia/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}
