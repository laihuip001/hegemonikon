# コード/コメント矛盾検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 軸数矛盾 (High): モジュールdocstringは「13軸」、`get_boot_context` docstringは「12軸」、`Axes` リストはA-N (14項目)、実装はそれ以上のコンポーネント（WAL, BC Violationなど）をロードしている。
- `generate_boot_template` (High): docstringは「モード別の穴埋めテンプレートを生成する」と主張しているが、実装は `MODE_REQUIREMENTS.get("detailed", {})` をハードコードしており、引数 `mode` も受け取らないため、実質的に `detailed` モード専用となっている。
- `THEOREM_REGISTRY` (Medium): コメントで「Boot 時に明示的に参照可能にする」と謳っているが、このファイル内で定義された後、一切参照・使用されていない（Dead Code）。
- ローカル関数シャドウイング (High): `_load_projects`, `_load_skills` が定義されているが、`get_boot_context` 内では `mekhane.symploke.boot_axes` から同名の関数をインポートして使用しており、ローカル定義が無視されている（Dead Code / Misleading）。
- 未使用定義 (Low): `SERIES_INFO`, `extract_dispatch_info` が定義されているが、ファイル内で使用されていない。

## 重大度
High
