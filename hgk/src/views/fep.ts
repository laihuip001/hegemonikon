import { api } from '../api/client';
import type { FEPStateResponse, FEPStepResponse, FEPDashboardResponse } from '../api/client';
import { getCurrentRoute, esc, applyCountUpAnimations, applyStaggeredFadeIn, startPolling } from '../utils';

export async function renderFep(): Promise<void> {
    await renderFepContent();
    startPolling(renderFepContent, 30_000);
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
    if (getCurrentRoute() !== 'fep') return;

    const maxBelief = Math.max(...state.beliefs, 0.01);
    const beliefsHtml = state.beliefs.map((b: number, idx: number) =>
        `<div class="belief-bar" style="height: ${(b / maxBelief) * 100}%" title="[${idx}] ${b.toFixed(4)}"></div>`
    ).join('');

    const epsilonEntries = Object.entries(state.epsilon)
        .map(([k, v]) => `<tr><td>${esc(k)}</td><td>${(v as number).toFixed(4)}</td></tr>`)
        .join('');

    const actionEntries = dashboard ? Object.entries(dashboard.action_distribution)
        .sort(([, a], [, b]) => (b as number) - (a as number)) : [];
    const actionMax = actionEntries.length > 0 ? Math.max(...actionEntries.map(([, v]) => v as number), 1) : 1;
    const actionDist = actionEntries.map(([k, v]) => {
        const pct = ((v as number) / actionMax * 100).toFixed(0);
        return `<tr><td>${esc(k)}</td><td><div class="dist-bar-wrap"><div class="dist-bar"><div class="dist-bar-fill" style="width:${pct}%"></div></div><span class="dist-bar-value">${String(v)}</span></div></td></tr>`;
    }).join('');

    const seriesEntries = dashboard ? Object.entries(dashboard.series_distribution)
        .sort(([, a], [, b]) => (b as number) - (a as number)) : [];
    const seriesMax = seriesEntries.length > 0 ? Math.max(...seriesEntries.map(([, v]) => v as number), 1) : 1;
    const seriesDist = seriesEntries.map(([k, v]) => {
        const pct = ((v as number) / seriesMax * 100).toFixed(0);
        return `<tr><td>${esc(k)}</td><td><div class="dist-bar-wrap"><div class="dist-bar"><div class="dist-bar-fill" style="width:${pct}%"></div></div><span class="dist-bar-value">${String(v)}</span></div></td></tr>`;
    }).join('');

    app.innerHTML = `
    <h1>FEP エージェント <small class="poll-badge">自動更新 30秒</small></h1>
    <div class="card">
      <div class="metric-label">信念分布 (${state.beliefs.length} 次元)</div>
      <div class="beliefs-chart">${beliefsHtml}</div>
      <small style="color:var(--text-secondary);">ホバーで値表示。最大値 = ${maxBelief.toFixed(4)}</small>
    </div>
    <div class="card step-panel">
      <div class="metric-label">推論ステップ実行</div>
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <label for="obs-input">観測値 (0-47):</label>
        <input type="number" id="obs-input" class="input" min="0" max="47" value="0" style="width:80px;" />
        <button id="step-btn" class="btn">ステップ</button>
      </div>
      <div id="step-result" style="margin-top:0.5rem;"></div>
    </div>
    <div class="grid">
      <div class="card">
        <div class="metric-label">Epsilon</div>
        <table class="data-table">${epsilonEntries}</table>
      </div>
      <div class="card">
        <div class="metric-label">履歴</div>
        <div class="metric"><span data-count-target="${state.history_length}">${state.history_length}</span></div>
        <p style="color:var(--text-secondary); font-size:0.8rem; margin:0.25rem 0 0;">推論ステップ</p>
      </div>
      ${dashboard ? `
      <div class="card">
        <div class="metric-label">行動分布</div>
        <table class="data-table">${actionDist || '<tr><td colspan="2">データなし</td></tr>'}</table>
      </div>
      <div class="card">
        <div class="metric-label">シリーズ分布</div>
        <table class="data-table">${seriesDist || '<tr><td colspan="2">データなし</td></tr>'}</table>
      </div>
      ` : ''}
    </div>
  `;

    applyCountUpAnimations(app);
    applyStaggeredFadeIn(app);

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
            void renderFepContent();
        } catch (e) {
            resultDiv.innerHTML = `<span class="status-error">ステップ失敗: ${esc((e as Error).message)}</span>`;
        }
    });
}
