# AI のデスクトップアプリを作った話

> **ID**: E4
> **想定媒体**: Zenn（技術記事）→ Note
> **想定読者**: フルスタックエンジニア
> **フック**: Tauri + Vite + FastAPI で AI ダッシュボードを構築

---

## 本文構成（案）

### 1. なぜデスクトップアプリ？

- Web だとブラウザ依存
- Tauri はメモリ効率が良い (Electron 比 1/10)
- ローカルの Python バックエンドと直結

### 2. 技術スタック

| 層 | 技術 |
|:---|:-----|
| フロントエンド | Vite + React |
| バックエンド | FastAPI (Python) |
| ラッパー | Tauri (Rust) |
| データ | PKS (ローカルインデックス) |

### 3. 表示問題との格闘

- Skeleton loader が消えない問題
- WebView と Vite dev server の接続
- CORS 設定の罠

### 4. AI が書いたコードの割合

- Rust (Tauri): 80% AI
- React: 90% AI
- Python (FastAPI): 95% AI
- デバッグ: 50% AI + 50% 人間

---

*関連: C2 (787コミット), C5 (MCP統合)*
