# SELECT * 反対者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` が `registry.yaml` の全データを辞書リストとして返却しているが、呼び出し元の `print_boot_summary` ではフォーマット済み文字列しか使用していない（Medium）
- `_load_skills` が全スキルの本文（body）を含む辞書リストを返却しているが、フォーマット済み文字列以外で本文が使用される箇所がない（Medium）
- `get_boot_context` が全軸の生データを統合して返却しており、CLI出力に必要な情報量に対して過剰なデータをメモリに展開・返却している（Medium）

## 重大度
Medium
