# Protocolの伝道師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **WAL処理における具体的データクラスへの依存 (Low)**
  - `get_boot_context` 内で `IntentWALManager` から返される `prev_wal` オブジェクトの属性（`progress`, `session_goal`, `status`, `action`）に直接アクセスしている。
  - これは具体的クラス `IntentWAL` への暗黙的な依存であり、構造的型付けの機会を逃している。
  - `WALEntryProtocol` (status, action) および `WALStateProtocol` (progress, session_goal) を定義し、振る舞いに対してコードを書くべきである。

- **Dispatch Planにおける具体的構造への依存 (Low)**
  - `extract_dispatch_info` 内で `dispatcher.dispatch()` の戻り値 `plan` の構造（`primary.workflow`, `alternatives[].workflow`）を具体的クラス `DispatchPlan` に依存して処理している。
  - `DispatchItemProtocol` (workflow) および `DispatchPlanProtocol` (primary, alternatives) を定義することで、ディスパッチャの実装詳細から疎結合にできる。

- **Handoff Itemの型なしダックタイピング (Low)**
  - `handoffs_result["latest"]` に対して `.metadata` や `.content` にアクセスしているが、型定義が存在しない。
  - 明示的な `HandoffItemProtocol` を定義することで、期待される構造をコード上で表現すべきである。

## 重大度
Low
