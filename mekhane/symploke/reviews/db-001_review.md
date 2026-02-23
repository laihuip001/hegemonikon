# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical**: `_load_skills` 関数内での N+1 File I/O
  - ループ内で `skill_md.exists()` および `skill_md.read_text()` を実行している。スキル数（ディレクトリ数）に比例してI/O操作が増加するため、パフォーマンスに悪影響を与える可能性がある。

## 重大度
Critical
