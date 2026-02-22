# 認知チャンク分析者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Line 179: 1行に4つの `len()` 呼び出しと文字列フォーマットが含まれており、認知負荷が高い (Medium)
- Line 513: 単一の `print` 文に9つの変数展開、三項演算子、ネストされた f-string が含まれており、可読性を著しく損なっている (Medium)
- Line 685: Line 179 と同様に、1行に多数の `len()` 呼び出しが含まれている (Medium)
- Line 733, 752, 762, 774, 790, 825: `postcheck_boot_report` 関数内の詳細文字列生成において、三項演算子と文字列結合が複雑に絡み合っており、認知負荷が高い (Medium)

## 重大度
Medium
