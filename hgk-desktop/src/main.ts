import { api } from './api/client';
import { isPermissionGranted, requestPermission, sendNotification } from '@tauri-apps/plugin-notification';
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
  SymplokeSearchResponse,
  SymplokeSearchResultItem,
  TimelineEvent,
  TimelineEventDetail,
  DigestCandidate,
} from './api/client';
import { kiList, kiGet, kiCreate, kiUpdate, kiDelete, kiSearch } from './api/client';
import { marked } from 'marked';
import { recordView, renderUsageCard } from './telemetry';
import { initCommandPalette } from './command_palette';
import './styles.css';

// ─── OS Notification ─────────────────────────────────────────

/** OS通知を発火済みの通知IDを追跡 */
const sentOsNotifIds = new Set<string>();

/** CRITICAL/HIGH 通知を OS ネイティブ通知として送る */
async function fireOsNotifications(notifications: Notification[]): Promise<void> {
  try {
    let granted = await isPermissionGranted();
    if (!granted) {
      const perm = await requestPermission();
      granted = perm === 'granted';
    }
    if (!granted) return;

    for (const n of notifications) {
      if (n.level !== 'CRITICAL' && n.level !== 'HIGH') continue;
      if (sentOsNotifIds.has(n.id)) continue;
      sentOsNotifIds.add(n.id);
      sendNotification({
        title: `${n.level === 'CRITICAL' ? '🚨' : '⚠️'} ${n.title}`,
        body: n.body.substring(0, 200),
      });
    }
  } catch {
    // OS通知が利用できない環境では静かに無視
  }
}

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
  'search': renderSearch,
  'fep': renderFep,
  'gnosis': renderGnosis,
  'quality': renderQuality,
  'postcheck': renderPostcheck,
  'graph': renderGraph3D,
  'notifications': renderNotifications,
  'pks': renderPKS,
  'sophia': renderSophiaView,
  'timeline': renderTimelineView,
  'synteleia': renderSynteleiaView,
  'digestor': renderDigestorView,
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
  initKeyboardNav();
});

// ─── Keyboard Navigation (Ctrl+1‑9,0) ───────────────────────

