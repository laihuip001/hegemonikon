import { api } from '../api/client';
import type { SynedrionSweepResult, SynedrionCacheStats } from '../api/client';
import { esc } from '../utils';

// ─── Synedrion View — SweepEngine 多視点スキャン ───────────────

export async function renderSynedrionView(): Promise<void> {
    const app = document.getElementById('view-content');
    if (!app) return;

    // Fetch cache stats in background
    let cacheHtml = '';
    try {
        const stats = await api.synedrionCacheStats();
        cacheHtml = renderCacheCard(stats);
    } catch {
        cacheHtml = '<div class="text-muted">キャッシュ情報取得不可</div>';
    }

    app.innerHTML = `
    <div class="view-container">
      <h2>🔭 Synedrion — 多視点スキャン</h2>
      <p style="color:var(--text-secondary);margin-bottom:1rem">SweepEngine が複数の perspective からソースコードを分析します</p>

      <div class="card" style="margin-bottom:1rem">
        <h3 style="margin-top:0">スキャン設定</h3>
        <div style="display:flex;flex-direction:column;gap:0.75rem">
          <div>
            <label style="font-size:0.8rem;color:var(--text-secondary);display:block;margin-bottom:0.25rem">ファイルパス</label>
            <input id="syd-filepath" type="text" placeholder="/home/.../example.py"
              style="width:100%;background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border-color);border-radius:6px;padding:0.5rem;font-family:var(--font-mono, monospace)" />
          </div>
          <div style="display:flex;gap:1rem;flex-wrap:wrap">
            <div style="flex:1;min-width:200px">
              <label style="font-size:0.8rem;color:var(--text-secondary);display:block;margin-bottom:0.25rem">ドメインフィルタ (カンマ区切り)</label>
              <input id="syd-domains" type="text" placeholder="Security, Performance, ..."
                style="width:100%;background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border-color);border-radius:4px;padding:0.4rem" />
            </div>
            <div style="flex:1;min-width:200px">
              <label style="font-size:0.8rem;color:var(--text-secondary);display:block;margin-bottom:0.25rem">座標フィルタ (カンマ区切り)</label>
              <input id="syd-axes" type="text" placeholder="O1, S2, H3, ..."
                style="width:100%;background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border-color);border-radius:4px;padding:0.4rem" />
            </div>
          </div>
          <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap">
            <div>
              <label style="font-size:0.8rem;color:var(--text-secondary);display:block;margin-bottom:0.25rem">Perspectives数</label>
              <input id="syd-max" type="number" value="10" min="1" max="50"
                style="width:80px;background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border-color);border-radius:4px;padding:0.4rem;text-align:center" />
            </div>
            <div>
              <label style="font-size:0.8rem;color:var(--text-secondary);display:block;margin-bottom:0.25rem">モデル</label>
              <select id="syd-model" style="background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border-color);border-radius:4px;padding:0.4rem">
                <option value="gemini-2.0-flash">gemini-2.0-flash</option>
                <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                <option value="gemini-2.5-pro">gemini-2.5-pro</option>
              </select>
            </div>
            <button id="syd-run" class="btn-primary" style="margin-left:auto;margin-top:auto">🔭 スキャン実行</button>
          </div>
        </div>
      </div>

      <div id="syd-result" class="card" style="display:none"></div>

      <div class="card" style="margin-top:1rem">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
          <h3 style="margin:0">📦 ResponseCache</h3>
          <button id="syd-clear-cache" class="btn-secondary" style="font-size:0.8rem">🗑 クリア</button>
        </div>
        <div id="syd-cache">${cacheHtml}</div>
      </div>
    </div>`;

    // --- Event handlers ---
    document.getElementById('syd-run')?.addEventListener('click', () => void doSweep());
    document.getElementById('syd-clear-cache')?.addEventListener('click', async () => {
        try {
            const res = await api.synedrionCacheClear();
            const cacheEl = document.getElementById('syd-cache');
            if (cacheEl) cacheEl.innerHTML = `<div class="text-muted">✅ ${esc(res.message)}</div>`;
            // Refresh stats after a moment
            setTimeout(async () => {
                try {
                    const stats = await api.synedrionCacheStats();
                    if (cacheEl) cacheEl.innerHTML = renderCacheCard(stats);
                } catch { /* silent */ }
            }, 500);
        } catch (e) {
            const cacheEl = document.getElementById('syd-cache');
            if (cacheEl) cacheEl.innerHTML = `<div class="status-error">クリア失敗: ${esc((e as Error).message)}</div>`;
        }
    });
}

