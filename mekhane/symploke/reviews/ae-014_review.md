# 比喩一貫性の詩人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- ドメイン用語の不統一 (High): `THEOREM_REGISTRY` 内の定理名が `AGENTS.md` (v5.0) の定義と乖離している。
    - S1: Metron (Code) vs Hermēneia (Docs)
    - S3: Stathmos (Code) vs Chronos (Docs)
    - K1: Eukairia (Code) vs Taksis (Docs)
    - K2: Chronos (Code) vs Sophia (Docs)
    - K3: Telos (Code) vs Anamnēsis (Docs)
    - K4: Sophia (Code) vs Epistēmē (Docs)
    - A1: Pathos (Code) vs Hexis (Docs)
    - A3: Gnōmē (Code) vs Epimeleia (Docs)
    これは「一つのドメインには一つの比喩世界」という原則以前に、ドメインそのものの定義が揺らいでいる状態である。
- 比喩の混在 (Medium): 異なるドメインの比喩が無秩序に混在している。
    - "Intent-WAL": 認知 (Intent) と データベース実装詳細 (Write-Ahead Log) の混同
    - "Attractor Dispatcher": 力学系 (Attractor) と 物流/計算機 (Dispatcher) の混同
    - "Digestor" vs "Incoming": 生物学的消化 (Digestor) と 事務的受信箱 (Incoming) の混同
- 役割メタファーの不徹底 (Low): `generate_boot_template` (Factory的振る舞い) や `_load_projects` (Loader) など、機能的な命名と概念的な命名が混在し、統一された世界観（例：認知的覚醒プロセス）を構築できていない。

## 重大度
High