function initKeyboardNav(): void {
  const keyRouteMap: Record<string, string> = {
    '1': 'dashboard',
    '2': 'notifications',
    '3': 'digestor',
    '4': 'search',
    '5': 'gnosis',
    '6': 'sophia',
    '7': 'pks',
    '8': 'timeline',
    '9': 'fep',
    '0': 'graph',
  };
  document.addEventListener('keydown', (e: KeyboardEvent) => {
    // Skip when typing in input/textarea/contenteditable
    const el = e.target as HTMLElement;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable) return;
    if (!e.ctrlKey || e.shiftKey || e.altKey || e.metaKey) return;
    const route = keyRouteMap[e.key];
    if (route) {
      e.preventDefault();
      navigate(route);
    }
  });
}

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
  app.innerHTML = '<div class="loading">読み込み中...</div>';

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
  const [health, healthCheck, fep, gnosisStats, criticals, kalonHist] = await Promise.all([
    api.status().catch((): null => null),
    api.health().catch((): null => null),
    api.fepState().catch((): null => null),
    api.gnosisStats().catch((): null => null),
    api.notifications(5, 'CRITICAL').catch((): Notification[] => []),
    api.kalonHistory(5).catch((): null => null),
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
      <div class="card kalon-card">
        <div class="kalon-card-header">
          <span class="kalon-card-icon">◆</span>
          <span class="kalon-card-title">Kalon</span>
        </div>
        <div class="kalon-card-equation">Kalon(x) ⟺ x = Fix(G∘F)</div>
        <div class="kalon-card-attrs">
          <span class="kalon-card-attr">判定数: <strong>${kalonHist?.total ?? 0}</strong></span>
          ${kalonHist?.judgments?.[0] ? `<span class="kalon-card-attr">最新: ${esc(kalonHist.judgments[0].verdict)} ${esc(kalonHist.judgments[0].concept)}</span>` : ''}
        </div>
        <div class="kalon-card-hint">Ctrl+K → kalon [概念] で判定</div>
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
    app.innerHTML = `<div class="card status-error">FEP エージェント利用不可: ${esc((err as Error).message)}</div>`;
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
    <h1>FEP エージェント <small class="poll-badge">自動更新 30秒</small></h1>

    <div class="card">
      <h3>信念分布 (${state.beliefs.length} 次元)</h3>
      <div class="beliefs-chart">${beliefsHtml}</div>
      <small style="color:#8b949e;">ホバーで値表示。最大値 = ${maxBelief.toFixed(4)}</small>
    </div>

    <div class="card step-panel">
      <h3>推論ステップ実行</h3>
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <label for="obs-input">観測値 (0-47):</label>
        <input type="number" id="obs-input" class="input" min="0" max="47" value="0" style="width:80px;" />
        <button id="step-btn" class="btn">ステップ</button>
      </div>
      <div id="step-result" style="margin-top:0.5rem;"></div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Epsilon</h3>
        <table class="data-table">${epsilonEntries}</table>
      </div>
      <div class="card">
        <h3>履歴</h3>
        <div class="metric">${state.history_length}</div>
        <p>推論ステップ</p>
      </div>
      ${dashboard ? `
      <div class="card">
        <h3>行動分布</h3>
        <table class="data-table">${actionDist || '<tr><td colspan="2">データなし</td></tr>'}</table>
      </div>
      <div class="card">
        <h3>シリーズ分布</h3>
        <table class="data-table">${seriesDist || '<tr><td colspan="2">データなし</td></tr>'}</table>
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
        '<span class="status-error">観測値は 0-47 の範囲で入力してください</span>';
      return;
    }

    const resultDiv = document.getElementById('step-result')!;
    resultDiv.innerHTML = '<span class="loading">実行中...</span>';
    try {
      const res: FEPStepResponse = await api.fepStep(obs);
      resultDiv.innerHTML = `
        <div class="step-result-box">
          <strong>行動:</strong> ${esc(res.action_name)} (idx: ${res.action_index})<br/>
          <strong>シリーズ:</strong> ${esc(res.selected_series ?? 'N/A')}<br/>
          <strong>エントロピー:</strong> ${res.beliefs_entropy?.toFixed(4) ?? '-'}<br/>
          ${res.explanation ? `<strong>説明:</strong> ${esc(res.explanation)}` : ''}
        </div>
      `;
      // Refresh charts after step
      void renderFepContent();
    } catch (e) {
      resultDiv.innerHTML = `<span class="status-error">ステップ失敗: ${esc((e as Error).message)}</span>`;
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
        <button class="btn btn-sm nr-narrate-btn" data-title="${esc(p.title)}" data-fmt="deep_dive">🎙️ ナレーション</button>
        <button class="btn btn-sm btn-outline nr-narrate-btn" data-title="${esc(p.title)}" data-fmt="brief">📝 概要</button>
        <button class="btn btn-sm btn-outline nr-narrate-btn" data-title="${esc(p.title)}" data-fmt="critique">🔍 批評</button>
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
  narrationDiv.innerHTML = '<div class="loading">ナレーション生成中...</div>';

  try {
    const res: GnosisNarrateResponse = await api.gnosisNarrate(title, fmt);
    if (!res.generated || res.segments.length === 0) {
      narrationDiv.innerHTML = '<div class="nr-narration-empty">ナレーション利用不可</div>';
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
    narrationDiv.innerHTML = `<div class="status-error">ナレーション失敗: ${esc((e as Error).message)}</div>`;
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
        <h3>論文総数</h3>
        <div class="metric">${stats.total}</div>
      </div>
      <div class="card">
        <h3>固有 DOI</h3>
        <div class="metric">${stats.unique_dois}</div>
      </div>
      <div class="card">
        <h3>固有 arXiv</h3>
        <div class="metric">${stats.unique_arxiv}</div>
      </div>
      <div class="card">
        <h3>ソース</h3>
        <div style="font-size:0.9rem;">
          ${Object.entries(stats.sources).map(([k, v]) => `${esc(k)}: <strong>${String(v)}</strong>`).join(' · ')}
        </div>
        <small>最終収集: ${esc(stats.last_collected)}</small>
      </div>
    </div>
  ` : '';

  app.innerHTML = `
    <h1>Gnōsis</h1>
    ${statsHtml}
    <div class="card">
      <div style="display:flex; gap:0.5rem;">
        <input type="text" id="gnosis-search-input" class="input" placeholder="知識基盤を検索..." style="flex:1;" />
        <button id="gnosis-search-btn" class="btn">🔍 検索</button>
        <button id="gnosis-papers-btn" class="btn btn-outline">📚 論文</button>
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
    resultsDiv.innerHTML = '<div class="loading">検索中...</div>';
    try {
      const res: GnosisSearchResponse = await api.gnosisSearch(query);
      if (res.results.length === 0) {
        resultsDiv.innerHTML = '<div class="card">結果が見つかりませんでした。</div>';
        return;
      }
      resultsDiv.innerHTML = res.results.map(r => `
        <div class="search-result card">
          <h3><a href="${esc(r.url) || '#'}" target="_blank" rel="noopener">${esc(r.title) || '無題'}</a></h3>
          <p>${esc(r.abstract?.substring(0, 300))}</p>
          <small>スコア: ${r.score?.toFixed(3) ?? '-'} | ソース: ${esc(r.source)} | ${esc(r.authors)}</small>
        </div>
      `).join('');
    } catch (e) {
      resultsDiv.innerHTML = `<div class="card status-error">検索失敗: ${esc((e as Error).message)}</div>`;
    }
  };

  const loadPapers = async (): Promise<void> => {
    const query = searchInput.value.trim();
    const resultsDiv = document.getElementById('search-results')!;
    resultsDiv.innerHTML = '<div class="loading">論文読み込み中...</div>';
    try {
      const res: GnosisPapersResponse = await api.gnosisPapers(query, 20);
      if (res.papers.length === 0) {
        resultsDiv.innerHTML = '<div class="card">論文が見つかりませんでした。</div>';
        return;
      }
      resultsDiv.innerHTML = `
        <div class="nr-header">📚 ${res.total} 件 ${query ? `「${esc(query)}」に一致` : ''}</div>
        ${res.papers.map(p => renderPaperCard(p)).join('')}
      `;
      // Bind narrate buttons
      resultsDiv.querySelectorAll('.nr-narrate-btn').forEach(btn => {
        btn.addEventListener('click', () => void handleNarrate(btn as HTMLButtonElement));
      });
    } catch (e) {
      resultsDiv.innerHTML = `<div class="card status-error">論文読み込み失敗: ${esc((e as Error).message)}</div>`;
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
    app.innerHTML = `<div class="card status-error">品質レポート利用不可: ${esc((err as Error).message)}</div>`;
    return;
  }

  const app = document.getElementById('view-content')!;
  const s = report.summary;
  const pct = s.coverage_percent ?? 0;
  const displayPct = pct > 1 ? pct.toFixed(1) : (pct * 100).toFixed(1);
  const coverageClass = pct >= 0.7 ? 'status-ok' : pct >= 0.4 ? 'status-warn' : 'status-error';

  app.innerHTML = `
    <h1>コード品質 (Dendron)</h1>
    <div class="grid">
      <div class="card">
        <h3>カバレッジ</h3>
        <div class="metric ${coverageClass}">${displayPct}%</div>
        <p>${s.files_with_proof} / ${s.total_files} ファイル検証済み</p>
      </div>
      <div class="card">
        <h3>構造</h3>
        <div class="metric">${s.total_dirs}</div>
        <p>${s.dirs_with_proof} / ${s.total_dirs} ディレクトリ検証済み</p>
      </div>
    </div>
    ${s.issues.length > 0 ? `
      <div class="card" style="margin-top:1rem;">
        <h3>課題 (${s.issues.length})</h3>
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
    app.innerHTML = `<div class="card status-error">ポストチェック利用不可: ${esc((err as Error).message)}</div>`;
    return;
  }

  const app = document.getElementById('view-content')!;

  const wfRows = selList.items.map(item => {
    const modes = Object.keys(item.modes).join(', ') || '-';
    return `<tr>
      <td>${esc(item.wf_name)}</td>
      <td>${esc(modes)}</td>
      <td><button class="btn btn-sm run-postcheck-btn" data-wf="${esc(item.wf_name)}">実行</button></td>
    </tr>`;
  }).join('');

  app.innerHTML = `
    <h1>ポストチェック</h1>
    <div class="card">
      <h3>ワークフロー登録 (${selList.total} 件)</h3>
      <table class="data-table">
        <thead><tr><th>ワークフロー</th><th>モード</th><th>アクション</th></tr></thead>
        <tbody>${wfRows}</tbody>
      </table>
    </div>
    <div class="card">
      <h3>手動ポストチェック</h3>
      <div class="grid" style="grid-template-columns: 1fr 100px;">
        <div>
          <label>ワークフロー名:</label>
          <input type="text" id="pc-wf" class="input" placeholder="例: dia, noe, boot" style="margin-bottom:0.5rem;" />
          <label>チェック対象:</label>
          <textarea id="pc-content" class="input" rows="4" placeholder="出力テキストを貼り付け..."></textarea>
        </div>
        <div style="display:flex; flex-direction:column; gap:0.5rem;">
          <label>モード:</label>
          <select id="pc-mode" class="input">
            <option value="">デフォルト</option>
            <option value="+">+ (深層)</option>
            <option value="-">- (最小)</option>
            <option value="*">* (メタ)</option>
          </select>
          <button id="pc-run-btn" class="btn" style="margin-top:auto;">チェック実行</button>
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
      document.getElementById('pc-result')!.innerHTML = '<span class="status-warn">ワークフロー名とチェック対象を入力してください</span>';
      return;
    }
    const resultDiv = document.getElementById('pc-result')!;
    resultDiv.innerHTML = '<span class="loading">チェック中...</span>';
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
      resultDiv.innerHTML = `<span class="status-error">チェック失敗: ${esc((e as Error).message)}</span>`;
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
      const isDigestor = n.data?.digestor === true;
      const digestorUrl = isDigestor && n.data?.url ? String(n.data.url) : '';
      const digestorScore = isDigestor && n.data?.score ? Number(n.data.score) : 0;
      return `
          <div class="card notif-card level-${levelClass}${isDigestor ? ' notif-digestor' : ''}">
            <div class="notif-top">
              <span class="notif-source">${esc(n.source)}</span>
              <span class="notif-level ${levelClass}">${esc(levelLabel)}</span>
              ${isDigestor && digestorScore > 0
          ? `<span class="notif-score" title="関連度スコア">${(digestorScore * 100).toFixed(0)}%</span>`
          : ''}
              <span class="notif-time">${esc(relativeTime(n.timestamp))}</span>
            </div>
            <div class="notif-title">${esc(n.title)}</div>
            <div class="notif-body">${formatNotifBody(n.body)}</div>
            ${digestorUrl
          ? `<a href="${esc(digestorUrl)}" target="_blank" rel="noopener" class="btn btn-sm notif-link-btn">📎 論文を開く</a>`
          : ''}
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

  // OS ネイティブ通知を発火 (CRITICAL/HIGH のみ)
  void fireOsNotifications(notifications);

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
        <h2>📚 Sophia KI — 知識項目</h2>
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
          <div class="loading">読み込み中...</div>
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

  detailEl.innerHTML = '<div class="loading">読み込み中...</div>';

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
        <span>種別: ${esc(ki.source_type)}</span>
        ${ki.created ? `<span>作成日: ${new Date(ki.created).toLocaleString('ja-JP')}</span>` : ''}
        ${ki.updated ? `<span>更新日: ${new Date(ki.updated).toLocaleString('ja-JP')}</span>` : ''}
        <span>${Math.round(ki.size_bytes / 1024)}KB</span>
      </div>
      ${ki.backlinks.length > 0 ? `
        <div class="sophia-backlinks">
          <strong>🔗 逆リンク:</strong>
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

// ─── Symploke 統合検索 ───────────────────────────────────────

const SOURCE_COLORS: Record<string, string> = {
  handoff: '#58a6ff',
  sophia: '#a371f7',
  kairos: '#3fb950',
  gnosis: '#f0883e',
  chronos: '#f778ba',
};

const SOURCE_LABELS: Record<string, string> = {
  handoff: '📋 Handoff',
  sophia: '📚 Sophia',
  kairos: '⏳ Kairos',
  gnosis: '🔬 Gnosis',
  chronos: '💬 Chronos',
};

let searchActiveSources = new Set(['handoff', 'sophia', 'kairos', 'gnosis', 'chronos']);

async function renderSearch(): Promise<void> {
  const app = document.getElementById('view-content')!;

  const sourceChips = Object.entries(SOURCE_LABELS).map(([key, label]) => {
    const active = searchActiveSources.has(key);
    const color = SOURCE_COLORS[key] ?? '#8b949e';
    return `<button class="search-source-chip ${active ? 'active' : ''}"
      data-source="${esc(key)}"
      style="--chip-color: ${color}">
      ${label}
    </button>`;
  }).join('');

  app.innerHTML = `
    <h1>🔍 統合検索</h1>
    <div class="card">
      <div style="display:flex; gap:0.5rem; margin-bottom:0.75rem;">
        <input type="text" id="symploke-search-input" class="input"
          placeholder="すべての知識ソースを横断検索..."
          style="flex:1; font-size:1.05rem;" />
        <button id="symploke-search-btn" class="btn">検索</button>
      </div>
      <div id="search-source-filters" style="display:flex; gap:0.4rem; flex-wrap:wrap;">
        ${sourceChips}
      </div>
    </div>
    <div id="symploke-search-results"></div>
  `;

  const searchInput = document.getElementById('symploke-search-input') as HTMLInputElement;
  const searchBtn = document.getElementById('symploke-search-btn')!;

  // Source chip toggle
  document.querySelectorAll('.search-source-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const source = chip.getAttribute('data-source') ?? '';
      if (searchActiveSources.has(source)) {
        searchActiveSources.delete(source);
        chip.classList.remove('active');
      } else {
        searchActiveSources.add(source);
        chip.classList.add('active');
      }
    });
  });

  const doSearch = async (): Promise<void> => {
    const query = searchInput.value.trim();
    if (!query) return;
    const resultsDiv = document.getElementById('symploke-search-results')!;
    resultsDiv.innerHTML = '<div class="loading">検索中...</div>';

    const sources = Array.from(searchActiveSources).join(',');
    try {
      const res: SymplokeSearchResponse = await api.symplokeSearch(query, 20, sources);


      if (res.results.length === 0) {
        resultsDiv.innerHTML = `
          <div class="card" style="text-align:center; padding:2rem;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">📭</div>
            <p>「${esc(query)}」に一致する結果がありません</p>
            <small style="color:#8b949e;">検索対象: ${res.sources_searched.map(s => SOURCE_LABELS[s] ?? s).join(', ')}</small>
          </div>`;
        return;
      }

      const sourceSummary = res.sources_searched
        .map(s => `<span style="color:${SOURCE_COLORS[s] ?? '#8b949e'};">${SOURCE_LABELS[s] ?? s}</span>`)
        .join(' · ');

      resultsDiv.innerHTML = `
        <div class="search-summary" style="margin:0.75rem 0; color:#8b949e; font-size:0.85rem;">
          ${res.total} 件の結果 — ${sourceSummary}
        </div>
        ${res.results.map((r: SymplokeSearchResultItem) => {
        const color = SOURCE_COLORS[r.source] ?? '#8b949e';
        const scorePercent = Math.min(r.score * 100, 100);
        return `
            <div class="card search-result-card" style="border-left: 3px solid ${color};">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                <span class="search-source-badge" style="background:${color}20; color:${color}; border:1px solid ${color}40;">
                  ${esc(SOURCE_LABELS[r.source] ?? r.source)}
                </span>
                <span class="search-score">
                  <span class="search-score-bar" style="width:${scorePercent}%; background:${color};"></span>
                  ${r.score.toFixed(3)}
                </span>
              </div>
              <h3 class="search-result-title">${esc(r.title) || esc(r.id)}</h3>
              ${r.snippet ? `<p class="search-result-snippet">${esc(r.snippet)}</p>` : ''}
            </div>`;
      }).join('')}
      `;
    } catch (e) {
      resultsDiv.innerHTML = `<div class="card status-error">検索失敗: ${esc((e as Error).message)}</div>`;
    }
  };

  searchBtn.addEventListener('click', () => void doSearch());
  searchInput.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.key === 'Enter') void doSearch();
  });
  searchInput.focus();
}


