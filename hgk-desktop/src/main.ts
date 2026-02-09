import { api } from './api/client';
import type {
  HealthReportResponse,
  FEPStateResponse,
  FEPStepResponse,
  FEPDashboardResponse,
  GnosisSearchResponse,
  GnosisStatsResponse,
  DendronReportResponse,
  SELListResponse,
} from './api/client';
import './styles.css';

// ─── Utilities ───────────────────────────────────────────────

/** Escape HTML to prevent XSS */
function esc(s: string | undefined | null): string {
  if (!s) return '';
  return s.replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ─── Polling Manager (S5) ────────────────────────────────────

let pollingTimers: ReturnType<typeof setInterval>[] = [];

function clearPolling(): void {
  pollingTimers.forEach(t => clearInterval(t));
  pollingTimers = [];
}

function startPolling(fn: () => Promise<void>, intervalMs: number): void {
  const timer = setInterval(() => { void fn(); }, intervalMs);
  pollingTimers.push(timer);
}

// ─── Router ──────────────────────────────────────────────────

type ViewRenderer = () => Promise<void>;
const routes: Record<string, ViewRenderer> = {
  'dashboard': renderDashboard,
  'fep': renderFep,
  'gnosis': renderGnosis,
  'quality': renderQuality,
  'postcheck': renderPostcheck,
};

let currentRoute = '';

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  navigate('dashboard');
});

function setupNavigation(): void {
  document.querySelectorAll('nav button').forEach(btn => {
    btn.addEventListener('click', () => {
      const route = btn.getAttribute('data-route');
      if (route) navigate(route);
    });
  });
}

function navigate(route: string): void {
  if (route === currentRoute) return;
  currentRoute = route;
  clearPolling();

  document.querySelectorAll('nav button').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-route') === route);
  });

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

// ─── Dashboard ───────────────────────────────────────────────

async function renderDashboard(): Promise<void> {
  await renderDashboardContent();
  startPolling(renderDashboardContent, 60_000); // S5: 60s polling
}

