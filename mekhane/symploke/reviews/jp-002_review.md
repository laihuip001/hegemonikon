# 敬体常体統一者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- [Low] 384行目 `lines.append("<!-- FILL: registry.yaml が見つかりません -->")` で敬体「見つかりません」が使用されています。他のコメントや出力（「必須」「生成する。」など）が常体であるため、文体が混在しています。

## 重大度
Low
