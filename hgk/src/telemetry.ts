/**
 * Telemetry — ビュー使用頻度の記録
 *
 * localStorage にルート別のアクセスカウントと最終アクセス時刻を保存。
 * 30日以上経過したデータは自動パージ。
 */

const STORAGE_KEY = 'hgk_telemetry';
const MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000; // 30 days

interface ViewRecord {
    count: number;
    lastAccess: string; // ISO 8601
    firstAccess: string;
}

interface TelemetryData {
    views: Record<string, ViewRecord>;
    totalNavigations: number;
    sessionStart: string;
}

function load(): TelemetryData {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw) as TelemetryData;
    } catch { /* corrupt data */ }
    return {
        views: {},
        totalNavigations: 0,
        sessionStart: new Date().toISOString(),
    };
}

function save(data: TelemetryData): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

/** Record a view navigation event */
export function recordView(route: string): void {
    const data = load();
    const now = new Date().toISOString();

    if (!data.views[route]) {
        data.views[route] = { count: 0, lastAccess: now, firstAccess: now };
    }

    data.views[route].count++;
    data.views[route].lastAccess = now;
    data.totalNavigations++;

    // Purge old entries
    const cutoff = Date.now() - MAX_AGE_MS;
    for (const [key, record] of Object.entries(data.views)) {
        if (new Date(record.lastAccess).getTime() < cutoff) {
            delete data.views[key];
        }
    }

    save(data);
}

/** Get telemetry statistics */
export function getStats(): TelemetryData {
    return load();
}

/** Render a usage card HTML string for the Dashboard */
export function renderUsageCard(): string {
    const data = load();
    const entries = Object.entries(data.views)
        .sort(([, a], [, b]) => b.count - a.count);

    if (entries.length === 0) {
        return `
      <div class="card telemetry-card">
        <h3>📊 View Usage</h3>
        <div class="telemetry-empty">まだ使用データがありません</div>
      </div>`;
    }

    const maxCount = entries[0]?.[1].count ?? 1;
    const bars = entries.map(([route, rec]) => {
        const pct = Math.round((rec.count / maxCount) * 100);
        return `
      <div class="telemetry-row">
        <span class="telemetry-route">${escTel(route)}</span>
        <div class="telemetry-bar-bg">
          <div class="telemetry-bar" style="width:${pct}%"></div>
        </div>
        <span class="telemetry-count">${rec.count}</span>
      </div>`;
    }).join('');

    return `
    <div class="card telemetry-card">
      <h3>📊 View Usage</h3>
      <div class="telemetry-total">Total: ${data.totalNavigations} navigations</div>
      ${bars}
    </div>`;
}

function escTel(s: string): string {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}
