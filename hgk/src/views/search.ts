import './css/content.css';
import { api } from '../api/client';
import type { SymplokeSearchResponse, SymplokeSearchResultItem } from '../api/client';
import { esc, applyStaggeredFadeIn } from '../utils';

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

export async function renderSearch(): Promise<void> {
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
    <h1>統合検索</h1>
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
          <div class="empty-state">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🔍</div>
            <p>「${esc(query)}」に一致する結果がありません</p>
            <small style="color:var(--text-secondary);">検索対象: ${res.sources_searched.map(s => SOURCE_LABELS[s] ?? s).join(', ')}</small>
          </div>`;
                return;
            }

            const sourceSummary = res.sources_searched
                .map(s => `<span style="color:${SOURCE_COLORS[s] ?? '#8b949e'};">${SOURCE_LABELS[s] ?? s}</span>`)
                .join(' · ');

            resultsDiv.innerHTML = `
        <div class="search-summary" style="margin:0.75rem 0; color:var(--text-secondary); font-size:0.85rem;">
          <span class="metric-label" style="display:inline;">${res.total} 件</span> — ${sourceSummary}
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

            applyStaggeredFadeIn(resultsDiv);
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
