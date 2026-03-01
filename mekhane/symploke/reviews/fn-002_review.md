# 辞書ディスパッチ推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内にプロジェクトをカテゴリ分類するための6分岐のif-elif-elseチェーンが存在します。状態（status）やID、パスの接頭辞を判定するswitch-likeなパターンとなっており、辞書ディスパッチやルーティングテーブルへのリファクタリングが推奨されます。 (Medium)

## 重大度
Medium
