# AIDB記事収集: 並列実行ガイド

このドキュメントでは、5つの独立したチャットセッションでAIDB記事を並列収集するための手順を説明します。

## 📋 前提条件

1. すべてのチャットは同じワークスペース `C:\Users\raikh\Forge` にアクセス可能
2. ブラウザでAIDBにログイン済み（Cookie共有）
3. 各チャットは独立したバッチIDを使用

## 🗂️ バッチ分割（594件、Index 0始まり）

> [!NOTE]
> Index 1-30は既にこのチャットで処理済みです。

| Batch ID | Index範囲 | 件数 | 担当チャット |
|----------|-----------|------|--------------|
| 1 | 31-150 | 120件 | 新規チャット1 |
| 2 | 151-270 | 120件 | 新規チャット2 |
| 3 | 271-390 | 120件 | 新規チャット3 |
| 4 | 391-510 | 120件 | 新規チャット4 |
| 5 | 511-594 | 84件 | 新規チャット5 |

## 🚀 各チャット用プロンプト

### Batch 1 (Index 31-150)

```
# AIDB記事収集 - Batch 1 (Index 31-150)

以下の手順でAIDB記事を収集してください。

## 対象
- URL一覧: `C:\Users\raikh\Forge\Raw\aidb\_index\url_list.txt` の31行目から150行目
- 保存スクリプト: `python scripts/phase3-save-batch-parallel.py 1`
- 一時ファイル: `temp_batch_data_1.json`

## 収集手順（各記事に対して）

1. **メタデータ取得**: browser_subagentでURLにアクセスし、以下のJSを実行
```javascript
(() => {
  const result = {};
  result.url = window.location.href;
  result.title = document.querySelector('h1')?.innerText?.trim() || "";
  let dateText = document.querySelector('.p-article__date')?.innerText?.trim() || document.querySelector('.entry-date')?.innerText?.trim();
  if (!dateText) {
      const match = document.body.innerText.match(/\d{4}\.\d{2}\.\d{2}/);
      dateText = match ? match[0] : "";
  }
  result.date = dateText;
  const tagElements = Array.from(document.querySelectorAll('a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"], .post_tag a'));
  result.metadata = { tags: [...new Set(tagElements.map(el => el.innerText.trim()).filter(t => t.length > 0))] };
  return JSON.stringify(result);
})()
```

2. **Chunk 1取得 (0-6000文字)**: 同URLで以下のJSを実行
3. **Chunk 2取得 (6000-末尾)**: 必要に応じてChunk 3も取得
4. **保存**: メタデータとMarkdownを結合し、`temp_batch_data_1.json` に保存後、スクリプト実行:
   `python scripts/phase3-save-batch-parallel.py 1`

## 注意事項
- 404エラーはスキップし、URLをログに記録
- 1記事ずつ処理して段階的に進行
```

---

### Batch 2 (Index 151-270)

```
# AIDB記事収集 - Batch 2 (Index 151-270)

以下の手順でAIDB記事を収集してください。

## 対象
- URL一覧: `C:\Users\raikh\Forge\Raw\aidb\_index\url_list.txt` の151行目から270行目
- 保存スクリプト: `python scripts/phase3-save-batch-parallel.py 2`
- 一時ファイル: `temp_batch_data_2.json`

## 収集手順（各記事に対して）

1. **メタデータ取得**: browser_subagentでURLにアクセスし、以下のJSを実行
```javascript
(() => {
  const result = {};
  result.url = window.location.href;
  result.title = document.querySelector('h1')?.innerText?.trim() || "";
  let dateText = document.querySelector('.p-article__date')?.innerText?.trim() || document.querySelector('.entry-date')?.innerText?.trim();
  if (!dateText) {
      const match = document.body.innerText.match(/\d{4}\.\d{2}\.\d{2}/);
      dateText = match ? match[0] : "";
  }
  result.date = dateText;
  const tagElements = Array.from(document.querySelectorAll('a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"], .post_tag a'));
  result.metadata = { tags: [...new Set(tagElements.map(el => el.innerText.trim()).filter(t => t.length > 0))] };
  return JSON.stringify(result);
})()
```

2. **Chunk 1取得 (0-6000文字)**: 同URLで以下のJSを実行
3. **Chunk 2取得 (6000-末尾)**: 必要に応じてChunk 3も取得
4. **保存**: メタデータとMarkdownを結合し、`temp_batch_data_2.json` に保存後、スクリプト実行:
   `python scripts/phase3-save-batch-parallel.py 2`

## 注意事項
- 404エラーはスキップし、URLをログに記録
- 1記事ずつ処理して段階的に進行
```

---

### Batch 3 (Index 271-390)

