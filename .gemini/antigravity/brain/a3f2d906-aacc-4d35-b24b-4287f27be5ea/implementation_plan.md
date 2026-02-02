# 王道リスト消化計画 — ライブラリ構造版

> **構造**: 組み込み → 標準ライブラリ → ユーザーライブラリ

---

## Tier 0: 組み込み (Built-in) — 24定理

**変更なし。王道は定理の増強として消化。**

| Hub | 定理 | CCL |
|:----|:-----|:----|
| O | Noēsis, Boulēsis, Zētēsis, Energeia | `/noe` `/bou` `/zet` `/ene` |
| S | Metron, Mekhanē, Stathmos, Praxis | `/met` `/mek` `/sta` `/pra` |
| A | Pathos, Krisis, Gnōmē, Epistēmē | `/pat` `/dia` `/gno` `/epi` |
| H | Propatheia, Pistis, Orexis, Doxa | `/pro` `/pis` `/ore` `/dox` |
| P | Khōra, Hodos, Trokhia, Tekhnē | `/kho` `/hod` `/tro` `/tek` |
| K | Eukairia, Chronos, Telos, Sophia | `/euk` `/chr` `/tel` `/sop` |

---

## Tier 1: 標準ライブラリ (Standard Library)

**普遍度: 高 — 全ての認知活動で有用**

### モード派生 (定理の増強)

| 王道 | 定理 | モード | 説明 |
|:-----|:-----|:-------|:-----|
| ベイズ推論 | H2 | `/pis.bayes` | FEPの核心 |
| フェルミ推定 | S1 | `/met.fermi` | 概算 |
| アナロジー | A3 | `/gno.analogy` | 写像 |
| 背理法 | A2 | `/dia.reductio` | 矛盾証明 |
| アブダクション | O3 | `/zet.abduction` | 最良説明 |
| パレート | S3 | `/sta.pareto` | 80/20 |
| JTBD | H3 | `/ore.jtbd` | 欲求分析 |
| TOC | X | `/x.toc` | 制約理論 |

### マクロ (定理の組み合わせ)

| 王道 | マクロ | CCL | 構成 |
|:-----|:-------|:----|:-----|
| MECE | `@mece` | `/kho_/sta` | 場+基準 |
| OODA | `@ooda` | `/noe_/bou_/dia_/ene` | 4定理 |
| PDCA | `@pdca` | `/tro~` | サイクル |
| 5 Whys | `@5why` | `F:5{/zet}` | 繰返し探求 |
| デザイン思考 | `@design` | `/ore_/zet_/ene~` | 欲求→行為 |

### 既存WF (復活/更新)

| 王道 | WF | 状態 |
|:-----|:---|:-----|
| Five Whys | `/why` | deprecated → 復活 |
| Premortem | `/pre` | active |
| PoC/Spike | `/poc` | active |

---

## Tier 2: ユーザーライブラリ (User Library)

**普遍度: 中〜低 — 専門的状況で有用**

### 業界特化

| 王道 | 形式 | CCL/モード |
|:-----|:-----|:-----------|
| TRIZ | マクロ | `@triz` |
| DMAIC | マクロ | `@dmaic` |
| カノモデル | マクロ | `@kano` |
| A3思考 | モード | `/kho.a3` |

### 方法論特化

| 王道 | 形式 | CCL/モード |
|:-----|:-----|:-----------|
| シネクティクス | マクロ | `@synectics` |
| モーフォロジカル | マクロ | `@morpho` |
| SCAMPER | マクロ | `@scamper` |

---

## 集計

| Tier | 件数 | 説明 |
|:-----|:-----|:-----|
| 0: 組み込み | 24 | 定理 (変更なし) |
| 1: 標準 | ~30 | 高普遍度 |
| 2: ユーザー | ~100 | 中〜低普遍度 |

---

## 次のアクション

1. Tier 1 (標準) を優先実装
2. Tier 2 は必要に応じて追加
3. `/why` を deprecated から復活

---

*v3.0 — ライブラリ構造版 (2026-01-30)*
