# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **単純な文字数計算 (len())**: `generate_boot_template` や `postcheck_boot_report` において、`len()` を使用して文字列の長さを判定している (Low)。絵文字や結合文字が含まれる場合、視覚的な文字数と一致しないため、意図したバリデーション（例: 3000文字以上）が不正確になる可能性がある。
- **Unicode文字列の単純なスライス**: `_load_projects` (Line 147), `get_boot_context` (Line 282), `generate_boot_template` (Line 625) において、`summary[:50]` や `content[:200]` のような単純なスライスが行われている (Low)。結合文字やサロゲートペアの途中での切断が発生し、表示崩れや文字化けの原因となるリスクがある。
- **正規化の欠如**: 外部ファイル (`registry.yaml`, `SKILL.md` 等) から読み込まれたテキストに対して、`unicodedata.normalize` による正規化（NFC等）が行われていない (Low)。異なる正規化形式が混在すると、文字列比較や検索で意図しない不一致が発生する可能性がある。

## 重大度
Low
