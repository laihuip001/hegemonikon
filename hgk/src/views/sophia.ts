import './css/content.css';
import { esc } from '../utils';
import { kiList, kiGet, kiCreate, kiUpdate, kiDelete, kiSearch } from '../api/client';
import type { KIListItem, KIDetail } from '../api/client';
import { marked } from 'marked';

export async function renderSophiaView(): Promise<void> {
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
