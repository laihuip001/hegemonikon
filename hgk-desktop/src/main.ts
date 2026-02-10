import { api } from './api/client';
import { renderGraph3D } from './views/graph3d';
import type {
  HealthReportResponse,
  FEPStateResponse,
  FEPStepResponse,
  FEPDashboardResponse,
  GnosisSearchResponse,
  GnosisStatsResponse,
  DendronReportResponse,
  SELListResponse,
  Notification,
  PKSPushResponse,
  PKSNugget,
  PKSStatsResponse,
  PaperCard,
  GnosisPapersResponse,
  GnosisNarrateResponse,
  KIListItem,
  KIDetail,
} from './api/client';
import { kiList, kiGet, kiCreate, kiUpdate, kiDelete, kiSearch } from './api/client';
import { marked } from 'marked';
import { recordView, renderUsageCard } from './telemetry';
import { initCommandPalette } from './command_palette';
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
  'graph': renderGraph3D,
  'notifications': renderNotifications,
  'pks': renderPKS,
  'sophia': renderSophiaView,
};

let currentRoute = '';

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  navigate('dashboard');
  // Start global badge polling
  void updateNotifBadge();
  setInterval(() => { void updateNotifBadge(); }, 60_000);
  // PKS auto-push on startup (fire-and-forget)
  void api.pksTriggerPush().catch(() => { /* silent */ });
  // CCL Command Palette — Ctrl+K
  initCommandPalette();
});

function setupNavigation(): void {
  document.querySelectorAll('nav button').forEach(btn => {
    btn.addEventListener('click', () => {
      const route = btn.getAttribute('data-route');
      if (route) navigate(route);
    });
  });
}

// ─── Nav Badge (CRITICAL count) ──────────────────────────────

async function updateNotifBadge(): Promise<void> {
  try {
    const criticals = await api.notifications(100, 'CRITICAL');
    const count = criticals.length;
    const notifBtn = document.querySelector('nav button[data-route="notifications"]');
    if (!notifBtn) return;
    // Remove existing badge
    const existing = notifBtn.querySelector('.nav-badge');
    if (existing) existing.remove();
    if (count > 0) {
      const badge = document.createElement('span');
      badge.className = 'nav-badge';
      badge.textContent = String(count);
      notifBtn.appendChild(badge);
    }
  } catch { /* silent */ }
}

function navigate(route: string): void {
  if (route === currentRoute) return;
  currentRoute = route;
  clearPolling();
  recordView(route);

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
  const [health, healthCheck, fep, gnosisStats, criticals] = await Promise.all([
    api.status().catch((): null => null),
    api.health().catch((): null => null),
    api.fepState().catch((): null => null),
    api.gnosisStats().catch((): null => null),
    api.notifications(5, 'CRITICAL').catch((): Notification[] => []),
  ]);

  const app = document.getElementById('view-content')!;
  if (currentRoute !== 'dashboard') return;

  const score = health ? health.score : 0;
  const scoreClass = score >= 0.8 ? 'status-ok' : score >= 0.5 ? 'status-warn' : 'status-error';
  const healthStatus = health
    ? `<span class="${scoreClass}">稼働中 (${score.toFixed(2)})</span>`
    : '<span class="status-error">オフライン</span>';

  const historyLen = fep ? fep.history_length : '-';
  const uptimeSec = healthCheck?.uptime_seconds ?? 0;
  const uptimeDisplay = uptimeSec >= 3600 ? `${(uptimeSec / 3600).toFixed(1)}時間`
    : uptimeSec >= 60 ? `${Math.floor(uptimeSec / 60)}分`
      : `${Math.floor(uptimeSec)}秒`;

  const gnosisCount = gnosisStats?.total ?? '-';

  // CRITICAL alert widget
  const alertHtml = criticals.length > 0 ? `
    <div class="card dashboard-alert">
      <div class="dashboard-alert-title">🚨 緊急通知 ${criticals.length}件</div>
      ${criticals.slice(0, 3).map((n: Notification) => `
        <div class="dashboard-alert-item">
          <strong>${esc(n.title)}</strong>
          <span class="notif-time"> — ${esc(relativeTime(n.timestamp))}</span>
        </div>
      `).join('')}
      ${criticals.length > 3 ? `<div class="dashboard-alert-item" style="color:#8b949e;">他 ${criticals.length - 3}件...</div>` : ''}
    </div>
  ` : '';

  app.innerHTML = `
    <h1>ダッシュボード <small class="poll-badge">自動更新 60秒</small></h1>
    ${alertHtml}
    <div class="grid">
      <div class="card">
        <h3>システム状態</h3>
        <div class="metric">${healthStatus}</div>
        <p>稼働時間: ${esc(uptimeDisplay)}</p>
      </div>
      <div class="card">
        <h3>FEP エージェント</h3>
        <div class="metric">${String(historyLen)} <small>ステップ</small></div>
        <p>能動推論の履歴</p>
      </div>
      <div class="card">
        <h3>Gnōsis</h3>
        <div class="metric">${String(gnosisCount)} <small>論文</small></div>
        <p>知識基盤</p>
      </div>
    </div>
    ${renderHealthItems(health)}
    ${renderUsageCard()}
  `;
}

