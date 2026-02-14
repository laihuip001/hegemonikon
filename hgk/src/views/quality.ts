import { api } from '../api/client';
import type { DendronReportResponse } from '../api/client';
import { esc, applyCountUpAnimations, applyStaggeredFadeIn } from '../utils';

export async function renderQuality(): Promise<void> {
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
        <div class="metric-label">カバレッジ</div>
        <div class="metric ${coverageClass}"><span data-count-target="${parseFloat(displayPct)}">${displayPct}</span>%</div>
        <p style="color:var(--text-secondary); font-size:0.8rem; margin:0.25rem 0 0;">${s.files_with_proof} / ${s.total_files} ファイル検証済み</p>
      </div>
      <div class="card">
        <div class="metric-label">構造</div>
        <div class="metric"><span data-count-target="${s.total_dirs}">${s.total_dirs}</span></div>
        <p style="color:var(--text-secondary); font-size:0.8rem; margin:0.25rem 0 0;">${s.dirs_with_proof} / ${s.total_dirs} ディレクトリ検証済み</p>
      </div>
    </div>
    ${s.issues.length > 0 ? `
      <div class="card" style="margin-top:1rem;">
        <h3>課題 (${s.issues.length})</h3>
        <ul>${s.issues.map(i => `<li>${esc(i)}</li>`).join('')}</ul>
      </div>
    ` : ''}
  `;

    applyCountUpAnimations(app);
    applyStaggeredFadeIn(app);
}
