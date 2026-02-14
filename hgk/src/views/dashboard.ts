import { api } from '../api/client';
import type {
    HealthReportResponse, Notification, DigestCandidate, DigestReport,
    QuotaResponse, QuotaModel,
} from '../api/client';
import { getCurrentRoute, esc, applyCountUpAnimations, applyStaggeredFadeIn, startPolling } from '../utils';
import { renderUsageCard } from '../telemetry';

// ─── Dashboard ───────────────────────────────────────────────

export async function renderDashboard(): Promise<void> {
    await renderDashboardContent();
    startPolling(renderDashboardContent, 60_000);
}

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

async function renderDashboardContent(): Promise<void> {
    const [health, healthCheck, fep, gnosisStats, criticals, kalonHist, quota, digestLatest] = await Promise.all([
        api.status().catch((): null => null),
        api.health().catch((): null => null),
        api.fepState().catch((): null => null),
        api.gnosisStats().catch((): null => null),
        api.notifications(5, 'CRITICAL').catch((): Notification[] => []),
        api.kalonHistory(5).catch((): null => null),
        api.quota().catch((): null => null),
        api.digestorLatest().catch((): null => null),
    ]);

    const app = document.getElementById('view-content')!;
    if (getCurrentRoute() !== 'dashboard') return;

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

    const alertHtml = criticals.length > 0 ? `
    <div class="alert-banner fade-in">
      <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
        <span class="status-dot error"></span>
        <strong style="color:var(--error-color);">緊急通知 ${criticals.length}件</strong>
      </div>
      ${criticals.slice(0, 3).map((n: Notification) => `
        <div style="padding:0.2rem 0; font-size:0.875rem;">
          ${esc(n.title)}
          <span style="color:var(--text-secondary); font-size:0.75rem;"> — ${esc(relativeTime(n.timestamp))}</span>
        </div>
      `).join('')}
      ${criticals.length > 3 ? `<div style="color:var(--text-secondary); font-size:0.8rem;">他 ${criticals.length - 3}件...</div>` : ''}
    </div>
  ` : '';

    app.innerHTML = `
    <h1>ダッシュボード <small class="poll-badge">自動更新 60秒</small></h1>
    ${alertHtml}
    <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
      <div class="card">
        <div class="metric-label">システム状態</div>
        <div class="metric">
          <span class="status-dot ${score >= 0.8 ? 'ok' : score >= 0.5 ? 'warn' : 'error'}"></span>
          ${healthStatus}
        </div>
        <p style="color:var(--text-secondary); font-size:0.8rem; margin:0.25rem 0 0;">稼働時間: ${esc(uptimeDisplay)}</p>
      </div>
      <div class="card">
        <div class="metric-label">FEP エージェント</div>
        <div class="metric"><span data-count-target="${typeof historyLen === 'number' ? historyLen : 0}">${String(historyLen)}</span></div>
        <p style="color:var(--text-secondary); font-size:0.8rem; margin:0.25rem 0 0;">推論ステップ数</p>
      </div>
      <div class="card">
        <div class="metric-label">Gnōsis</div>
        <div class="metric"><span data-count-target="${typeof gnosisCount === 'number' ? gnosisCount : 0}">${String(gnosisCount)}</span></div>
        <p style="color:var(--text-secondary); font-size:0.8rem; margin:0.25rem 0 0;">収集済み論文</p>
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
    ${renderQuotaCard(quota)}
    ${renderDigestCard(digestLatest)}
    ${renderHealthItems(health)}
    ${renderUsageCard()}
    <footer class="dashboard-footer">
      <span>Hegemonikón Desktop v0.3.0</span>
      <span>·</span>
      <span>FEP-based Cognitive Hypervisor</span>
      <span>·</span>
      <span>${new Date().toLocaleDateString('ja-JP')}</span>
    </footer>
  `;

    applyCountUpAnimations(app);
    applyStaggeredFadeIn(app);
}