```
# AIDB記事収集 - Batch 3 (Index 271-390)

以下の手順でAIDB記事を収集してください。

## 対象
- URL一覧: `C:\Users\raikh\Forge\Raw\aidb\_index\url_list.txt` の271行目から390行目
- 保存スクリプト: `python scripts/phase3-save-batch-parallel.py 3`
- 一時ファイル: `temp_batch_data_3.json`

## 収集手順（各記事に対して）

1. **メタデータ取得**: browser_subagentでURLにアクセスし、以下のJSを実行
```javascript
(() => {
  const result = {};
  result.url = window.location.href;
  result.title = document.querySelector('h1')?.innerText?.trim() || "";
  let dateText = document.querySelector('.p-article__date')?.innerText?.trim() || document.querySelector('.entry-date')?.innerText?.trim();
  if (!dateText) {
      const match = document.body.innerText.match(/\d{4}\.\d{2}\.\d{2}/);
      dateText = match ? match[0] : "";
  }
  result.date = dateText;
  const tagElements = Array.from(document.querySelectorAll('a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"], .post_tag a'));
  result.metadata = { tags: [...new Set(tagElements.map(el => el.innerText.trim()).filter(t => t.length > 0))] };
  return JSON.stringify(result);
})()
```

2. **Chunk 1取得 (0-6000文字)**: 同URLで以下のJSを実行
3. **Chunk 2取得 (6000-末尾)**: 必要に応じてChunk 3も取得
4. **保存**: メタデータとMarkdownを結合し、`temp_batch_data_3.json` に保存後、スクリプト実行:
   `python scripts/phase3-save-batch-parallel.py 3`

## 注意事項
- 404エラーはスキップし、URLをログに記録
- 1記事ずつ処理して段階的に進行
```

---

### Batch 4 (Index 391-510)

```
# AIDB記事収集 - Batch 4 (Index 391-510)

以下の手順でAIDB記事を収集してください。

## 対象
- URL一覧: `C:\Users\raikh\Forge\Raw\aidb\_index\url_list.txt` の391行目から510行目
- 保存スクリプト: `python scripts/phase3-save-batch-parallel.py 4`
- 一時ファイル: `temp_batch_data_4.json`

## 収集手順（各記事に対して）

1. **メタデータ取得**: browser_subagentでURLにアクセスし、以下のJSを実行
```javascript
(() => {
  const result = {};
  result.url = window.location.href;
  result.title = document.querySelector('h1')?.innerText?.trim() || "";
  let dateText = document.querySelector('.p-article__date')?.innerText?.trim() || document.querySelector('.entry-date')?.innerText?.trim();
  if (!dateText) {
      const match = document.body.innerText.match(/\d{4}\.\d{2}\.\d{2}/);
      dateText = match ? match[0] : "";
  }
  result.date = dateText;
  const tagElements = Array.from(document.querySelectorAll('a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"], .post_tag a'));
  result.metadata = { tags: [...new Set(tagElements.map(el => el.innerText.trim()).filter(t => t.length > 0))] };
  return JSON.stringify(result);
})()
```

2. **Chunk 1取得 (0-6000文字)**: 同URLで以下のJSを実行
3. **Chunk 2取得 (6000-末尾)**: 必要に応じてChunk 3も取得
4. **保存**: メタデータとMarkdownを結合し、`temp_batch_data_4.json` に保存後、スクリプト実行:
   `python scripts/phase3-save-batch-parallel.py 4`

## 注意事項
- 404エラーはスキップし、URLをログに記録
- 1記事ずつ処理して段階的に進行
```

---

### Batch 5 (Index 511-595)

```
# AIDB記事収集 - Batch 5 (Index 511-595)

以下の手順でAIDB記事を収集してください。

## 対象
- URL一覧: `C:\Users\raikh\Forge\Raw\aidb\_index\url_list.txt` の511行目から595行目
- 保存スクリプト: `python scripts/phase3-save-batch-parallel.py 5`
- 一時ファイル: `temp_batch_data_5.json`

## 収集手順（各記事に対して）

1. **メタデータ取得**: browser_subagentでURLにアクセスし、以下のJSを実行
```javascript
(() => {
  const result = {};
  result.url = window.location.href;
  result.title = document.querySelector('h1')?.innerText?.trim() || "";
  let dateText = document.querySelector('.p-article__date')?.innerText?.trim() || document.querySelector('.entry-date')?.innerText?.trim();
  if (!dateText) {
      const match = document.body.innerText.match(/\d{4}\.\d{2}\.\d{2}/);
      dateText = match ? match[0] : "";
  }
  result.date = dateText;
  const tagElements = Array.from(document.querySelectorAll('a[href*="/archives/type-tag/"], a[href*="/archives/tech-tag/"], a[href*="/archives/app-tag/"], .post_tag a'));
  result.metadata = { tags: [...new Set(tagElements.map(el => el.innerText.trim()).filter(t => t.length > 0))] };
  return JSON.stringify(result);
})()
```

2. **Chunk 1取得 (0-6000文字)**: 同URLで以下のJSを実行
3. **Chunk 2取得 (6000-末尾)**: 必要に応じてChunk 3も取得
4. **保存**: メタデータとMarkdownを結合し、`temp_batch_data_5.json` に保存後、スクリプト実行:
   `python scripts/phase3-save-batch-parallel.py 5`

## 注意事項
- 404エラーはスキップし、URLをログに記録
- 1記事ずつ処理して段階的に進行
```

---

## 🔄 並列実行後の統合

すべてのバッチが完了したら、以下のコマンドでマニフェストを統合：

```bash
python scripts/merge-manifests.py
```

これにより `manifest_1.jsonl` 〜 `manifest_5.jsonl` が `manifest.jsonl` に統合されます。

## 📊 進捗確認

各バッチの進捗は以下で確認できます：

```bash
# 各バッチのマニフェスト行数を確認
(Get-Content Raw/aidb/_index/manifest_1.jsonl).Count
(Get-Content Raw/aidb/_index/manifest_2.jsonl).Count
# ... など
```
