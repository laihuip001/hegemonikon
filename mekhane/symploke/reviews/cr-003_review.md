# ソクラテス式問答者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- (Medium) ローダーの配置場所が不統一: なぜ `_load_projects` と `_load_skills` はこのファイル内で定義され、他の軸（`handoffs` 等）は `boot_axes.py` からインポートされるのか？
- (Medium) プロジェクトカテゴリの判定ロジックがハードコード: なぜ `kalon`, `aristos` などの特定のIDをコード内で直接判定する必要があるのか？
- (Medium) 環境依存のパスとURLがハードコード: なぜ `Path.home() / "oikos" ...` や `http://localhost:5678` が設定ファイル化されずに直接記述されているのか？

## 重大度
Medium
