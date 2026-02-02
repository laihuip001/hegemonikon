# M-Series 再編計画

## 目的

1. **FEPメタデータ追加**: 既存M-seriesにHegemonikón 4軸を付与
2. **ギャップ分析**: Hegemonikón 16機能で未カバーの要素を特定
3. **新モジュール提案**: 必要な追加M-seriesを提案
4. **番号再編**: 飛び番を解消し、連番化

---

## Part 1: 現行M-series × FEP軸マッピング

### FEP 4軸の定義

| 軸 | コード | 意味 |
|---|---|---|
| **Flow** | I / A | 推論 (Inference) vs 行為 (Action) |
| **Value** | E / P | 認識的 (Epistemic) vs 実践的 (Pragmatic) |
| **Tempo** | F / S | 短期 (Fast) vs 長期 (Slow) |
| **Stratum** | L / H | 低次 (Low) vs 高次 (High) |

### 現行M-seriesのFEPマッピング

| 現番号 | 名称 | Hegemonikón対応 | FEP Code | 役割 |
|--------|------|-----------------|----------|------|
| **M1** | Input Gate | 09 Aisthēsis-H + 10 Krisis-H | **I-E/P-F-H** | 入力解析・リスク評価 |
| **M6** | Context Nexus | 09 Aisthēsis-H | **I-E-F-H** | 文脈維持・漂流検知 |
| **M7** | Adversarial Council | 13 Theōria-H + 15 Dokimē-H | **I-E-S-H** | 多角的批評・検証 |
| **M9** | Protocol Loader | 06 Phronēsis-L | **I-P-S-L** | 動的知識注入 |

---

## Part 2: ギャップ分析

### Hegemonikón 16機能 カバレッジ

| ID | 機能 | FEP Code | 現行カバー | ギャップ |
|----|------|----------|------------|----------|
| 01 | Aisthēsis-L (感覚知覚) | I-E-F-L | Antigravity組込 | — |
| 02 | Krisis-L (運動判断) | I-P-F-L | Antigravity組込 | — |
| 03 | Peira-L (探索運動) | A-E-F-L | Antigravity組込 | — |
| 04 | Praxis-L (反射実行) | A-P-F-L | Antigravity組込 | — |
| 05 | Theōria-L (感覚学習) | I-E-S-L | — | ⚠️ 低優先 |
| 06 | Phronēsis-L (運動計画) | I-P-S-L | **M9** | ✅ |
| 07 | Dokimē-L (感覚実験) | A-E-S-L | — | ⚠️ 低優先 |
| 08 | Anamnēsis-L (運動記憶) | A-P-S-L | — | **🔴 要追加** |
| 09 | Aisthēsis-H (文脈認識) | I-E-F-H | **M1, M6** | ✅ |
| 10 | Krisis-H (目標評価) | I-P-F-H | **M1 (部分)** | ⚠️ 強化要 |
| 11 | Peira-H (能動質問) | A-E-F-H | — | **🔴 要追加** |
| 12 | Praxis-H (意思決定) | A-P-F-H | — | **🔴 要追加** |
| 13 | Theōria-H (世界観構築) | I-E-S-H | **M7 (部分)** | ✅ |
| 14 | Phronēsis-H (人生設計) | I-P-S-H | — | **🔴 要追加** |
| 15 | Dokimē-H (検証設計) | A-E-S-H | **M7 (部分)** | ✅ |
| 16 | Anamnēsis-H (価値更新) | A-P-S-H | — | **🔴 要追加** |

### 🔴 致命的ギャップ (要追加)

| 機能 | 欠損による影響 |
|------|---------------|
| **Peira-H (能動質問)** | 不確実性検出時に情報収集を能動的に発動できない |
| **Praxis-H (意思決定)** | 評価結果を行動に変換する判断機構がない |
| **Anamnēsis-L (運動記憶)** | 操作履歴の保存・学習ができない |
| **Phronēsis-H (人生設計)** | 長期目標に基づく戦略設計ができない |
| **Anamnēsis-H (価値更新)** | 経験からの価値観更新・メタ学習ができない |