// ─── Timeline View ───────────────────────────────────────────

let tlCurrentType: string | undefined;
let tlCurrentOffset = 0;
const TL_PAGE_SIZE = 30;

async function renderTimelineView(): Promise<void> {
  const app = document.getElementById('view-content');
  if (!app) return;
  tlCurrentType = undefined;
  tlCurrentOffset = 0;

  let statsHtml = '';
  try {
    const stats = await api.timelineStats();
    statsHtml = `
      <div class="tl-stats">
        <span class="tl-stat">📋 Handoff: <strong>${stats.by_type.handoff}</strong></span>
        <span class="tl-stat">💡 Doxa: <strong>${stats.by_type.doxa}</strong></span>
        <span class="tl-stat">⚙️ WF: <strong>${stats.by_type.workflow}</strong></span>
        <span class="tl-stat">◆ Kalon: <strong>${stats.by_type.kalon || 0}</strong></span>
        <span class="tl-stat tl-stat-total">合計: <strong>${stats.total}</strong></span>
      </div>`;
  } catch { /* ignore */ }

  app.innerHTML = `
    <div class="tl-view">
      <div class="tl-header">
        <h2>📅 セッション・タイムライン</h2>
        ${statsHtml}
        <div class="tl-filters">
          <button class="tl-filter active" data-type="">全て</button>
          <button class="tl-filter" data-type="handoff">📋 Handoff</button>
          <button class="tl-filter" data-type="doxa">💡 Doxa</button>
          <button class="tl-filter" data-type="workflow">⚙️ Workflow</button>
          <button class="tl-filter" data-type="kalon">◆ Kalon</button>
        </div>
      </div>
      <div class="tl-body">
        <div class="tl-list" id="tl-list"><div class="loading">読み込み中...</div></div>
        <div class="tl-detail" id="tl-detail"><div class="tl-empty">← イベントを選択してください</div></div>
      </div>
    </div>`;

  app.querySelectorAll('.tl-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      app.querySelectorAll('.tl-filter').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const t = (btn as HTMLElement).dataset.type;
      tlCurrentType = t || undefined;
      tlCurrentOffset = 0;
      void loadTimelineEvents();
    });
  });
  await loadTimelineEvents();
}

