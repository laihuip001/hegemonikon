# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_skills` 関数内 (L213-L221付近) で、ディレクトリをイテレートしながら `SKILL.md` を個別に `read_text` している (N+1 File I/O)。ループ内クエリはパフォーマンス劣化の要因となる。

## 重大度
Critical
