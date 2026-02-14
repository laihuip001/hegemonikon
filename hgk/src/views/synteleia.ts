import './css/audit.css';
import { api } from '../api/client';
import { esc } from '../utils';

export async function renderSynteleiaView(): Promise<void> {
    const app = document.getElementById('view-content');
    if (!app) return;

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
