import './css/audit.css';
import { api } from '../api/client';
import type { DigestCandidate } from '../api/client';
import { esc } from '../utils';

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

export async function renderDigestorView(): Promise<void> {
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

        let activeTab: 'reports' | 'news' = 'news';

        function render() {
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

            app.querySelectorAll('.dg-tab').forEach(btn => {
                btn.addEventListener('click', () => {
                    activeTab = (btn as HTMLElement).dataset.tab as 'reports' | 'news';
                    render();
                });
            });

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
