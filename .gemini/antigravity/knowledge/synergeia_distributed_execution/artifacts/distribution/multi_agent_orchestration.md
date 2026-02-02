# Synergeia Architecture: Multi-Agent Orchestration

## 1. システム階層

### 1.1 コーディネーション層 (n8n / OpenManus)

- CCL 式をパースし、各ステップを最適なスレッドに割り当てる。
- スレッド間のデータ（コンテキスト）の受け渡しを制御する。
- 全体の進行状況を監視し、エラー発生時に再試行またはフォールバックを指示する。

### 1.2 実行層 (Heterogeneous Threads)

- **Cognitive Thread**: 高度な判断が必要なタスク（Antigravity）。
- **Execution Thread**: コード作成、デバッグ、コマンド実行（Claude Code, Gemini, Codex）。
- **Research Thread**: 最新情報の検索、文献調査（Perplexity）。
- **Worker Thread**: Docker コンテナ内での自律的な一連の作業（OpenManus）。

### 1.3 統合層 (Result Aggregator)

- 各スレッドから返された断片的な知見・成果物を一つの最終回答、あるいは `/dox` (信念) へと統合する。

## 2. 通信プロトコル

| レベル | 方式 | ツール | 特徴 |
|:-------|:-----|:-------|:-----|
| **同期** | メモリ共有/API | REST/Context | 即時性が高い。小規模タスク向け。 |
| **非同期** | メッセージキュー | n8n / Polling | 長時間タスク向け。接続断に強い。 |
| **永続** | ファイルベース | Git / Markdown | 証跡が残る。大規模「労働」向け。 |

## 3. エラーハンドリング（フォールトトレランス）

分散実行時、単一スレッドの失敗はシステム全体の停止を意味しない。

- **Retry**: 一次的な接続エラー時は指数バックオフで再試行。
- **Fallback**: 特定のエージェントが応答しない場合、別系統のエージェント（例：Claude → Gemini）へ処理を切り替える。
- **Graceful Degradation**: 一部の非本質的なスレッドが失敗しても、残りの成果で可能な限りの回答を生成する。

## 4. コーディネーターの実装 (`coordinator.py`)

プロトタイプ実装として、以下の機能を備えた軽量コーディネーターを開発した。

- **CCL 解析**: 正規表現と文字分割により `||` (並列) と `|>` (パイプライン) を検出。
- **スレッド・レジストリ**: `/sop` -> Perplexity, `/ene` -> Gemini / Claude / Codex といった、演算子に基づいた自動ルーティング。
- **並列処理**: Python の `concurrent.futures.ThreadPoolExecutor` を使用し、I/O 待ち（API 応答）の間もメイン認知をブロックせずに並列実行。
- **ログ記録**: 各スレッドの応答、実行時間、コストを JSON 形式で `/experiments` に保存。

## 5. 対話的コーディネーション (`interactive.py`)

手動スレッド（Antigravity）の結果をリアルタイムで統合するための、CLI ベースのインタラクティブモードを実装した。

- **自動→手動のシーケンス**: API 駆動の自動スレッド（Perplexity 等）を先行実行し、その結果をコンテキストとして保持したまま、Antigravity（ユーザー/AI 本体）へ結果の入力を促す。
- **コンテキスト継承**: パイプライン実行において、前段のスレッド出力を入力プロンプトに表示し、一貫性のある作業継続を支援。

---
*Consolidated: 2026-02-01 | Synergeia Architecture v1.0*