---

## Part 3: 新M-series提案

### 提案: 8モジュール体制

| 新番号 | 名称 | 旧番号 | Hegemonikón対応 | 状態 |
|--------|------|--------|-----------------|------|
| **M1** | Input Gate | M1 | 09 + 10 | 維持 |
| **M2** | Context Nexus | M6 | 09 | リナンバー |
| **M3** | Adversarial Council | M7 | 13 + 15 | リナンバー |
| **M4** | Protocol Loader | M9 | 06 | リナンバー |
| **M5** | Active Inquiry | **新規** | 11 Peira-H | **新規** |
| **M6** | Decision Engine | **新規** | 12 Praxis-H | **新規** |
| **M7** | Memory System | **新規** | 08 + 16 Anamnēsis | **新規** |
| **M8** | Strategic Planner | **新規** | 14 Phronēsis-H | **新規** |

### 新モジュール詳細

#### M5: Active Inquiry (能動質問)

| 項目 | 内容 |
|------|------|
| **Hegemonikón** | 11 Peira-H (A-E-F-H) |
| **役割** | 不確実性を検出し、情報収集行動を自律的に発動 |
| **トリガー** | uncertainty_score > 0.6、明示的「調べて」 |
| **出力** | 検索クエリ、収集結果、統合情報 |
| **ツール** | Perplexity Sonar/Research、Web検索 |

#### M6: Decision Engine (意思決定)

| 項目 | 内容 |
|------|------|
| **Hegemonikón** | 12 Praxis-H (A-P-F-H) |
| **役割** | 評価結果に基づき行動タイプを決定 (execute/propose/defer/skip) |
| **トリガー** | Krisis出力受信、緊急フラグ |
| **出力** | 実行決定、ユーザー提案、実行ログ |
| **ツール** | Antigravity (実行発動) |

#### M7: Memory System (記憶・学習)

| 項目 | 内容 |
|------|------|
| **Hegemonikón** | 08 Anamnēsis-L + 16 Anamnēsis-H |
| **役割** | 操作履歴保存、パターン学習、価値更新 |
| **トリガー** | セッション終了、定期バッチ |
| **出力** | Vault保存、最適化提案、価値関数更新 |
| **ツール** | Obsidian Vault、GitHub |

#### M8: Strategic Planner (人生設計)

| 項目 | 内容 |
|------|------|
| **Hegemonikón** | 14 Phronēsis-H (I-P-S-H) |
| **役割** | 長期目標に基づく戦略設計・方策評価 |
| **トリガー** | 目標設定、環境大変化、定期レビュー |
| **出力** | 戦略、方策集合、ロードマップ |
| **ツール** | Claude Opus (深い推論) |

---

## Part 4: 実装ロードマップ

### フェーズ 1: メタデータ追加 + リナンバー

| タスク | 対象 | 変更内容 |
|--------|------|----------|
| 1.1 | M1 SKILL.md | FEPメタデータ追加 |
| 1.2 | M6 → M2 | ディレクトリ名変更 + FEPメタデータ |
| 1.3 | M7 → M3 | ディレクトリ名変更 + FEPメタデータ |
| 1.4 | M9 → M4 | ディレクトリ名変更 + FEPメタデータ |

### フェーズ 2: 新モジュール作成

| タスク | 対象 | 内容 |
|--------|------|------|
| 2.1 | M5 Active Inquiry | SKILL.md 新規作成 |
| 2.2 | M6 Decision Engine | SKILL.md 新規作成 |
| 2.3 | M7 Memory System | SKILL.md 新規作成 |
| 2.4 | M8 Strategic Planner | SKILL.md 新規作成 |

---

## 決定事項（ユーザー承認待ち）

1. **8モジュール体制** を採用するか？
2. **リナンバー** (M6→M2, M7→M3, M9→M4) を実施するか？
3. **新モジュール4つ** を全て作成するか、優先順位をつけるか？
