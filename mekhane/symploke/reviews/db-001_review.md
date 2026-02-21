# N+1検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical**: `_load_skills` 関数内にて、`sorted(skills_dir.iterdir())` のループ内で `skill_md.read_text()` が実行されている (N+1問題)。各スキルディレクトリごとにファイル読み込みが発生しており、スキル数が増加すると起動時間が線形に悪化する。

## 重大度
Critical
