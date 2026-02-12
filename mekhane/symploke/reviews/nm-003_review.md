# 略語撲滅の十字軍 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `tg` (L362, L363): `TaskGroup` の略語。文脈がないと不明瞭であり、`task_group` と展開すべき。 (Medium)
- `resp` (L158, L160, L165, L167, L168): `response` の慣習的略語。ドメイン外の読者への配慮として展開すべき。 (Medium)
- `pr` (L223), `pr_url` (L224, L233): `Pull Request` の略語。開発者には通じるが、正式名称 `pull_request` を推奨。 (Low)
- `func` (L113, L122): `function` の略語。 (Low)
- `OTEL` (L37, L161): `OpenTelemetry` の略語。 (Low)
- `state_str` (L73, L83, L86, L92): `state_string` の略語。 (Low)

## 重大度
Medium
