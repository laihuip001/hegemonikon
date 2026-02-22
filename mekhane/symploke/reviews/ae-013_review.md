# シンプリシティの門番 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical (Dead Code)**: 定数 `THEOREM_REGISTRY` と `SERIES_INFO` はテスト (`test_theorem_registry.py`) でのみ参照されており、プロダクションコード内では未使用です。これらは `boot_axes.py` に移動するか、不要であれば削除すべきです。
- **Critical (Dead Code)**: 関数 `extract_dispatch_info`, `_load_projects`, `_load_skills` は定義されていますが、このファイル内でも外部からも呼び出されていません（`get_boot_context` は `boot_axes` から同名の関数をインポートして使用しています）。これらは完全なデッドコードです。
- **Medium (Redundant Logic)**: `postcheck_boot_report` 内の `epsilon_precision` 計算ロジック（BS-3b fix）は、ブートスクリプトとしては過剰に複雑で、保守性を低下させています。
- **Low (Unused Imports)**: 未使用関数 (`_load_projects` 等) のためにインポートされている `yaml` などのライブラリが、クリーンアップ後には不要になります。

## 重大度
Critical