async function renderDashboardContent(): Promise<void> {
  const [health, fep, gnosisStats] = await Promise.all([
    api.status().catch((): null => null),
    api.fepState().catch((): null => null),
    api.gnosisStats().catch((): null => null),
  ]);

  const app = document.getElementById('view-content')!;
  if (currentRoute !== 'dashboard') return; // guard against stale render

  const score = health ? health.score : 0;
  const scoreClass = score >= 0.8 ? 'status-ok' : score >= 0.5 ? 'status-warn' : 'status-error';
  const healthStatus = health
    ? `<span class="${scoreClass}">Online (${score.toFixed(2)})</span>`
    : '<span class="status-error">Offline</span>';

  const historyLen = fep ? fep.history_length : '-';
  const uptimeItem = health?.items.find((i: HealthReportResponse['items'][number]) => i.name === 'uptime');
  const uptimeSec = uptimeItem?.metric?.toFixed(0) ?? '0';

  const gnosisCount = gnosisStats?.total ?? '-';

  app.innerHTML = `
    <h1>Dashboard <small class="poll-badge">auto-refresh 60s</small></h1>
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
      <div class="card">
        <h3>Gnōsis</h3>
        <div class="metric">${String(gnosisCount)} <small>papers</small></div>
        <p>Knowledge Base</p>
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
      <table class="data-table">
        <thead><tr><th>Service</th><th>Status</th><th>Detail</th></tr></thead>
        <tbody>
          ${health.items.map((item: HealthReportResponse['items'][number]) => {
    const cls = item.status === 'ok' ? 'status-ok' : item.status === 'warn' ? 'status-warn' : 'status-error';
    return `<tr>
              <td>${esc(item.emoji)} ${esc(item.name)}</td>
              <td class="${cls}">${esc(item.status)}</td>
              <td>${esc(item.detail)}</td>
            </tr>`;
  }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ─── FEP Agent (S6: Step UI + S5: 30s polling) ──────────────

async function renderFep(): Promise<void> {
  await renderFepContent();
  startPolling(renderFepContent, 30_000); // S5: 30s polling
}

async function renderFepContent(): Promise<void> {
  let state: FEPStateResponse;
  let dashboard: FEPDashboardResponse | null = null;
  try {
    [state, dashboard] = await Promise.all([
      api.fepState(),
      api.fepDashboard().catch((): null => null),
    ]);
  } catch (err) {
    const app = document.getElementById('view-content')!;
    app.innerHTML = `<div class="card status-error">FEP Agent unavailable: ${esc((err as Error).message)}</div>`;
    return;
  }

  const app = document.getElementById('view-content')!;
  if (currentRoute !== 'fep') return;

  const maxBelief = Math.max(...state.beliefs, 0.01);
  const beliefsHtml = state.beliefs.map((b: number, idx: number) =>
    `<div class="belief-bar" style="height: ${(b / maxBelief) * 100}%" title="[${idx}] ${b.toFixed(4)}"></div>`
  ).join('');

  const epsilonEntries = Object.entries(state.epsilon)
    .map(([k, v]) => `<tr><td>${esc(k)}</td><td>${(v as number).toFixed(4)}</td></tr>`)
    .join('');

  // Dashboard distribution
  const actionDist = dashboard ? Object.entries(dashboard.action_distribution)
    .sort(([, a], [, b]) => (b as number) - (a as number))
    .map(([k, v]) => `<tr><td>${esc(k)}</td><td>${String(v)}</td></tr>`)
    .join('') : '';

  const seriesDist = dashboard ? Object.entries(dashboard.series_distribution)
    .sort(([, a], [, b]) => (b as number) - (a as number))
    .map(([k, v]) => `<tr><td>${esc(k)}</td><td>${String(v)}</td></tr>`)
    .join('') : '';

  app.innerHTML = `
    <h1>FEP Agent <small class="poll-badge">auto-refresh 30s</small></h1>

    <div class="card">
      <h3>Belief Distribution (${state.beliefs.length} dims)</h3>
      <div class="beliefs-chart">${beliefsHtml}</div>
      <small style="color:#8b949e;">Hover for values. Max = ${maxBelief.toFixed(4)}</small>
    </div>

    <div class="card step-panel">
      <h3>Run Inference Step</h3>
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <label for="obs-input">Observation (0-47):</label>
        <input type="number" id="obs-input" class="input" min="0" max="47" value="0" style="width:80px;" />
        <button id="step-btn" class="btn">Step</button>
      </div>
      <div id="step-result" style="margin-top:0.5rem;"></div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Epsilon</h3>
        <table class="data-table">${epsilonEntries}</table>
      </div>
      <div class="card">
        <h3>History</h3>
        <div class="metric">${state.history_length}</div>
        <p>inference steps</p>
      </div>
      ${dashboard ? `
      <div class="card">
        <h3>Action Distribution</h3>
        <table class="data-table">${actionDist || '<tr><td colspan="2">No data</td></tr>'}</table>
      </div>
      <div class="card">
        <h3>Series Distribution</h3>
        <table class="data-table">${seriesDist || '<tr><td colspan="2">No data</td></tr>'}</table>
      </div>
      ` : ''}
    </div>
  `;

  // S6: FEP Step event handler
  document.getElementById('step-btn')?.addEventListener('click', async () => {
    const obsInput = document.getElementById('obs-input') as HTMLInputElement;
    const obs = parseInt(obsInput.value, 10);
    if (isNaN(obs) || obs < 0 || obs > 47) {
      document.getElementById('step-result')!.innerHTML =
        '<span class="status-error">Observation must be 0-47</span>';
      return;
    }

    const resultDiv = document.getElementById('step-result')!;
    resultDiv.innerHTML = '<span class="loading">Running...</span>';
    try {
      const res: FEPStepResponse = await api.fepStep(obs);
      resultDiv.innerHTML = `
        <div class="step-result-box">
          <strong>Action:</strong> ${esc(res.action_name)} (idx: ${res.action_index})<br/>
          <strong>Series:</strong> ${esc(res.selected_series ?? 'N/A')}<br/>
          <strong>Entropy:</strong> ${res.beliefs_entropy?.toFixed(4) ?? '-'}<br/>
          ${res.explanation ? `<strong>Explanation:</strong> ${esc(res.explanation)}` : ''}
        </div>
      `;
      // Refresh charts after step
      void renderFepContent();
    } catch (e) {
      resultDiv.innerHTML = `<span class="status-error">Step failed: ${esc((e as Error).message)}</span>`;
    }
  });
}

// ─── Gnōsis Search ───────────────────────────────────────────

async function renderGnosis(): Promise<void> {
  let stats: GnosisStatsResponse | null = null;
  try {
    stats = await api.gnosisStats();
  } catch { /* ok, show search anyway */ }

  const app = document.getElementById('view-content')!;

  const statsHtml = stats ? `
    <div class="grid" style="margin-bottom:1rem;">
      <div class="card">
        <h3>Total Papers</h3>
        <div class="metric">${stats.total}</div>
      </div>
      <div class="card">
        <h3>Unique DOIs</h3>
        <div class="metric">${stats.unique_dois}</div>
      </div>
      <div class="card">
        <h3>Unique arXiv</h3>
        <div class="metric">${stats.unique_arxiv}</div>
      </div>
      <div class="card">
        <h3>Sources</h3>
        <div style="font-size:0.9rem;">
          ${Object.entries(stats.sources).map(([k, v]) => `${esc(k)}: <strong>${String(v)}</strong>`).join(' · ')}
        </div>
        <small>Last collected: ${esc(stats.last_collected)}</small>
      </div>
    </div>
  ` : '';

  app.innerHTML = `
    <h1>Gnōsis</h1>
    ${statsHtml}
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
  searchInput.focus();
}

