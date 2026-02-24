# 比喩一貫性の詩人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- **ドメイン用語の不統一 (High)**: `THEOREM_REGISTRY` が旧体系（Metron, Stathmos, Hodos, Trokhia, Tekhnē, Pathos, Gnōmē）を使用しており、AGENTS.md v5.0 の正典（Hermēneia, Chronos, Telos, Eukairia, Stasis, Hexis, Epimeleia）と著しく乖離している。また `SERIES_INFO` において K (Kairos) が「時間」と定義されているが、正しくは「文脈」である（時間は Chronos/Perigraphē の領域）。
- **比喩の混在 (Low)**: "Intent-WAL"（データベース/ログ）、"Attractor"（力学系）、"Digestor"（生物学）、"Incoming"（事務）と、異なる体系の比喩が無秩序に混在している。特に「Digestor（消化器官）」が「Incoming（受信トレイ）」フォルダを処理する構造は、生物学的比喩と事務的メタファーの不協和音を生んでいる。
- **実装パターンの比喩不統一 (Low)**: `_load_projects` (Loader), `generate_boot_template` (Generator), `AttractorDispatcher` (Dispatcher), `IntentWALManager` (Manager) と、機能的な命名において統一された世界観（例：すべてを「生成」と捉える、あるいは「選別」と捉える等）が欠如し、一般的なソフトウェアパターンが散在している。
- **メタファーの中途半端な適用 (Low)**: `todays_theorem` は単なる変数名であり、`TheoremAttractor` のような荘厳な比喩世界と比較して弱く、文法的にも不正確（本来は `todays_theorem` ではなく `theorem_of_the_day` や `daily_theorem` が適切、あるいは `DailyOracle` 等の比喩が望ましい）。

## 重大度
High
