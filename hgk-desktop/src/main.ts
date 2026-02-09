import { api } from './api/client';
import type { HealthReportResponse, FEPStateResponse, GnosisSearchResponse, DendronReportResponse } from './api/client';
import './styles.css';

// --- Utilities ---

/** Escape HTML to prevent XSS (S1 fix) */
function esc(s: string | undefined | null): string {
  if (!s) return '';
  return s.replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// --- Router ---

const routes: Record<string, () => Promise<void>> = {
  'dashboard': renderDashboard,
  'fep': renderFep,
  'gnosis': renderGnosis,
  'quality': renderQuality,
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  navigate('dashboard');
});

function setupNavigation(): void {
  const navButtons = document.querySelectorAll('nav button');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const route = btn.getAttribute('data-route');
      if (route) navigate(route);
    });
  });
}

function navigate(route: string): void {
  // Update Active State
  document.querySelectorAll('nav button').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-route') === route);
  });

  // Render View
  const app = document.getElementById('view-content');
  if (!app) return;

  app.innerHTML = '<div class="loading">Loading...</div>';
  const renderer = routes[route];
  if (renderer) {
    renderer().catch((err: Error) => {
      app.innerHTML = `<div class="card status-error">Error: ${esc(err.message)}</div>`;
    });
  }
}

// --- View Renderers ---

async function renderDashboard(): Promise<void> {
  const [health, fep] = await Promise.all([
    api.status().catch((): null => null),
    api.fepState().catch((): null => null),
  ]);

  const app = document.getElementById('view-content')!;

  const score = health ? health.score : 0;
  const scoreClass = score >= 0.8 ? 'status-ok' : score >= 0.5 ? 'status-warn' : 'status-error';
  const healthStatus = health
    ? `<span class="${scoreClass}">Online (Score: ${score.toFixed(2)})</span>`
    : '<span class="status-error">Offline</span>';

  const historyLen = fep ? fep.history_length : '-';
  const uptimeItem = health?.items.find((i: HealthReportResponse['items'][number]) => i.name === 'uptime');
  const uptimeSec = uptimeItem?.metric?.toFixed(0) ?? '0';

  app.innerHTML = `
    <h1>Dashboard</h1>
    <div class="grid">
      <div class="card">
        <h3>System Status</h3>
        <div class="metric">${healthStatus}</div>
        <p>Uptime: ${esc(uptimeSec)}s</p>
      </div>
      <div class="card">
        <h3>FEP Agent</h3>
        <div class="metric">${String(historyLen)} <small>steps</small></div>
        <p>Active Inference History</p>
      </div>
    </div>
    ${renderHealthItems(health)}
  `;
}