// ─── Quality (Dendron) ───────────────────────────────────────

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
  const pct = s.coverage_percent ?? 0;
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

// ─── Postcheck (S7) ──────────────────────────────────────────

async function renderPostcheck(): Promise<void> {
  let selList: SELListResponse;
  try {
    selList = await api.postcheckList();
  } catch (err) {
    const app = document.getElementById('view-content')!;
    app.innerHTML = `<div class="card status-error">Postcheck unavailable: ${esc((err as Error).message)}</div>`;
    return;
  }

  const app = document.getElementById('view-content')!;

  const wfRows = selList.items.map(item => {
    const modes = Object.keys(item.modes).join(', ') || '-';
    return `<tr>
      <td>${esc(item.wf_name)}</td>
      <td>${esc(modes)}</td>
      <td><button class="btn btn-sm run-postcheck-btn" data-wf="${esc(item.wf_name)}">Run</button></td>
    </tr>`;
  }).join('');

  app.innerHTML = `
    <h1>Postcheck</h1>
    <div class="card">
      <h3>Workflow Registry (${selList.total} workflows)</h3>
      <table class="data-table">
        <thead><tr><th>Workflow</th><th>Modes</th><th>Action</th></tr></thead>
        <tbody>${wfRows}</tbody>
      </table>
    </div>
    <div class="card">
      <h3>Manual Postcheck</h3>
      <div class="grid" style="grid-template-columns: 1fr 100px;">
        <div>
          <label>Workflow name:</label>
          <input type="text" id="pc-wf" class="input" placeholder="e.g. dia, noe, boot" style="margin-bottom:0.5rem;" />
          <label>Content to check:</label>
          <textarea id="pc-content" class="input" rows="4" placeholder="Paste output text here..."></textarea>
        </div>
        <div style="display:flex; flex-direction:column; gap:0.5rem;">
          <label>Mode:</label>
          <select id="pc-mode" class="input">
            <option value="">default</option>
            <option value="+">+ (deep)</option>
            <option value="-">- (minimal)</option>
            <option value="*">* (meta)</option>
          </select>
          <button id="pc-run-btn" class="btn" style="margin-top:auto;">Run Check</button>
        </div>
      </div>
      <div id="pc-result" style="margin-top:1rem;"></div>
    </div>
  `;

  // Manual run handler
  document.getElementById('pc-run-btn')?.addEventListener('click', async () => {
    const wf = (document.getElementById('pc-wf') as HTMLInputElement).value.trim();
    const content = (document.getElementById('pc-content') as HTMLTextAreaElement).value.trim();
    const mode = (document.getElementById('pc-mode') as HTMLSelectElement).value;
    if (!wf || !content) {
      document.getElementById('pc-result')!.innerHTML = '<span class="status-warn">Enter workflow name and content</span>';
      return;
    }
    const resultDiv = document.getElementById('pc-result')!;
    resultDiv.innerHTML = '<span class="loading">Checking...</span>';
    try {
      const res = await api.postcheckRun(wf, content, mode);
      const passClass = res.passed ? 'status-ok' : 'status-error';
      const checksHtml = res.checks.map(c => {
        const icon = c.passed ? '✅' : '❌';
        return `<li>${icon} ${esc(c.requirement)} ${c.detail ? `— ${esc(c.detail)}` : ''}</li>`;
      }).join('');
      resultDiv.innerHTML = `
        <div class="card">
          <h3 class="${passClass}">${res.passed ? 'PASS' : 'FAIL'} — ${esc(res.wf_name)} [${esc(res.mode || 'default')}]</h3>
          <ul>${checksHtml}</ul>
        </div>
      `;
    } catch (e) {
      resultDiv.innerHTML = `<span class="status-error">Check failed: ${esc((e as Error).message)}</span>`;
    }
  });

  // Quick-run buttons in table
  document.querySelectorAll('.run-postcheck-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const wfName = btn.getAttribute('data-wf') ?? '';
      (document.getElementById('pc-wf') as HTMLInputElement).value = wfName;
      document.getElementById('pc-content')?.focus();
    });
  });
}
