# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical**: `_load_skills` (L163) 関数内で、`skills_dir.iterdir()` (L175) によるループの中で `skill_md.read_text()` (L179) が実行されており、スキル数に比例した I/O (N+1問題) が発生している。

## 重大度
Critical