function renderHealthItems(health: HealthReportResponse | null): string {
  if (!health) return '';
  return `
    <div class="card" style="margin-top: 1rem;">
      <h3>Service Details</h3>
      <table style="width:100%; border-collapse: collapse;">
        <thead><tr>
          <th style="text-align:left; padding:0.3rem;">Service</th>
          <th style="text-align:left; padding:0.3rem;">Status</th>
          <th style="text-align:left; padding:0.3rem;">Detail</th>
        </tr></thead>
        <tbody>
          ${health.items.map((item: HealthReportResponse['items'][number]) => {
    const cls = item.status === 'ok' ? 'status-ok'
      : item.status === 'warn' ? 'status-warn' : 'status-error';
    return `<tr>
              <td style="padding:0.3rem;">${esc(item.emoji)} ${esc(item.name)}</td>
              <td style="padding:0.3rem;" class="${cls}">${esc(item.status)}</td>
              <td style="padding:0.3rem;">${esc(item.detail)}</td>
            </tr>`;
  }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function renderFep(): Promise<void> {
  let state: FEPStateResponse;
  try {
    state = await api.fepState();
  } catch (err) {
    const app = document.getElementById('view-content')!;
    app.innerHTML = `<div class="card status-error">FEP Agent unavailable: ${esc((err as Error).message)}</div>`;
    return;
  }

  const app = document.getElementById('view-content')!;
  const maxBelief = Math.max(...state.beliefs, 0.01);

  // Render Beliefs Bar Chart (normalized to max)
  const beliefsHtml = state.beliefs.map((b: number, idx: number) =>
    `<div
      class="belief-bar"
      style="height: ${(b / maxBelief) * 100}%"
      title="[${idx}] ${b.toFixed(4)}"
      role="img"
      aria-label="Belief ${idx}: ${b.toFixed(4)}"
    ></div>`
  ).join('');

  const epsilonEntries = Object.entries(state.epsilon)
    .map(([k, v]) => `<tr><td style="padding:0.2rem;">${esc(k)}</td><td style="padding:0.2rem;">${(v as number).toFixed(4)}</td></tr>`)
    .join('');

  app.innerHTML = `
    <h1>FEP Agent State</h1>
    <div class="card">
      <h3>Belief Distribution (${state.beliefs.length} dimensions)</h3>
      <div
        class="beliefs-chart"
        role="group"
        aria-label="Belief Distribution Chart"
      >${beliefsHtml}</div>
      <small style="color:#8b949e;">
        <span aria-hidden="true">Hover bars for values. </span>
        Normalized to max = ${maxBelief.toFixed(4)}
      </small>
    </div>
    <div class="grid">
      <div class="card">
        <h3>Epsilon (Precision)</h3>
        <table style="width:100%;">
          ${epsilonEntries}
        </table>
      </div>
      <div class="card">
        <h3>History</h3>
        <div class="metric">${state.history_length}</div>
        <p>inference steps</p>
      </div>
    </div>
  `;
}

async function renderGnosis(): Promise<void> {
  const app = document.getElementById('view-content')!;
  app.innerHTML = `
    <h1>Gnōsis Search</h1>
    <div class="card">
      <div style="display:flex; gap:0.5rem;">
        <input type="text" id="gnosis-search-input" class="input" placeholder="Search knowledge base..." style="flex:1;" />
        <button id="gnosis-search-btn" class="btn">Search</button>
      </div>
    </div>
    <div id="search-results"></div>
  `;

  const searchBtn = document.getElementById('gnosis-search-btn')!;
  const searchInput = document.getElementById('gnosis-search-input') as HTMLInputElement;

  const doSearch = async (): Promise<void> => {
    const query = searchInput.value.trim();
    if (!query) return;

    const resultsDiv = document.getElementById('search-results')!;
    resultsDiv.innerHTML = '<div class="loading">Searching...</div>';

    try {
      const res: GnosisSearchResponse = await api.gnosisSearch(query);
      if (res.results.length === 0) {
        resultsDiv.innerHTML = '<div class="card">No results found.</div>';
        return;
      }
      resultsDiv.innerHTML = res.results.map(r => `
        <div class="search-result card">
          <h3><a href="${esc(r.url) || '#'}" target="_blank" rel="noopener">${esc(r.title) || 'Untitled'}</a></h3>
          <p>${esc(r.abstract?.substring(0, 300))}</p>
          <small>Score: ${r.score?.toFixed(3) ?? '-'} | Source: ${esc(r.source)} | ${esc(r.authors)}</small>
        </div>
      `).join('');
    } catch (e) {
      resultsDiv.innerHTML = `<div class="card status-error">Search failed: ${esc((e as Error).message)}</div>`;
    }
  };

  searchBtn.addEventListener('click', doSearch);
  searchInput.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.key === 'Enter') void doSearch();
  });
}

async function renderQuality(): Promise<void> {
  let report: DendronReportResponse;
  try {
    report = await api.dendronReport('summary');
  } catch (err) {
    const app = document.getElementById('view-content')!;
    app.innerHTML = `<div class="card status-error">Quality report unavailable: ${esc((err as Error).message)}</div>`;
    return;
  }

  const app = document.getElementById('view-content')!;
  const s = report.summary;
  const pct = (s.coverage_percent ?? 0);
  // coverage_percent is 0.0-1.0 from API schema
  const displayPct = pct > 1 ? pct.toFixed(1) : (pct * 100).toFixed(1);
  const coverageClass = pct >= 0.7 ? 'status-ok' : pct >= 0.4 ? 'status-warn' : 'status-error';

  app.innerHTML = `
    <h1>Code Quality (Dendron)</h1>
    <div class="grid">
      <div class="card">
        <h3>Coverage</h3>
        <div class="metric ${coverageClass}">${displayPct}%</div>
        <p>${s.files_with_proof} / ${s.total_files} files verified</p>
      </div>
      <div class="card">
        <h3>Structure</h3>
        <div class="metric">${s.total_dirs}</div>
        <p>${s.dirs_with_proof} / ${s.total_dirs} dirs verified</p>
      </div>
    </div>
    ${s.issues.length > 0 ? `
      <div class="card" style="margin-top:1rem;">
        <h3>Issues (${s.issues.length})</h3>
        <ul>${s.issues.map(i => `<li>${esc(i)}</li>`).join('')}</ul>
      </div>
    ` : ''}
  `;
}