function renderHealthItems(health: HealthReportResponse | null): string {
  if (!health) return '';
  return `
    <div class="card" style="margin-top: 1rem;">
      <h3>サービス詳細</h3>
      <table class="data-table">
        <thead><tr><th>サービス</th><th>状態</th><th>詳細</th></tr></thead>
        <tbody>
          ${health.items.map((item: HealthReportResponse['items'][number]) => {
    const cls = item.status === 'ok' ? 'status-ok' : item.status === 'warn' ? 'status-warn' : 'status-error';
    const statusJa = item.status === 'ok' ? '正常' : item.status === 'warn' ? '注意' : 'エラー';
    return `<tr>
              <td>${esc(item.emoji)} ${esc(item.name)}</td>
              <td class="${cls}">${esc(statusJa)}</td>
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

// ─── Gnōsis Narrator ─── kalon: 知識は問いとして走ってくる ──

function renderPaperCard(p: PaperCard): string {
  const score = p.relevance_score > 0
    ? `<span class="nr-score">${(p.relevance_score * 100).toFixed(0)}%</span>`
    : '';
  const topics = p.topics.length > 0
    ? p.topics.slice(0, 3).map(t => `<span class="nr-tag">${esc(t)}</span>`).join('')
    : '';
  return `
    <div class="nr-card" data-title="${esc(p.title)}">
      <div class="nr-card-header">
        <h3 class="nr-title">${esc(p.title)}</h3>
        ${score}
      </div>
      ${p.authors ? `<div class="nr-authors">${esc(p.authors)}</div>` : ''}
      ${topics ? `<div class="nr-topics">${topics}</div>` : ''}
      ${p.abstract ? `<p class="nr-abstract">${esc(p.abstract.substring(0, 200))}${p.abstract.length > 200 ? '...' : ''}</p>` : ''}
      ${p.question ? `<div class="nr-question">💡 ${esc(p.question)}</div>` : ''}
      <div class="nr-actions">
        <button class="btn btn-sm nr-narrate-btn" data-title="${esc(p.title)}" data-fmt="deep_dive">🎙️ Narrate</button>
        <button class="btn btn-sm btn-outline nr-narrate-btn" data-title="${esc(p.title)}" data-fmt="brief">📝 Brief</button>
        <button class="btn btn-sm btn-outline nr-narrate-btn" data-title="${esc(p.title)}" data-fmt="critique">🔍 Critique</button>
      </div>
      <div class="nr-narration" style="display:none;"></div>
    </div>
  `;
}

async function handleNarrate(btn: HTMLButtonElement): Promise<void> {
  const title = btn.dataset.title ?? '';
  const fmt = btn.dataset.fmt ?? 'deep_dive';
  const card = btn.closest('.nr-card') as HTMLElement;
  const narrationDiv = card.querySelector('.nr-narration') as HTMLElement;

  narrationDiv.style.display = 'block';
  narrationDiv.innerHTML = '<div class="loading">Generating narration...</div>';

  try {
    const res: GnosisNarrateResponse = await api.gnosisNarrate(title, fmt);
    if (!res.generated || res.segments.length === 0) {
      narrationDiv.innerHTML = '<div class="nr-narration-empty">Narration not available</div>';
      return;
    }
    narrationDiv.innerHTML = `
      <div class="nr-narration-header">${esc(res.icon)} ${esc(res.fmt.toUpperCase())}</div>
      ${res.segments.map(s => `
        <div class="nr-segment">
          <span class="nr-speaker">${esc(s.speaker)}:</span>
          <span class="nr-content">${esc(s.content)}</span>
        </div>
      `).join('')}
    `;
  } catch (e) {
    narrationDiv.innerHTML = `<div class="status-error">Narration failed: ${esc((e as Error).message)}</div>`;
  }
}

async function renderGnosis(): Promise<void> {
  let stats: GnosisStatsResponse | null = null;
  try {
    stats = await api.gnosisStats();
  } catch { /* ok */ }

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
        <button id="gnosis-search-btn" class="btn">🔍 Search</button>
        <button id="gnosis-papers-btn" class="btn btn-outline">📚 Papers</button>
      </div>
    </div>
    <div id="search-results"></div>
  `;

  const searchBtn = document.getElementById('gnosis-search-btn')!;
  const papersBtn = document.getElementById('gnosis-papers-btn')!;
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

  const loadPapers = async (): Promise<void> => {
    const query = searchInput.value.trim();
    const resultsDiv = document.getElementById('search-results')!;
    resultsDiv.innerHTML = '<div class="loading">Loading papers...</div>';
    try {
      const res: GnosisPapersResponse = await api.gnosisPapers(query, 20);
      if (res.papers.length === 0) {
        resultsDiv.innerHTML = '<div class="card">No papers found.</div>';
        return;
      }
      resultsDiv.innerHTML = `
        <div class="nr-header">📚 ${res.total} papers ${query ? `matching "${esc(query)}"` : ''}</div>
        ${res.papers.map(p => renderPaperCard(p)).join('')}
      `;
      // Bind narrate buttons
      resultsDiv.querySelectorAll('.nr-narrate-btn').forEach(btn => {
        btn.addEventListener('click', () => void handleNarrate(btn as HTMLButtonElement));
      });
    } catch (e) {
      resultsDiv.innerHTML = `<div class="card status-error">Papers load failed: ${esc((e as Error).message)}</div>`;
    }
  };

  searchBtn.addEventListener('click', doSearch);
  papersBtn.addEventListener('click', () => void loadPapers());
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

// ─── Notifications ───────────────────────────────────────────────

function relativeTime(isoTimestamp: string): string {
  const now = Date.now();
  const then = new Date(isoTimestamp).getTime();
  const diffSec = Math.floor((now - then) / 1000);
  if (diffSec < 60) return `${diffSec}秒前`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}分前`;
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour}時間前`;
  const diffDay = Math.floor(diffHour / 24);
  return `${diffDay}日前`;
}

const LEVEL_LABELS: Record<string, string> = {
  CRITICAL: '🚨 緊急',
  HIGH: '⚠️ 重要',
  INFO: 'ℹ️ 情報',
};

/** Parse body text into structured meta tags + remaining text */
function formatNotifBody(body: string): string {
  const lines = body.split('\n');
  const metaTags: string[] = [];
  const textLines: string[] = [];

  for (const line of lines) {
    const match = line.match(/^([A-Za-z_]+):\s*(.+)$/);
    if (match) {
      metaTags.push(`<span class="notif-meta-tag"><strong>${esc(match[1])}</strong> ${esc(match[2])}</span>`);
    } else if (line.trim()) {
      textLines.push(esc(line));
    }
  }

  let html = '';
  if (textLines.length > 0) {
    html += `<div class="notif-body-text">${textLines.join('<br>')}</div>`;
  }
  if (metaTags.length > 0) {
    html += `<div class="notif-meta-row">${metaTags.join('')}</div>`;
  }
  return html;
}

let notifLevelFilter = '';

async function renderNotifications(): Promise<void> {
  await renderNotificationsContent();
  startPolling(renderNotificationsContent, 30_000);
}

async function renderNotificationsContent(): Promise<void> {
  let notifications: Notification[] = [];
  try {
    notifications = await api.notifications(
      50,
      notifLevelFilter || undefined,
    );
  } catch (err) {
    const app = document.getElementById('view-content')!;
    if (currentRoute !== 'notifications') return;
    app.innerHTML = `<div class="card status-error">通知を取得できません: ${esc((err as Error).message)}</div>`;
    return;
  }

  // Merge PKS nuggets as virtual notifications
  const pksNuggets = await api.pksPush().catch((): null => null);
  if (pksNuggets && pksNuggets.nuggets.length > 0) {
    const pksAsNotifs: Notification[] = pksNuggets.nuggets.map((n) => ({
      id: `pks-${n.title.slice(0, 20)}`,
      timestamp: pksNuggets.timestamp,
      source: '📡 PKS',
      level: 'INFO' as const,
      title: n.title,
      body: (n.push_reason ? `💡 ${n.push_reason}\n` : '') +
        (n.abstract ? n.abstract.substring(0, 200) : '') +
        (n.relevance_score ? `\nRelevance: ${(n.relevance_score * 100).toFixed(0)}%` : ''),
      data: { pks: true, relevance_score: n.relevance_score },
    }));
    // Prepend PKS notifications (most recent first)
    notifications = [...pksAsNotifs, ...notifications];
  }

  const app = document.getElementById('view-content')!;
  if (currentRoute !== 'notifications') return;

  const cardsHtml = notifications.length === 0
    ? '<div class="notif-empty">📭 通知はありません</div>'
    : notifications.map((n: Notification) => {
      const levelClass = n.level.toLowerCase();
      const levelLabel = LEVEL_LABELS[n.level] ?? n.level;
      return `
          <div class="card notif-card level-${levelClass}">
            <div class="notif-top">
              <span class="notif-source">${esc(n.source)}</span>
              <span class="notif-level ${levelClass}">${esc(levelLabel)}</span>
              <span class="notif-time">${esc(relativeTime(n.timestamp))}</span>
            </div>
            <div class="notif-title">${esc(n.title)}</div>
            <div class="notif-body">${formatNotifBody(n.body)}</div>
          </div>`;
    }).join('');

  app.innerHTML = `
    <div class="notif-header">
      <h1>🔔 通知 <small class="poll-badge">自動更新 30秒</small></h1>
      <select id="notif-level-filter" class="input" style="width:130px;">
        <option value="">すべて</option>
        <option value="CRITICAL" ${notifLevelFilter === 'CRITICAL' ? 'selected' : ''}>🚨 緊急</option>
        <option value="HIGH" ${notifLevelFilter === 'HIGH' ? 'selected' : ''}>⚠️ 重要</option>
        <option value="INFO" ${notifLevelFilter === 'INFO' ? 'selected' : ''}>ℹ️ 情報</option>
      </select>
      <button id="notif-refresh-btn" class="btn btn-sm">更新</button>
    </div>
    ${cardsHtml}
  `;

  // Filter change handler
  document.getElementById('notif-level-filter')?.addEventListener('change', (e) => {
    notifLevelFilter = (e.target as HTMLSelectElement).value;
    void renderNotificationsContent();
  });

  // Manual refresh
  document.getElementById('notif-refresh-btn')?.addEventListener('click', () => {
    void renderNotificationsContent();
  });
}

// ─── PKS (Proactive Knowledge Surface) ───────────────────────

async function renderPKS(): Promise<void> {
  await renderPKSContent();
  startPolling(renderPKSContent, 30_000);
}

async function renderPKSContent(): Promise<void> {
  let push: PKSPushResponse | null = null;
  let stats: PKSStatsResponse | null = null;
  try {
    [push, stats] = await Promise.all([
      api.pksPush().catch((): null => null),
      api.pksStats().catch((): null => null),
    ]);
  } catch { /* ok */ }

  const app = document.getElementById('view-content')!;
  if (currentRoute !== 'pks') return;

  // --- Stats cards ---
  const statsHtml = stats && stats.total_feedbacks > 0 ? `
    <div class="grid" style="margin-bottom:1rem;">
      <div class="card">
        <h3>フィードバック総数</h3>
        <div class="metric">${stats.total_feedbacks}</div>
      </div>
      ${Object.entries(stats.series_stats).map(([k, v]) => `
        <div class="card">
          <h3>${esc(k)}</h3>
          <div style="font-size:0.9rem;">
            件数: <strong>${(v as Record<string, number>).count ?? 0}</strong><br/>
            平均スコア: <strong>${((v as Record<string, number>).avg_score ?? 0).toFixed(2)}</strong>
          </div>
        </div>
      `).join('')}
    </div>
  ` : '';

  // --- Nugget cards ---
  const nuggetsHtml = push && push.nuggets.length > 0
    ? push.nuggets.map((n: PKSNugget) => {
      const scoreClass = n.relevance_score >= 0.7 ? 'status-ok'
        : n.relevance_score >= 0.5 ? 'status-warn' : '';
      return `
          <div class="card pks-nugget" data-title="${esc(n.title)}">
            <div class="pks-nugget-header">
              <span class="pks-score ${scoreClass}">${(n.relevance_score * 100).toFixed(0)}%</span>
              <span class="pks-source">${esc(n.source)}</span>
              ${n.serendipity_score > 0.3 ? '<span class="pks-serendipity">✨ セレンディピティ</span>' : ''}
            </div>
            <div class="pks-title">${esc(n.title)}</div>
            ${n.push_reason ? `<div class="pks-reason">💡 ${esc(n.push_reason)}</div>` : ''}
            ${n.abstract ? `<div class="pks-abstract">${esc(n.abstract.substring(0, 300))}${n.abstract.length > 300 ? '...' : ''}</div>` : ''}
            ${n.authors ? `<div class="pks-meta">👤 ${esc(n.authors)}</div>` : ''}
            ${n.url ? `<div class="pks-meta"><a href="${esc(n.url)}" target="_blank" rel="noopener">📎 開く</a></div>` : ''}
            ${n.suggested_questions.length > 0 ? `
              <div class="pks-questions">
                <strong>❓ 探求すべき問い:</strong>
                <ul>${n.suggested_questions.map(q => `<li>${esc(q)}</li>`).join('')}</ul>
              </div>
            ` : ''}
            <div class="pks-feedback-row">
              <button class="btn btn-sm pks-fb-btn" data-reaction="used">👍 活用した</button>
              <button class="btn btn-sm pks-fb-btn" data-reaction="deepened">🔬 深掘りした</button>
              <button class="btn btn-sm pks-fb-btn" data-reaction="dismissed">👎 不要</button>
            </div>
          </div>`;
    }).join('')
    : '<div class="notif-empty">📭 プッシュされた知識はありません</div>';

  // --- Topics ---
  const topicsHtml = push && push.topics.length > 0
    ? `<div class="pks-topics">${push.topics.map(t => `<span class="pks-topic-tag">${esc(t)}</span>`).join('')}</div>`
    : '';

  app.innerHTML = `
    <div class="notif-header">
      <h1>📡 知識プッシュ <small class="poll-badge">自動更新 30秒</small></h1>
      <button id="pks-trigger-btn" class="btn">プッシュ実行</button>
      <button id="pks-refresh-btn" class="btn btn-sm">更新</button>
    </div>
    ${topicsHtml}
    ${statsHtml}
    <div id="pks-nuggets">${nuggetsHtml}</div>
  `;

  // --- Event handlers ---

  // Trigger push
  document.getElementById('pks-trigger-btn')?.addEventListener('click', async () => {
    const btn = document.getElementById('pks-trigger-btn') as HTMLButtonElement;
    btn.disabled = true;
    btn.textContent = 'プッシュ中...';
    try {
      await api.pksTriggerPush();
      void renderPKSContent();
    } catch (e) {
      btn.textContent = `エラー: ${(e as Error).message}`;
    }
  });

  // Refresh
  document.getElementById('pks-refresh-btn')?.addEventListener('click', () => {
    void renderPKSContent();
  });

  // Feedback buttons
  document.querySelectorAll('.pks-fb-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const target = e.currentTarget as HTMLButtonElement;
      const reaction = target.dataset.reaction ?? '';
      const nuggetCard = target.closest('.pks-nugget') as HTMLElement;
      const title = nuggetCard?.dataset.title ?? '';

      target.disabled = true;
      target.textContent = '...';
      try {
        await api.pksFeedback(title, reaction);
        // Visually confirm
        const row = target.closest('.pks-feedback-row') as HTMLElement;
        if (row) {
          const reactionLabel = reaction === 'used' ? '✅ 活用した' : reaction === 'deepened' ? '✅ 深掘りした' : '✅ 不要';
          row.innerHTML = `<span class="status-ok">${reactionLabel}</span>`;
        }
      } catch {
        target.textContent = '❌';
      }
    });
  });
}

// ─── Sophia KI ───────────────────────────────────────────────

async function renderSophiaView(): Promise<void> {
  const app = document.getElementById('view-content');
  if (!app) return;

  app.innerHTML = `
    <div class="sophia-view">
      <div class="sophia-header">
        <h2>📚 Sophia KI — Knowledge Items</h2>
        <div class="sophia-toolbar">
          <div class="sophia-search-wrap">
            <input type="text" id="sophia-search" class="sophia-search" placeholder="🔍 KI を検索..." />
            <button id="sophia-search-btn" class="btn btn-sm">検索</button>
          </div>
          <button id="sophia-create-btn" class="btn btn-primary">＋ 新規 KI</button>
        </div>
      </div>
      <div class="sophia-layout">
        <div class="sophia-sidebar" id="sophia-ki-list">
          <div class="loading">Loading...</div>
        </div>
        <div class="sophia-main" id="sophia-detail">
          <div class="sophia-empty">← KI を選択してください</div>
        </div>
      </div>
    </div>
  `;

  await renderKIList();
  setupSophiaEvents();
}

async function renderKIList(searchQuery?: string): Promise<void> {
  const listEl = document.getElementById('sophia-ki-list');
  if (!listEl) return;

  try {
    let items: KIListItem[];
    if (searchQuery && searchQuery.trim()) {
      const res = await kiSearch(searchQuery);
      items = res.results.map(r => ({
        id: r.id,
        title: r.title,
        source_type: 'ki',
        updated: '',
        created: '',
        size_bytes: 0,
      }));
    } else {
      const res = await kiList();
      items = res.items;
    }

    if (items.length === 0) {
      listEl.innerHTML = `<div class="sophia-empty">${searchQuery ? '検索結果なし' : 'KI がまだありません'}</div>`;
      return;
    }

    listEl.innerHTML = items.map(ki => `
      <div class="sophia-ki-item" data-ki-id="${esc(ki.id)}">
        <div class="sophia-ki-title">${esc(ki.title)}</div>
        <div class="sophia-ki-meta">
          <span class="sophia-ki-type">${esc(ki.source_type)}</span>
          ${ki.updated ? `<span class="sophia-ki-date">${new Date(ki.updated).toLocaleDateString('ja-JP')}</span>` : ''}
          ${ki.size_bytes ? `<span class="sophia-ki-size">${Math.round(ki.size_bytes / 1024)}KB</span>` : ''}
        </div>
      </div>
    `).join('');

    listEl.querySelectorAll('.sophia-ki-item').forEach(el => {
      el.addEventListener('click', () => {
        const kiId = (el as HTMLElement).dataset.kiId;
        if (kiId) void renderKIDetail(kiId);
        listEl.querySelectorAll('.sophia-ki-item').forEach(e => e.classList.remove('active'));
        el.classList.add('active');
      });
    });
  } catch (err) {
    listEl.innerHTML = `<div class="status-error">KI 一覧の取得に失敗: ${esc((err as Error).message)}</div>`;
  }
}

async function renderKIDetail(kiId: string): Promise<void> {
  const detailEl = document.getElementById('sophia-detail');
  if (!detailEl) return;

  detailEl.innerHTML = '<div class="loading">Loading...</div>';

  try {
    const ki = await kiGet(kiId);
    const htmlContent = marked.parse(ki.content) as string;

    detailEl.innerHTML = `
      <div class="sophia-detail-header">
        <h3>${esc(ki.title)}</h3>
        <div class="sophia-detail-actions">
          <button class="btn btn-sm" id="sophia-edit-btn" data-ki-id="${esc(ki.id)}">✏️ 編集</button>
          <button class="btn btn-sm btn-danger" id="sophia-delete-btn" data-ki-id="${esc(ki.id)}">🗑️ 削除</button>
        </div>
      </div>
      <div class="sophia-detail-meta">
        <span>Type: ${esc(ki.source_type)}</span>
        ${ki.created ? `<span>Created: ${new Date(ki.created).toLocaleString('ja-JP')}</span>` : ''}
        ${ki.updated ? `<span>Updated: ${new Date(ki.updated).toLocaleString('ja-JP')}</span>` : ''}
        <span>${Math.round(ki.size_bytes / 1024)}KB</span>
      </div>
      ${ki.backlinks.length > 0 ? `
        <div class="sophia-backlinks">
          <strong>🔗 Backlinks:</strong>
          ${ki.backlinks.map(bl => `<a href="#" class="sophia-backlink" data-ki-id="${esc(bl)}">${esc(bl)}</a>`).join(', ')}
        </div>
      ` : ''}
      <div class="sophia-content">${htmlContent}</div>
    `;

    document.getElementById('sophia-edit-btn')?.addEventListener('click', () => {
      void renderKIEditor(ki);
    });

    document.getElementById('sophia-delete-btn')?.addEventListener('click', async () => {
      if (!confirm(`「${ki.title}」を削除しますか？\n（.trash/ に移動されます）`)) return;
      try {
        await kiDelete(ki.id);
        await renderKIList();
        detailEl.innerHTML = '<div class="sophia-empty">KI を削除しました</div>';
      } catch (err) {
        alert(`削除に失敗: ${(err as Error).message}`);
      }
    });

    detailEl.querySelectorAll('.sophia-backlink').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        const id = (el as HTMLElement).dataset.kiId;
        if (id) void renderKIDetail(id);
      });
    });
  } catch (err) {
    detailEl.innerHTML = `<div class="status-error">KI の取得に失敗: ${esc((err as Error).message)}</div>`;
  }
}

async function renderKIEditor(ki?: KIDetail): Promise<void> {
  const detailEl = document.getElementById('sophia-detail');
  if (!detailEl) return;

  const isNew = !ki;
  const title = ki?.title ?? '';
  const content = ki?.content ?? '';

  detailEl.innerHTML = `
    <div class="sophia-editor">
      <h3>${isNew ? '📝 新規 KI 作成' : `✏️ 編集: ${esc(title)}`}</h3>
      <div class="sophia-editor-form">
        <label>タイトル</label>
        <input type="text" id="sophia-editor-title" class="sophia-input" value="${esc(title)}" placeholder="KI タイトル..." />
        <label>本文 (Markdown)</label>
        <textarea id="sophia-editor-content" class="sophia-textarea" rows="20" placeholder="Markdown で記述...">${esc(content)}</textarea>
        <div class="sophia-editor-actions">
          <button id="sophia-save-btn" class="btn btn-primary">${isNew ? '作成' : '保存'}</button>
          <button id="sophia-cancel-btn" class="btn btn-sm">キャンセル</button>
          <button id="sophia-preview-btn" class="btn btn-sm">👁️ プレビュー</button>
        </div>
        <div id="sophia-preview-area" class="sophia-content" style="display:none;"></div>
      </div>
    </div>
  `;

  document.getElementById('sophia-save-btn')?.addEventListener('click', async () => {
    const newTitle = (document.getElementById('sophia-editor-title') as HTMLInputElement)?.value;
    const newContent = (document.getElementById('sophia-editor-content') as HTMLTextAreaElement)?.value;

    if (!newTitle || !newTitle.trim()) {
      alert('タイトルは必須です');
      return;
    }

    try {
      if (isNew) {
        const created = await kiCreate({ title: newTitle, content: newContent });
        await renderKIList();
        void renderKIDetail(created.id);
      } else {
        await kiUpdate(ki!.id, { title: newTitle, content: newContent });
        await renderKIList();
        void renderKIDetail(ki!.id);
      }
    } catch (err) {
      alert(`保存に失敗: ${(err as Error).message}`);
    }
  });

  document.getElementById('sophia-cancel-btn')?.addEventListener('click', () => {
    if (ki) {
      void renderKIDetail(ki.id);
    } else {
      detailEl.innerHTML = '<div class="sophia-empty">← KI を選択してください</div>';
    }
  });

  document.getElementById('sophia-preview-btn')?.addEventListener('click', () => {
    const previewArea = document.getElementById('sophia-preview-area');
    const contentEl = document.getElementById('sophia-editor-content') as HTMLTextAreaElement;
    if (previewArea && contentEl) {
      const visible = previewArea.style.display !== 'none';
      if (visible) {
        previewArea.style.display = 'none';
      } else {
        previewArea.innerHTML = marked.parse(contentEl.value) as string;
        previewArea.style.display = 'block';
      }
    }
  });
}

function setupSophiaEvents(): void {
  const searchBtn = document.getElementById('sophia-search-btn');
  const searchInput = document.getElementById('sophia-search') as HTMLInputElement;

  searchBtn?.addEventListener('click', () => {
    void renderKIList(searchInput?.value);
  });

  searchInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      void renderKIList(searchInput.value);
    }
  });

  document.getElementById('sophia-create-btn')?.addEventListener('click', () => {
    void renderKIEditor();
  });
}
