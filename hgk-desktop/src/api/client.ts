import { fetch } from '@tauri-apps/plugin-http';
import type { paths } from '../api-types';

const API_BASE = 'http://127.0.0.1:9696';

// Helper for type-safe fetch
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, options);
    if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return response.json() as Promise<T>;
}

export type HealthCheckResponse = paths['/api/status/health']['get']['responses']['200']['content']['application/json'];
export type HealthReportResponse = paths['/api/status']['get']['responses']['200']['content']['application/json'];
export type FEPStateResponse = paths['/api/fep/state']['get']['responses']['200']['content']['application/json'];
export type FEPDashboardResponse = paths['/api/fep/dashboard']['get']['responses']['200']['content']['application/json'];
export type GnosisSearchResponse = paths['/api/gnosis/search']['get']['responses']['200']['content']['application/json'];
export type DendronReportResponse = paths['/api/dendron/report']['get']['responses']['200']['content']['application/json'];

export const api = {
    health: () => apiFetch<HealthCheckResponse>('/api/status/health'),
    status: () => apiFetch<HealthReportResponse>('/api/status'),
    fepState: () => apiFetch<FEPStateResponse>('/api/fep/state'),
    fepDashboard: () => apiFetch<FEPDashboardResponse>('/api/fep/dashboard'),
    gnosisSearch: (q: string, limit = 10) => apiFetch<GnosisSearchResponse>(`/api/gnosis/search?q=${encodeURIComponent(q)}&limit=${limit}`),
    dendronReport: (detail: 'summary' | 'full' = 'summary') => apiFetch<DendronReportResponse>(`/api/dendron/report?detail=${detail}`),
};
