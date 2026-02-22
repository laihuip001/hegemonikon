# Immutableの司祭 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **グローバル可変状態 (High)**: `THEOREM_REGISTRY` (L30), `SERIES_INFO` (L71), `MODE_REQUIREMENTS` (L527) が通常の辞書として定義されており、実行時に変更可能です。これらは `types.MappingProxyType` や `frozen=True` なデータクラスとして定義すべきです。
- **可変設定リスト (Medium)**: `MODE_REQUIREMENTS` 内の `required_sections` (L531, L547) がリストとして定義されています。設定値は不変であるべきため、タプルを使用すべきです。
- **データ構造のプリミティブ依存 (Medium)**: 構造化データ（`THEOREM_REGISTRY` の値や関数の戻り値）が辞書で表現されています。`@dataclass(frozen=True)` を使用して不変性と型安全性を保証すべきです。

## 重大度
High
