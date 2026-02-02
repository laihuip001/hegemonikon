# Implementation: Phase 6 — Workflow Executor & Synergeia Integration

## 1. 概要
Phase 6 では、Hermēneus を実運用ワークフローのハブとするため、ワークフロー定義の管理機能（Registry）と、Synergeia との双方向連携（Adapter）を実装した。これにより、現実の `/noe+` や `/bou+` といった cognitive workflows を構造化・検証付きで実行可能となった。

## 2. コアコンポーネント

### 2.1 Workflow Registry (`registry.py`)
- **定義ロード**: `.agent/workflows/` 内の Markdown ファイルからワークフローのステージやメタデータをパース。
- **CCL マッピング**: 各ワークフロー名を CCL の演算子（例: `noe` → `/noe+`）として解決。

### 2.2 Workflow Executor (`executor.py`)
- **パイプライン制御**: `compile` → `execute` → `verify` → `audit` の一連の流れを `ExecutionPipeline` としてカプセル化。
- **バッチ実行**: `BatchExecutor` により、複数のタスクを並列または順次で一括処理。

### 2.3 Synergeia Adapter (`synergeia_adapter.py`)
- **分散スレッド連携**: Synergeia のスレッド設定を Hermēneus の実行プランに変換。
- **Adapter パターン**: スレッドごとのタイムアウト管理、確信度の集計、および Synergeia 形式のレポート生成。

## 3. Synergeia 側からの呼び出し
Synergeia の `coordinator.py` は、複雑なタスクに対して Hermēneus を優先的に呼び出し、LMQL による「保証付き実行」を選択する。Hermēneus は「構造の番人」として、分散スレッドの出力を SEL に適合させる。

---
*最終更新: 2026-02-01 | Hermēneus Phase 6 Implementation*
