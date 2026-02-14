import './css/notifications.css';
import { api } from '../api/client';
import type { PKSPushResponse, PKSNugget, PKSStatsResponse } from '../api/client';
import { getCurrentRoute, esc, startPolling } from '../utils';

export async function renderPKS(): Promise<void> {
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
    if (getCurrentRoute() !== 'pks') return;

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

    document.getElementById('pks-refresh-btn')?.addEventListener('click', () => {
        void renderPKSContent();
    });

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