async function loadTimelineEvents(): Promise<void> {
  const listEl = document.getElementById('tl-list');
  if (!listEl) return;
  try {
    const data = await api.timelineEvents(TL_PAGE_SIZE, tlCurrentOffset, tlCurrentType);
    if (data.events.length === 0) {
      listEl.innerHTML = '<div class="tl-empty">イベントがありません</div>';
      return;
    }
    const typeIcon = (t: string) => t === 'handoff' ? '📋' : t === 'doxa' ? '💡' : t === 'kalon' ? '◆' : '⚙️';
    const typeClass = (t: string) => `tl-type-${t}`;
    const eventsHtml = data.events.map((e: TimelineEvent) => `
      <div class="tl-event-card" data-event-id="${esc(e.id)}">
        <div class="tl-event-top">
          <span class="tl-event-icon ${typeClass(e.type)}">${typeIcon(e.type)}</span>
          <span class="tl-event-date">${esc(e.date || e.mtime?.substring(0, 10))}</span>
        </div>
        <div class="tl-event-title">${esc(e.title)}</div>
        <div class="tl-event-summary">${esc(e.summary?.substring(0, 120))}${(e.summary?.length || 0) > 120 ? '...' : ''}</div>
        <div class="tl-event-meta">
          <span class="tl-event-type">${esc(e.type)}</span>
          <span class="tl-event-size">${Math.round((e.size_bytes || 0) / 1024)}KB</span>
        </div>
      </div>`).join('');
    const paginationHtml = `
      <div class="tl-pagination">
        ${tlCurrentOffset > 0 ? '<button class="btn btn-sm" id="tl-prev">← 前へ</button>' : ''}
        <span class="tl-page-info">${tlCurrentOffset + 1}–${Math.min(tlCurrentOffset + TL_PAGE_SIZE, data.total)} / ${data.total}</span>
        ${data.has_more ? '<button class="btn btn-sm" id="tl-next">次へ →</button>' : ''}
      </div>`;
    listEl.innerHTML = eventsHtml + paginationHtml;
    listEl.querySelectorAll('.tl-event-card').forEach(el => {
      el.addEventListener('click', () => {
        listEl.querySelectorAll('.tl-event-card').forEach(c => c.classList.remove('active'));
        el.classList.add('active');
        const eventId = (el as HTMLElement).dataset.eventId;
        if (eventId) void loadTimelineDetail(eventId);
      });
    });
    document.getElementById('tl-prev')?.addEventListener('click', () => {
      tlCurrentOffset = Math.max(0, tlCurrentOffset - TL_PAGE_SIZE);
      void loadTimelineEvents();
    });
    document.getElementById('tl-next')?.addEventListener('click', () => {
      tlCurrentOffset += TL_PAGE_SIZE;
      void loadTimelineEvents();
    });
  } catch (e) {
    listEl.innerHTML = `<div class="card status-error">Timeline 読み込み失敗: ${esc((e as Error).message)}</div>`;
  }
}

