# raise再投げ監視官 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- (High) `synedrion_review` メソッド内 (L696): `except ImportError:` ブロック内で `raise ImportError(...)` が使用されています。`from` 句が欠落しているため、元の例外（モジュール内部のエラーなど）の情報が失われています。本来は `from e` を付与して原因を保存すべきです。

## 重大度
High
