# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_skills` 関数内 (L190-218周辺) で、`skills_dir.iterdir()` のループ毎に `skill_md.read_text()` を呼び出しています。これは N+1 問題（ループ内 I/O）に該当し、スキル数が増加すると起動時間が線形に悪化します。

## 重大度
Critical
