# ソクラテス式問答者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 理由不明: `THEOREM_REGISTRY` のハードコード (Medium)
  - なぜ統合スクリプト内で定義しているのか？ `kernel/` が真理の源ではないのか？
- 理由不明: `_load_projects` 内のハードコードされたID分岐 (Medium)
  - なぜ `kalon`, `ccl` などのIDをコード内で判定しているのか？ `registry.yaml` のメタデータで制御しない理由は？
- 理由不明: 環境依存のハードコード (Medium)
  - なぜ n8n の URL (`localhost:5678`) や Agent 名 (`Claude`) が固定なのか？ 設定ファイルや環境変数に切り出さない理由は？
- 理由不明: インポート位置の不統一 (Low)
  - なぜ `yaml` や `urllib` は関数内インポートで、`json` はトップレベルなのか？ 起動速度最適化の意図なら統一性がない。
- 理由不明: マジックナンバーの使用 (Low)
  - なぜ `summary[:50]` や `max(..., 25)` なのか？ これらの値の根拠は？

## 重大度
Medium
