# ソクラテス式問答者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **THEOREM_REGISTRY のハードコード (Medium)**
  - なぜここで定理定義を再定義しているのか？
  - なぜ `kernel/` や `hermeneus/` の正本を参照しないのか？
  - なぜ整合性を犠牲にしてまでここで定義する必要があるのか？

- **プロジェクト分類のハードコード (Medium)**
  - なぜ `_load_projects` 内で特定のプロジェクトID (`kalon`, `aristos`, `autophonos`) をハードコードしているのか？
  - なぜこの分類ロジックはデータ駆動（例：registry.yaml のタグ）ではないのか？
  - なぜ分類ルールが変更されるたびにコード修正が必要な設計なのか？

- **環境依存のハードコード (Medium)**
  - なぜ n8n の URL (`http://localhost:5678...`) がハードコードされているのか？
  - なぜ `Path.home()` 前提のパス構築 (`oikos/mneme/...`) を行っているのか？
  - なぜ環境変数や設定ファイルによる注入を許容しないのか？

- **スクリプトへの逆依存 (Low)**
  - なぜ `mekhane` (コア実装) が `scripts` (ユーティリティ) に依存しているのか？ (`from scripts.bc_violation_logger import ...`)
  - なぜこのロジックはライブラリ化されていないのか？
  - なぜ循環参照やパス解決の問題を招く依存方向を採用したのか？

- **マジックナンバーの散在 (Low)**
  - なぜ `MODE_REQUIREMENTS` の数値（handoff_count: 10, min_chars: 3000 等）はここに直接書かれているのか？
  - なぜこれらは設定として分離されていないのか？
  - なぜ要件変更のためにコード変更を強いるのか？

## 重大度
Medium
