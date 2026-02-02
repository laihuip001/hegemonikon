# X-Series 完全実装計画

> **目標**: 24/24 定理の関係層を体系的に定義・文書化

---

## 1. 24定理一覧 (1:1 ワークフロー対応)

| Series | 定理1 | 定理2 | 定理3 | 定理4 |
|:-------|:------|:------|:------|:------|
| **O** (Ousia) | O1 Noēsis `/noe` | O2 Boulēsis `/bou` | O3 Zētēsis `/zet` | O4 Energeia `/ene` |
| **S** (Schema) | S1 Metron `/met` | S2 Mekhanē `/mek` | S3 Stathmos `/sta` | S4 Praxis `/pra` |
| **H** (Hormē) | H1 Propatheia `/pro` | H2 Pistis `/pis` | H3 Orexis `/ore` | H4 Doxa `/dox` |
| **P** (Perigraphē) | P1 Khōra `/kho` | P2 Hodos `/hod` | P3 Trokhia `/tro` | P4 Tekhnē `/tek` |
| **K** (Kairos) | K1 Eukairia `/euk` | K2 Chronos `/chr` | K3 Telos `/tel` | K4 Sophia `/sop` |
| **A** (Akribeia) | A1 Pathos `/pat` | A2 Krisis `/dia` | A3 Gnōmē `/gno` | A4 Epistēmē `/epi` |

---

## 2. X-Series 関係タイプ

### 関係の種類

| タイプ | 記号 | 説明 |
|:-------|:-----|:-----|
| **因果** | `→` | A が B を引き起こす |
| **促進** | `⟹` | A が B を強化する |
| **抑制** | `⊣` | A が B を抑制する |
| **循環** | `↺` | A と B が相互に影響 |
| **前提** | `⊃` | A が B の前提条件 |

---

## 3. シリーズ間関係マトリクス（概要）

### X-O: O-series の外部接続

| From | To | 関係 | 説明 | 連結WF |
|:-----|:---|:-----|:-----|:-------|
| O1 Noēsis | S1 Metron | `⊃` | 認識がスケール決定の前提 | `/noe-plan` |
| O1 Noēsis | A2 Krisis | `→` | 認識が検証を誘発 | `/noe-dia` |
| O1 Noēsis | H1 Propatheia | `→` | 認識が初期傾向を形成 | — |
| O2 Boulēsis | K3 Telos | `⊃` | 意志が目的の前提 | — |
| O2 Boulēsis | O4 Energeia | `→` | 意志が行為を誘発 | — |
| O3 Zētēsis | O1 Noēsis | `→` | 調査が認識を深める | `/sop-noe` |
| O3 Zētēsis | A4 Epistēmē | `→` | 調査が知識を確立 | — |
| O4 Energeia | S4 Praxis | `→` | 行為が実践に変換 | — |
| O4 Energeia | A2 Krisis | `→` | 行為が検証を誘発 | — |

### X-S: S-series の外部接続

| From | To | 関係 | 説明 | 連結WF |
|:-----|:---|:-----|:-----|:-------|
| S1 Metron | P1 Khōra | `→` | スケールが条件空間を決定 | — |
| S2 Mekhanē | P4 Tekhnē | `→` | 方法が技法を選択 | — |
| S3 Stathmos | A2 Krisis | `⊃` | 基準が検証の前提 | — |
| S4 Praxis | H4 Doxa | `→` | 実践が信念を形成 | — |

### X-H: H-series の外部接続

| From | To | 関係 | 説明 | 連結WF |
|:-----|:---|:-----|:-----|:-------|
| H1 Propatheia | H2 Pistis | `→` | 初期傾向が確信を形成 | — |
| H2 Pistis | O4 Energeia | `⟹` | 確信が行為を促進 | — |
| H3 Orexis | O2 Boulēsis | `↺` | 欲求と意志が相互影響 | — |
| H4 Doxa | A3 Gnōmē | `→` | 信念が原則を生成 | — |

### X-K: K-series の外部接続

| From | To | 関係 | 説明 | 連結WF |
|:-----|:---|:-----|:-----|:-------|
| K1 Eukairia | O4 Energeia | `⟹` | 好機が行為を促進 | — |
| K2 Chronos | S1 Metron | `→` | 時間がスケールを制約 | — |
| K3 Telos | S3 Stathmos | `→` | 目的が基準を決定 | — |
| K4 Sophia | A4 Epistēmē | `↺` | 知恵と知識が相互強化 | — |

### X-P: P-series の外部接続

| From | To | 関係 | 説明 | 連結WF |
|:-----|:---|:-----|:-----|:-------|
| P1 Khōra | P2 Hodos | `→` | 空間が経路を制約 | — |
| P2 Hodos | P3 Trokhia | `→` | 経路が軌道を決定 | — |
| P3 Trokhia | K2 Chronos | `→` | 軌道が時間を消費 | — |
| P4 Tekhnē | S2 Mekhanē | `↺` | 技法と方法が相互選択 | — |

### X-A: A-series の外部接続

| From | To | 関係 | 説明 | 連結WF |
|:-----|:---|:-----|:-----|:-------|
| A1 Pathos | H1 Propatheia | `→` | 情念が初期傾向を誘発 | — |
| A2 Krisis | A4 Epistēmē | `→` | 検証が知識を確立 | — |
| A3 Gnōmē | S3 Stathmos | `→` | 原則が基準を形成 | — |
| A4 Epistēmē | H4 Doxa | `→` | 知識が信念を強化 | — |

---

## 4. 実装方針

### 選択肢

| 案 | 内容 | 工数 | 価値 |
|:---|:-----|:-----|:-----|
| **A** | 関係定義のみ（/x.md 更新） | 小 | 中 |
| **B** | 関係定義 + Mermaid 図 | 中 | 高 |
| **C** | 関係定義 + 連結WF 全展開 | 大 | 高 |

### 推奨: 段階的実装

1. **Phase 1**: /x.md に完全な関係マトリクスを追加（案B）
2. **Phase 2**: 高頻度の連結 WF を追加
3. **Phase 3**: Skill レベルで関係を利用

---

## 5. 変更対象

| ファイル | 変更 |
|:---------|:-----|
| `/x.md` | 関係マトリクス追加 |
| `/x.md` | Mermaid 図拡張 |

---

## 承認待ち

⏸️ **どの案で進めますか？** (A/B/C)