async function doSweep(): Promise<void> {
    const filepath = (document.getElementById('syd-filepath') as HTMLInputElement)?.value?.trim();
    if (!filepath) return;

    const domainsRaw = (document.getElementById('syd-domains') as HTMLInputElement)?.value?.trim();
    const axesRaw = (document.getElementById('syd-axes') as HTMLInputElement)?.value?.trim();
    const maxP = parseInt((document.getElementById('syd-max') as HTMLInputElement)?.value || '10', 10);
    const model = (document.getElementById('syd-model') as HTMLSelectElement)?.value || 'gemini-2.0-flash';

    const domains = domainsRaw ? domainsRaw.split(',').map(s => s.trim()).filter(Boolean) : undefined;
    const axes = axesRaw ? axesRaw.split(',').map(s => s.trim()).filter(Boolean) : undefined;

    const resultEl = document.getElementById('syd-result');
    if (!resultEl) return;

    resultEl.style.display = 'block';
    resultEl.innerHTML = '<div class="loading">🔭 スキャン実行中... (数分かかる場合があります)</div>';

    try {
        const res = await api.synedrionSweep(filepath, domains, axes, maxP, model);
        resultEl.innerHTML = renderSweepResult(res);
    } catch (e) {
        resultEl.innerHTML = `<div class="status-error">スキャン失敗: ${esc((e as Error).message)}</div>`;
    }
}

function renderSweepResult(res: SynedrionSweepResult): string {
    const hasIssues = res.issue_count > 0;
    const statusClass = hasIssues ? 'syn-fail' : 'syn-pass';
    const statusLabel = hasIssues ? `⚠️ ${res.issue_count} issues` : '✅ Clean';

    // Severity summary
    const sevEntries = Object.entries(res.severity)
        .filter(([, count]) => count > 0)
        .map(([sev, count]) => `<span class="syn-sev-${sev.toLowerCase()}" style="padding:0.1rem 0.5rem;border-radius:3px;font-size:0.8rem">${esc(sev)}: ${count}</span>`)
        .join(' ');

    // Issue cards
    const issueCards = res.issues.map(i => `
      <div class="syn-issue syn-sev-${i.severity.toLowerCase()}" style="margin-bottom:0.5rem;padding:0.5rem;border-radius:6px;border-left:3px solid">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <strong>[${esc(i.domain)} / ${esc(i.axis)}]</strong>
          <span class="syn-confidence" style="font-size:0.75rem">${esc(i.perspective_id)}</span>
        </div>
        <div style="margin-top:0.3rem">${esc(i.description)}</div>
        ${i.recommendation ? `<div style="margin-top:0.3rem;font-size:0.85rem;color:var(--text-secondary)"><em>→ ${esc(i.recommendation)}</em></div>` : ''}
      </div>
    `).join('');

    return `
    <div class="syn-result">
      <div class="syn-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem">
        <span class="syn-badge ${statusClass}">${statusLabel}</span>
        <span style="color:var(--text-secondary);font-size:0.85rem">
          ${res.total_perspectives} perspectives · ${res.coverage.toFixed(0)}% coverage · ${res.elapsed_seconds.toFixed(1)}s
        </span>
      </div>
      <div style="margin:0.5rem 0;font-family:var(--font-mono, monospace);font-size:0.85rem;color:var(--text-secondary)">
        📄 ${esc(res.filepath)}
      </div>
      ${sevEntries ? `<div class="syn-stats" style="margin-bottom:0.75rem">${sevEntries}</div>` : ''}
      ${res.silences > 0 ? `<div style="font-size:0.8rem;color:var(--text-muted)">🔇 Silences: ${res.silences} · Errors: ${res.errors}</div>` : ''}
      ${issueCards || '<div class="text-muted" style="text-align:center;padding:1rem">問題は検出されませんでした 🎉</div>'}
    </div>`;
}

function renderCacheCard(stats: SynedrionCacheStats): string {
    const hitRate = (stats.hit_rate * 100).toFixed(1);
    const ttlDays = (stats.ttl_seconds / 86400).toFixed(1);

    return `
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:0.75rem;font-size:0.85rem">
      <div style="text-align:center">
        <div style="font-size:1.5rem;font-weight:700;color:var(--accent-primary)">${stats.total_entries}</div>
        <div style="color:var(--text-secondary)">エントリ</div>
      </div>
      <div style="text-align:center">
        <div style="font-size:1.5rem;font-weight:700;color:var(--accent-primary)">${stats.size_mb.toFixed(1)}<span style="font-size:0.8rem">MB</span></div>
        <div style="color:var(--text-secondary)">/ ${stats.max_size_mb}MB</div>
      </div>
      <div style="text-align:center">
        <div style="font-size:1.5rem;font-weight:700;color:var(--accent-primary)">${hitRate}<span style="font-size:0.8rem">%</span></div>
        <div style="color:var(--text-secondary)">ヒット率</div>
      </div>
      <div style="text-align:center">
        <div style="font-size:1.5rem;font-weight:700;color:var(--text-primary)">${stats.hits} / ${stats.misses}</div>
        <div style="color:var(--text-secondary)">Hit / Miss</div>
      </div>
      <div style="text-align:center">
        <div style="font-size:1.5rem;font-weight:700;color:var(--text-primary)">${ttlDays}<span style="font-size:0.8rem">日</span></div>
        <div style="color:var(--text-secondary)">TTL</div>
      </div>
    </div>`;
}