function renderQuotaCard(quota: QuotaResponse | null): string {
    if (!quota) return '';
    if (quota.error) {
        const isLsError = quota.error.includes('Language Server') || quota.error.includes('agq-check');
        if (isLsError) {
            return `
        <div class="card quota-card" style="margin-top:1rem;">
          <div class="quota-header">
            <span class="metric-label">⚡ Quota</span>
            <span class="quota-plan" style="color: var(--text-secondary);">スタンドアロン</span>
          </div>
          <div style="color: var(--text-secondary); font-size: 0.85rem; padding: 0.5rem 0;">
            📡 Language Server 未接続 — Quota 追跡は LS 起動後に有効になります
          </div>
        </div>
      `;
        }
        return `
      <div class="card quota-card" style="margin-top:1rem;">
        <div class="metric-label">⚡ Quota</div>
        <div class="status-error" style="font-size:0.85rem;">Quota 情報取得不可: ${esc(quota.error)}</div>
      </div>
    `;
    }

    const statusIcon: Record<string, string> = {
        green: '🟢', yellow: '🟡', orange: '🟠', red: '🔴', unknown: '⚪',
    };
    const statusColor: Record<string, string> = {
        green: 'var(--success-color, #22c55e)',
        yellow: 'var(--warning-color, #eab308)',
        orange: 'var(--quota-orange, #f97316)',
        red: 'var(--error-color, #ef4444)',
        unknown: 'var(--text-secondary)',
    };

    const modelsHtml = quota.models.map((m: QuotaModel) => `
    <div class="quota-model">
      <div class="quota-model-header">
        <span class="quota-model-icon">${statusIcon[m.status] ?? '⚪'}</span>
        <span class="quota-model-label">${esc(m.label)}</span>
        <span class="quota-model-pct" style="color:${statusColor[m.status] ?? ''}">${m.remaining_pct}%</span>
      </div>
      <div class="quota-bar">
        <div class="quota-bar-fill" style="width:${m.remaining_pct}%; background:${statusColor[m.status] ?? ''}"></div>
      </div>
      ${m.reset_time ? `<div class="quota-model-reset">↻ ${esc(m.reset_time)} UTC</div>` : ''}
    </div>
  `).join('');

    const alertHtml = (quota.overall_status === 'orange' || quota.overall_status === 'red')
        ? `<div class="alert-banner quota-alert fade-in" style="margin-bottom:0.75rem;">
         <span class="status-dot ${quota.overall_status === 'red' ? 'error' : 'warn'}"></span>
         <strong style="color:${quota.overall_status === 'red' ? 'var(--error-color)' : 'var(--quota-orange, #f97316)'}">
           ${quota.overall_status === 'red' ? '🔴 Quota 残量危険 — Turtle Mode 推奨' : '🟠 Quota 残量低下'}
         </strong>
       </div>`
        : '';

    const pc = quota.prompt_credits;
    const fc = quota.flow_credits;

    return `
    <div class="card quota-card" style="margin-top:1rem;">
      ${alertHtml}
      <div class="quota-header">
        <span class="metric-label">⚡ Quota</span>
        <span class="quota-plan">${esc(quota.plan)}</span>
      </div>
      ${modelsHtml}
      <div class="quota-credits">
        <span>💳 Prompt: <strong>${pc.available}</strong>/${pc.monthly}</span>
        <span>🌊 Flow: <strong>${fc.available}</strong>/${fc.monthly}</span>
      </div>
    </div>
  `;
}

function renderDigestCard(digest: DigestReport | null): string {
    if (!digest) return '';

    const timeStr = digest.timestamp
        ? (() => {
            try {
                const d = new Date(digest.timestamp);
                return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
            } catch { return digest.timestamp; }
        })()
        : '';

    if (digest.candidates.length === 0) {
        return `
      <div class="card digest-card" style="margin-top:1rem;">
        <div class="digest-header">
          <span class="metric-label">🔬 最新消化</span>
          <span class="digest-timestamp">${esc(timeStr)}</span>
        </div>
        <div style="color:var(--text-secondary); font-size:0.85rem; padding:0.5rem 0;">
          消化候補なし — <code>digest_to_ki.py</code> を実行してください
        </div>
      </div>
    `;
    }

    const candidatesHtml = digest.candidates.slice(0, 5).map((c: DigestCandidate) => {
        const scoreWidth = Math.round(c.score * 100);
        const scoreColor = c.score >= 0.7 ? 'var(--success-color, #22c55e)'
            : c.score >= 0.4 ? 'var(--warning-color, #eab308)'
                : 'var(--text-secondary)';
        const topicTags = c.matched_topics.map(t =>
            `<span class="digest-topic-tag">${esc(t)}</span>`
        ).join('');

        return `
      <div class="digest-candidate">
        <div class="digest-candidate-header">
          <span class="digest-candidate-title">${c.url
                ? `<a href="${esc(c.url)}" target="_blank" rel="noopener" class="digest-link">${esc(c.title)}</a>`
                : esc(c.title)
            }</span>
          <span class="digest-candidate-score" style="color:${scoreColor}">${c.score.toFixed(2)}</span>
        </div>
        <div class="quota-bar" style="margin:0.2rem 0;">
          <div class="quota-bar-fill" style="width:${scoreWidth}%; background:${scoreColor}"></div>
        </div>
        <div class="digest-candidate-meta">
          <span class="digest-source">${esc(c.source)}</span>
          ${topicTags}
        </div>
      </div>
    `;
    }).join('');

    return `
    <div class="card digest-card" style="margin-top:1rem;">
      <div class="digest-header">
        <span class="metric-label">🔬 最新消化</span>
        <span class="digest-meta">
          ${digest.total_papers}件中 ${digest.candidates_selected}件選出
          <span class="digest-timestamp">${esc(timeStr)}</span>
        </span>
      </div>
      ${candidatesHtml}
    </div>
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
        const dotCls = item.status === 'ok' ? 'ok' : item.status === 'warn' ? 'warn' : 'error';
        const tagCls = item.status === 'ok' ? 'tag-success' : item.status === 'warn' ? 'tag-warning' : 'tag-error';
        const statusJa = item.status === 'ok' ? '正常' : item.status === 'warn' ? '注意' : 'エラー';
        return `<tr>
              <td>${esc(item.emoji)} ${esc(item.name)}</td>
              <td><span class="status-dot ${dotCls}"></span><span class="tag ${tagCls}">${esc(statusJa)}</span></td>
              <td style="color:var(--text-secondary);">${esc(item.detail)}</td>
            </tr>`;
    }).join('')}
        </tbody>
      </table>
    </div>
  `;
}
