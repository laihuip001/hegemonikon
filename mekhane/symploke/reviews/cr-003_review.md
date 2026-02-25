# ソクラテス式問答者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **n8n Webhook URLのハードコード (Medium)**
  - `http://localhost:5678/webhook/session-start` が直接記述されている。
  - なぜ構成ファイルや環境変数から読み込まないのか？
  - なぜポートは `5678` なのか？
- **`scripts` モジュールへの依存 (Medium)**
  - `from scripts.bc_violation_logger import ...` している。
  - `mekhane` (L2) が `scripts` (Utility) に依存するのはなぜか？ (依存方向の逆転)
- **プロジェクト分類のハードコード (Medium)**
  - `_load_projects` 内で `kalon`, `aristos`, `ccl` などのIDを直接条件分岐に使用している。
  - なぜこれらの分類ロジックをデータ (`registry.yaml`) 側に持たせないのか？
  - プロジェクトが増えるたびにこのコードを修正するつもりなのか？
- **マジックナンバーの使用 (Medium)**
  - `MODE_REQUIREMENTS` 内の `min_chars: 3000`, `handoff_count: 10` など。
  - なぜ 3000 文字なのか？ なぜ 10 件なのか？ 根拠が説明されていない。
  - `timeout=5` (n8n接続) の根拠は？
- **ハードコードされたパス (Medium)**
  - `Path.home() / "oikos" / ...`
  - なぜユーザーのホームディレクトリ下に `oikos` があると仮定しているのか？
  - `/tmp/boot_report_...`
  - なぜシステムの一時ディレクトリ (`tempfile` モジュール) を使わず `/tmp` を指定しているのか？
  - `sys.path.insert(0, ...)`
  - なぜ `sys.path` を直接操作しているのか？ パッケージ構造を正しく解決しないのか？

## 重大度
Medium
