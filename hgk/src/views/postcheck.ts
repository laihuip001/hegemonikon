import { api } from '../api/client';
import type { SELListResponse } from '../api/client';
import { esc } from '../utils';

export async function renderPostcheck(): Promise<void> {
    let selList: SELListResponse;
    try {
        selList = await api.postcheckList();
    } catch (err) {
        const app = document.getElementById('view-content')!;
        app.innerHTML = `<div class="card status-error">ポストチェック利用不可: ${esc((err as Error).message)}</div>`;
        return;
    }

    const app = document.getElementById('view-content')!;

    const wfCards = selList.items.map(item => {
        const modes = Object.keys(item.modes);
        const modeTags = modes.map(m => `<span class="tag tag-info">${esc(m)}</span>`).join(' ');
        return `<div class="card postcheck-wf-card" style="margin-bottom:0;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <div style="font-weight:600; font-size:0.95rem; margin-bottom:0.35rem;">/${esc(item.wf_name)}</div>
          <div style="display:flex; gap:0.3rem; flex-wrap:wrap;">${modeTags || '<span class="tag" style="opacity:0.4;">default</span>'}</div>
        </div>
        <button class="btn btn-sm run-postcheck-btn" data-wf="${esc(item.wf_name)}">実行</button>
      </div>
    </div>`;
    }).join('');

    app.innerHTML = `
    <h1>ポストチェック</h1>
    <div class="card" style="margin-bottom:1.5rem;">
      <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
        <h3 style="margin:0;">ワークフロー登録</h3>
        <span class="tag tag-info">${selList.total} 件</span>
      </div>
      <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap:0.75rem;">
        ${wfCards}
      </div>
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

    document.querySelectorAll('.run-postcheck-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const wfName = btn.getAttribute('data-wf') ?? '';
            (document.getElementById('pc-wf') as HTMLInputElement).value = wfName;
            document.getElementById('pc-content')?.focus();
        });
    });
}