async function loadTimelineDetail(eventId: string): Promise<void> {
  const detailEl = document.getElementById('tl-detail');
  if (!detailEl) return;
  detailEl.innerHTML = '<div class="loading">読み込み中...</div>';
  try {
    const event: TimelineEventDetail = await api.timelineEvent(eventId);
    const typeIcon = event.type === 'handoff' ? '📋' : event.type === 'doxa' ? '💡' : event.type === 'kalon' ? '◆' : '⚙️';
    const htmlContent = marked.parse(event.content || '') as string;
    detailEl.innerHTML = `
      <div class="tl-detail-header">
        <span class="tl-detail-icon">${typeIcon}</span>
        <div class="tl-detail-info">
          <h3>${esc(event.title)}</h3>
          <div class="tl-detail-meta">
            <span>${esc(event.type)}</span>
            <span>${esc(event.date || event.mtime?.substring(0, 10))}</span>
            <span>${esc(event.filename)}</span>
            <span>${Math.round((event.size_bytes || 0) / 1024)}KB</span>
          </div>
        </div>
      </div>
      <div class="tl-detail-content">${htmlContent}</div>`;
  } catch (e) {
    detailEl.innerHTML = `<div class="card status-error">詳細読み込み失敗: ${esc((e as Error).message)}</div>`;
  }
}

