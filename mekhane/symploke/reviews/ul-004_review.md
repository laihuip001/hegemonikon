# コード量減少主義者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`get_boot_context` の肥大化**: `IntentWALManager`, `bc_violation_logger`, `n8n` 通知などのロジックが直書きされており、関数が長大化している。これらを `boot_axes.py` に委譲すべきである（`boot_axes.py` には既に `load_violations` があるが使われていない）。
- **`_load_projects` / `_load_skills` の配置**: 合計約130行の実装がここにあり、`boot_axes.py` から参照されている。これらを `boot_axes.py` または専用モジュールに移動すれば、このファイルは大幅に削減できる。
- **`postcheck_boot_report` の記述冗長性**: チェック項目の定義が手続き的で記述量が多い。データ構造駆動にリファクタリングすれば行数を削減可能。
- **`THEOREM_REGISTRY` の巨大リテラル**: 50行近くを占有している。外部定義 (`kernel` 等) からインポートすれば削減可能。

## 重大度
Low
