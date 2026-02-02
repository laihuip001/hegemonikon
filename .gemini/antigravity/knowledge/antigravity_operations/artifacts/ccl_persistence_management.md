# CCL Persistence & Session Management (2026-01-29)

> **対象**: Mnēmē レイヤー (.hegemonikon)
> **目的**: セッションを跨いだ意図の学習と、実行記録の隔離管理。

---

## 1. 意図パターンの永続化 (Doxa Persistence)

CCL Generator v2.0 は、成功した変換例を `H4 Doxa` 実装として自動的に永続化する。

### 1.1 管理ファイル

`/.hegemonikon/ccl_patterns.json`

### 1.2 運用のメリット

- **環境ポータビリティ**: この JSON ファイルを移行することで、別の環境でも AI が Creator の意図（日本語意図 → CCL の癖）を即座に再現できる。
- **オフライン動作**: LLM (Layer 1) が利用不可な状況でも、過去に成功した複雑なパターン (Layer 2) は再現可能。

### 1.3 マクロ・ライブラリ (Macro Library)

`@name` で参照される定型認知パターンは、`ccl_macros.json` (または Doxa 学習結果) に集約される。これらは「個人用認知のショートカット」として、セッション開始時の `boot` シーケンスで脳内にロードされることが推奨される。

---

## 2. セッション分離型トレース (Session Isolation)

### 2.1 トレース・リポジトリ

`/mneme/.hegemonikon/ccl_traces/`

### 2.2 ディレクトリ構成

各実行セッションはタイムスタンプ ID を持ち、以下の 3 つの要素を保持する。

- **trace.log**: 逐次イベント。
- **state.json**: 機械可読な状態。
- **summary.md**: 人間可読なサマリー。

### 2.3 セッションの復旧 (Session Resumption)

CLI ツールからトレースを継続する場合、`load_latest()` または `load_session(session_id)` メソッドを利用してセッション状態をメモリへ復元し、`state.json` を更新しながら追跡を継続する。これにより、CLI プロセスを跨いだコンテキストの断絶を防ぐ。

---

## 3. メンテナンス・ルール

- **パターンの整合性**: `ccl_patterns.json` は定期的な `H4 Doxa` 健康診断の対象とし、古いまたは矛盾するパターンをクリーンアップする。
- **トレースのアーカイブ**: 蓄積されたトレースは、後続の `Audit` ワークフローによって「週次振り返り」などの栄養素として抽出される。

---

## 4. Session Export Reliability (Double-Export System)

To prevent session loss due to agent oversight, a two-tiered automatic persistence system is active.

### 4.1 Hourly Auto-Export (Cron)
The system runs `mekhane/anamnesis/auto_export.sh` every hour. This script detects active Antigravity sessions via the CDP port and saves them to the repository logs.

### 4.2 Programmatic AI Export (MCP)
The `hermeneus_export_session` tool allows the AI to trigger a context-aware export plan. This tool is a mandatory component of the `/bye` workflow and requires no user confirmation.

---
*Reference: mekhane/ccl/doxa_learner.py, mekhane/ccl/tracer.py, mekhane/anamnesis/auto_export.sh*