// ─── Synteleia (6-Agent Cognitive Audit) ─────────────────────

async function renderSynteleiaView(): Promise<void> {
  const app = document.getElementById('view-content');
  if (!app) return;

  // Fetch agents list
  let agentsHtml = '';
  try {
    const agents = await api.synteleiaAgents();
    agentsHtml = agents.map(a =>
      `<div class="syn-agent">
        <span class="syn-agent-header">
          ${a.layer === 'poiesis' ? '🔨' : '🔍'} <strong>${esc(a.name)}</strong>
          <span class="syn-confidence">[${esc(a.layer)}]</span>
        </span>
        <div style="font-size:0.8rem;color:var(--text-muted);padding-left:1.5rem">${esc(a.description)}</div>
      </div>`
    ).join('');
  } catch { /* ignore */ }

  app.innerHTML = `
    <div class="view-container">
      <h2>🛡️ Synteleia — 認知アンサンブル監査</h2>
      <p style="color:var(--text-secondary);margin-bottom:1rem">6視点の監査エージェントがテキストを多角的に検証します</p>

      <div class="card" style="margin-bottom:1rem">
        <h3 style="margin-top:0">エージェント一覧</h3>
        ${agentsHtml || '<div class="text-muted">エージェント情報を取得できませんでした</div>'}
      </div>

      <div class="card" style="margin-bottom:1rem">
        <h3 style="margin-top:0">監査実行</h3>
        <textarea id="syn-input" rows="6" placeholder="監査対象テキストを入力..." style="width:100%;background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border-color);border-radius:6px;padding:0.5rem;font-family:inherit;resize:vertical"></textarea>
        <div style="display:flex;gap:0.5rem;margin-top:0.5rem;align-items:center">
          <select id="syn-type" style="background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border-color);border-radius:4px;padding:0.3rem 0.5rem">
            <option value="generic">Generic</option>
            <option value="ccl_output">CCL Output</option>
            <option value="code">Code</option>
            <option value="thought">Thought</option>
            <option value="plan">Plan</option>
            <option value="proof">Proof</option>
          </select>
          <label style="font-size:0.8rem;color:var(--text-secondary);display:flex;align-items:center;gap:0.3rem">
            <input type="checkbox" id="syn-l2"> L2 (LLM)
          </label>
          <button id="syn-run" class="btn-primary" style="margin-left:auto">🛡️ 監査実行</button>
          <button id="syn-quick" class="btn-secondary">⚡ Quick</button>
        </div>
      </div>

      <div id="syn-result" class="card" style="display:none"></div>
    </div>`;

  // Audit button handlers
  const runBtn = document.getElementById('syn-run');
  const quickBtn = document.getElementById('syn-quick');

  async function doAudit(quick: boolean) {
    const input = (document.getElementById('syn-input') as HTMLTextAreaElement)?.value?.trim();
    if (!input) return;

    const targetType = (document.getElementById('syn-type') as HTMLSelectElement)?.value || 'generic';
    const withL2 = (document.getElementById('syn-l2') as HTMLInputElement)?.checked || false;
    const resultEl = document.getElementById('syn-result');
    if (!resultEl) return;

    resultEl.style.display = 'block';
    resultEl.innerHTML = '<div class="loading">監査実行中...</div>';

    try {
      const res = quick
        ? await api.synteleiaQuick(input, targetType)
        : await api.synteleiaAudit(input, targetType, withL2);

      const passClass = res.passed ? 'syn-pass' : 'syn-fail';
      const passLabel = res.passed ? '✅ PASS' : '❌ FAIL';

      const wbcHtml = res.wbc_alerted
        ? '<div class="syn-wbc-alert">🚨 WBC アラートが送信されました</div>'
        : '';

      const agentCards = res.agent_results.map(ar => {
        const icon = ar.passed ? '✅' : '❌';
        const issuesHtml = ar.issues.map(i =>
          `<div class="syn-issue syn-sev-${i.severity}">
            <strong>[${esc(i.code)}]</strong> ${esc(i.message)}
            ${i.suggestion ? `<br><em>→ ${esc(i.suggestion)}</em>` : ''}
          </div>`
        ).join('');
        return `
          <div class="syn-agent">
            <div class="syn-agent-header">
              ${icon} <strong>${esc(ar.agent_name)}</strong>
              <span class="syn-confidence">${(ar.confidence * 100).toFixed(0)}%</span>
            </div>
            ${issuesHtml}
          </div>`;
      }).join('');

      resultEl.innerHTML = `
        <div class="syn-result">
          <div class="syn-header">
            <span class="syn-badge ${passClass}">${passLabel}</span>
            <span class="syn-summary">${esc(res.summary)}</span>
          </div>
          ${wbcHtml}
          <div class="syn-stats">
            Issues: ${res.total_issues} (Critical: ${res.critical_count}, High: ${res.high_count})
          </div>
          ${agentCards}
        </div>`;
    } catch (e) {
      resultEl.innerHTML = `<div class="status-error">監査失敗: ${esc((e as Error).message)}</div>`;
    }
  }

  runBtn?.addEventListener('click', () => void doAudit(false));
  quickBtn?.addEventListener('click', () => void doAudit(true));
}

