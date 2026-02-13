# Doxa: LS API Playground は幻想、extension.js が真実の源泉

> **生成日**: 2026-02-13
> **セッション**: cf91660b — Synteleia Vision + Sandbox 隔離
> **CCL**: `@learn`
> **確信度**: [確信: 92%] (SOURCE: extension.js proto3 setEnumType() を直接確認)

---

## D1: Playground は LS API に存在しない

Antigravity IDE の「Playground」は LS のプロトコル層に存在しない。
`CortexTrajectorySource` enum 全量:

| 数値 | 名前 |
|:---|:---|
| 0 | UNSPECIFIED |
| 1 | CASCADE_CLIENT |
| 2 | EXPLAIN_PROBLEM |
| 3 | REFACTOR_FUNCTION |
| 4 | EVAL |
| 5 | EVAL_TASK |
| 6 | ASYNC_PRR |
| 7 | ASYNC_CF |
| 8 | ASYNC_SL |
| 9 | ASYNC_PRD |
| 10 | ASYNC_CM |
| 12 | INTERACTIVE_CASCADE |
| 13 | REPLAY |
| 15 | SDK |

**「Playground」は Electron UI のグルーピング表示。**

## D2: extension.js > strings binary

`extension.js` の proto3 `setEnumType()` 呼び出しが全 enum 値と数値マッピングを正確に保持。
`strings binary` はノイズが多く数値が不明。

**今後の LS リバースエンジニアリングの基本手法**: extension.js の grep から始める。

## D3: ワークスペース隔離パターン

IDE で新しいフォルダを開く → 専用 LS 起動 → AntigravityClient の `workspace` パラメータで接続先を切替。

**ハイフン→アンダースコア変換に注意**: `synteleia-sandbox` → workspace_id `synteleia_sandbox`

## 法則化

- **「存在を前提とした探索は時間を浪費する」** — まず enum 定義を確認してから探索すべき
- **「同じ情報の別ソースを持つ」** — バイナリ strings と extension.js は同じ情報の異なるビュー。より正確なソースを選べ