// ─── Digestor ────────────────────────────────────────────────

function renderCandidateCard(c: DigestCandidate, idx: number): string {
  const scorePercent = Math.min(c.score * 100, 100);
  const scoreClass = c.score >= 0.7 ? 'dg-score-high' : c.score >= 0.5 ? 'dg-score-mid' : 'dg-score-low';
  const topicsTags = c.matched_topics
    .map(t => `<span class="dg-topic-tag">${esc(t)}</span>`).join('');
  const templates = c.suggested_templates?.length > 0
    ? c.suggested_templates.slice(0, 2)
      .map(t => `<span class="dg-template-tag">${esc(t.id || String(t))}</span>`).join('')
    : '';

  return `
    <div class="card dg-candidate">
      <div class="dg-candidate-rank">#${idx + 1}</div>
      <div class="dg-candidate-body">
        <div class="dg-candidate-header">
          <h3 class="dg-candidate-title">
            ${c.url ? `<a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.title)}</a>` : esc(c.title)}
          </h3>
          <div class="dg-score-bar-wrap">
            <div class="dg-score-bar ${scoreClass}" style="width:${scorePercent}%"></div>
            <span class="dg-score-label">${c.score.toFixed(2)}</span>
          </div>
        </div>
        <div class="dg-candidate-meta">
          ${topicsTags}
          ${templates}
          ${c.source ? `<span class="dg-source">${esc(c.source)}</span>` : ''}
        </div>
        ${c.rationale ? `<div class="dg-rationale">${esc(c.rationale)}</div>` : ''}
      </div>
    </div>`;
}

async function renderDigestorView(): Promise<void> {
  const app = document.getElementById('view-content')!;
  app.innerHTML = '<div class="loading">Digestor 読み込み中...</div>';

  try {
    const data = await api.digestorReports(10);
    if (!data || data.reports.length === 0) {
      app.innerHTML = `
        <h1>🧬 Digestor</h1>
        <div class="card">
          <p>レポートが見つかりません。</p>
          <p style="color:#8b949e;">次回のスケジュール実行後に表示されます。</p>
        </div>`;
      return;
    }

    const totalReports = data.total;
    const latest = data.reports[0]!;
    const latestDate = latest.timestamp ? new Date(latest.timestamp).toLocaleString('ja-JP') : '-';

    // Tab state
    let activeTab: 'reports' | 'news' = 'news';

    function render() {
      // Report selector options
      const reportOptions = data.reports.map((r, i) => {
        const dt = r.timestamp ? new Date(r.timestamp).toLocaleDateString('ja-JP') : r.filename;
        const label = `${dt} — ${r.candidates_selected}件 ${r.dry_run ? '(DRY)' : ''}`;
        return `<option value="${i}">${esc(label)}</option>`;
      }).join('');

      app.innerHTML = `
        <h1>🧬 Digestor</h1>

        <div class="dg-tabs">
          <button class="dg-tab${activeTab === 'news' ? ' dg-tab-active' : ''}" data-tab="news">📰 AI ニュース</button>
          <button class="dg-tab${activeTab === 'reports' ? ' dg-tab-active' : ''}" data-tab="reports">📊 レポート</button>
        </div>

        <div class="grid" style="margin-bottom:1rem;">
          <div class="card">
            <h3>レポート数</h3>
            <div class="metric">${totalReports}</div>
          </div>
          <div class="card">
            <h3>最新レポート</h3>
            <div class="metric" style="font-size:1.2rem;">${esc(latestDate)}</div>
            <p>${latest.total_papers} 論文 → ${latest.candidates_selected} 候補</p>
          </div>
          <div class="card">
            <h3>ステータス</h3>
            <div class="metric ${latest.dry_run ? 'status-warn' : 'status-ok'}">
              ${latest.dry_run ? 'DRY RUN' : 'LIVE'}
            </div>
          </div>
        </div>

        ${activeTab === 'news' ? renderNewsTab(data) : renderReportsTab(data, reportOptions)}
      `;

      // Tab click handlers
      app.querySelectorAll('.dg-tab').forEach(btn => {
        btn.addEventListener('click', () => {
          activeTab = (btn as HTMLElement).dataset.tab as 'reports' | 'news';
          render();
        });
      });

      // Report selector handler (reports tab)
      if (activeTab === 'reports') {
        document.getElementById('dg-report-select')?.addEventListener('change', (e) => {
          const idx = parseInt((e.target as HTMLSelectElement).value, 10);
          showReportCandidates(data, idx);
        });
        showReportCandidates(data, 0);
      }
    }

    render();

  } catch (e) {
    app.innerHTML = `<div class="card status-error">Digestor エラー: ${esc((e as Error).message)}</div>`;
  }
}

function renderNewsTab(data: { reports: Array<{ timestamp: string; candidates: DigestCandidate[] }> }): string {
  // Collect candidates from latest report(s)
  const latest = data.reports[0];
  if (!latest || latest.candidates.length === 0) {
    return '<div class="dg-empty-state"><div class="dg-empty-icon">📰</div><p>ニュースはまだありません。<br>Digestor が論文を収集すると、ここに表示されます。</p></div>';
  }

  const reportDate = latest.timestamp ? new Date(latest.timestamp).toLocaleDateString('ja-JP') : '';

  const newsCards = latest.candidates.map((c, i) => {
    const scorePercent = Math.min(c.score * 100, 100);
    const topicTags = c.matched_topics
      .slice(0, 4)
      .map(t => `<span class="dg-news-tag">${esc(t)}</span>`).join('');

    return `
      <div class="card dg-news-card">
        <div class="dg-news-header">
          <span class="dg-news-rank">#${i + 1}</span>
          <span class="dg-news-score">${scorePercent.toFixed(0)}%</span>
        </div>
        <h3 class="dg-news-title">
          ${c.url ? `<a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.title)}</a>` : esc(c.title)}
        </h3>
        ${c.rationale ? `<p class="dg-news-rationale">${esc(c.rationale)}</p>` : ''}
        <div class="dg-news-topics">${topicTags}</div>
        ${c.url ? `<a href="${esc(c.url)}" target="_blank" rel="noopener" class="dg-news-link">📎 論文を開く</a>` : ''}
      </div>`;
  }).join('');

  return `
    <div class="dg-news-date">📅 ${esc(reportDate)} の AI ニュース</div>
    ${newsCards}
  `;
}

function renderReportsTab(_data: { reports: Array<{ timestamp: string; candidates_selected: number; dry_run: boolean; filename: string; candidates: DigestCandidate[] }> }, reportOptions: string): string {
  return `
    <div class="card" style="margin-bottom:1rem;">
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <label>レポート選択:</label>
        <select id="dg-report-select" class="input" style="flex:1;">${reportOptions}</select>
      </div>
    </div>
    <div id="dg-candidates"></div>
  `;
}

function showReportCandidates(data: { reports: Array<{ filename: string; total_papers: number; candidates: DigestCandidate[] }> }, idx: number): void {
  const report = data.reports[idx];
  const candidatesDiv = document.getElementById('dg-candidates');
  if (!candidatesDiv) return;
  if (!report || report.candidates.length === 0) {
    candidatesDiv.innerHTML = '<div class="card"><p>候補なし</p></div>';
    return;
  }
  candidatesDiv.innerHTML = `
    <div class="dg-report-header">
      <span>${esc(report.filename)}</span>
      <span>${report.candidates.length} 候補 / ${report.total_papers} 論文</span>
    </div>
    ${report.candidates.map((c: DigestCandidate, i: number) => renderCandidateCard(c, i)).join('')}
  `;
}

