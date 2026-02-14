---
doc_id: "SYSTEM_MANIFEST"
version: "1.0.0"
tier: "KERNEL"
status: "CANONICAL"
lineage: "axiom_hierarchy v3.1 + 6 Series files + 存在証明カバレッジ調査 (2026-02-13)"
---

# System Manifest — 96要素体系一覧

> **唯一の公理**: FEP (予測誤差最小化)
> **体系核**: 103 (素数) = 1 + 6 + 24 + 72
> **関係総計**: 108 = 36 (Series内) + 72 (Series間)

---

## 公理 (1)

| ID | 名称 | 定義箇所 | 存在証明 |
|:---|:-----|:---------|:---------|
| A0 | FEP (Free Energy Principle) | [axiom_hierarchy.md](axiom_hierarchy.md) L84 | FEP 自体が公理 — 証明不要 |

---

## 座標 (6) — 定理¹

| d | Question | 座標 | Opposition | 定義箇所 |
|:-:|:---------|:-----|:-----------|:---------|
| 0 | Who | **Flow** | I (推論) ↔ A (行為) | [axiom_hierarchy.md](axiom_hierarchy.md) L109 |
| 1 | Why | **Value** | E (認識) ↔ P (実用) | L110 |
| 1 | How | **Function** | Explore ↔ Exploit | L111 |
| 2 | Where/When | **Scale** | Micro ↔ Macro | L112 |
| 2 | Which | **Valence** | + ↔ - | L113 |
| 2 | How much | **Precision** | C ↔ U | L114 |

---

## 定理² (24 = 6×4) — Series 別

### O-series: Ousia (本質) — L0

> 生成: Flow × {Value, Function} = L1 × L1|L1.5

| ID | 名称 | 生成 | kernel/ | SKILL.md | WF |
|:---|:-----|:-----|:--------|:---------|:---|
| O1 | Noēsis (認識) | I × E | [ousia.md](ousia.md) L58 | ✅ | `/noe` |
| O2 | Boulēsis (意志) | I × P | L69 | ✅ | `/bou` |
| O3 | Zētēsis (探求) | A × E | L77 | ✅ | `/zet` |
| O4 | Energeia (活動) | A × P | L85 | ✅ | `/ene` |

### S-series: Schema (様態) — L1

> 生成: Flow × {Scale, Function} = L1 × L1.5|L2

| ID | 名称 | 生成 | kernel/ | SKILL.md | WF |
|:---|:-----|:-----|:--------|:---------|:---|
| S1 | Metron (尺度) | Flow × Scale | [schema.md](schema.md) L57 | ✅ | — |
| S2 | Mekhanē (機構) | Flow × Function | L65 | ✅ | `/mek` |
| S3 | Stathmos (基点) | Value × Scale | L73 | ✅ | — |
| S4 | Praxis (実践) | Value × Function | L81 | ✅ | `/pra` |

### H-series: Hormē (傾向) — L2a

> 生成: Flow × {Valence, Precision} = L1 × L1.75

| ID | 名称 | 生成 | kernel/ | SKILL.md | WF |
|:---|:-----|:-----|:--------|:---------|:---|
| H1 | Propatheia (前感情) | Flow × Valence | [horme.md](horme.md) L57 | ✅ | `/pro` |
| H2 | Pistis (確信) | Flow × Precision | L66 | ✅ | `/pis` |
| H3 | Orexis (欲求) | Value × Valence | L74 | ✅ | `/ore` |
| H4 | Doxa (見解) | Value × Precision | L82 | ✅ | `/dox` |

### P-series: Perigraphē (条件) — L2b

> 生成: Scale × {Scale, Function} = L1.5 × L1.5|L2

| ID | 名称 | 生成 | kernel/ | SKILL.md | WF |
|:---|:-----|:-----|:--------|:---------|:---|
| P1 | Khōra (空間) | Scale × Scale | [perigraphe.md](perigraphe.md) L57 | ✅ | — |
| P2 | Hodos (経路) | Scale × Function | L68 | ✅ | — |
| P3 | Trokhia (軌跡) | Function × Scale | L77 | ✅ | — |
| P4 | Tekhnē (技術) | Function × Function | L85 | ✅ | — |

### K-series: Kairos (文脈) — L3

> 生成: Scale × {Valence, Precision} = L1.5 × L1.75

| ID | 名称 | 生成 | kernel/ | SKILL.md | WF |
|:---|:-----|:-----|:--------|:---------|:---|
| K1 | Eukairia (好機) | Scale × Valence | [kairos.md](kairos.md) L57 | ✅ | — |
| K2 | Chronos (時間) | Scale × Precision | L65 | ✅ | — |
| K3 | Telos (目的) | Function × Valence | L73 | ✅ | — |
| K4 | Sophia (知恵) | Function × Precision | L81 | ✅ | `/sop` |

### A-series: Akribeia (精密) — L4

> 生成: Valence × {Valence, Precision} = L1.75 × L1.75

| ID | 名称 | 生成 | kernel/ | SKILL.md | WF |
|:---|:-----|:-----|:--------|:---------|:---|
| A1 | Pathos (情動) | Valence × Valence | [akribeia.md](akribeia.md) L57 | ✅ | — |
| A2 | Krisis (判断) | Valence × Precision | L65 | ✅ | `/dia` |
| A3 | Gnōmē (見識) | Precision × Valence | L73 | ✅ | — |
| A4 | Epistēmē (知識) | Precision × Precision | L81 | ✅ | `/epi` |

---

## X-series 関係 (72 = 9グループ × 8)

| X | 接続 | 共有座標 | 数 | 定義箇所 |
|:--|:-----|:---------|---:|:---------|
| X-OS | O→S | Flow | 8 | [axiom_hierarchy.md](axiom_hierarchy.md) L242 |
| X-OH | O→H | Flow | 8 | L243 |
| X-SH | S→H | Flow | 8 | L244 |
| X-SP | S→P | Scale | 8 | L245 |
| X-SK | S→K | Scale | 8 | L246 |
| X-PK | P→K | Scale | 8 | L247 |
| X-HA | H→A | Valence | 8 | L248 |
| X-HK | H→K | Valence | 8 | L249 |
| X-KA | K→A | Valence | 8 | L250 |

---

## Series 内関係 (36 = 3型 × 12)

| 型 | 圏論構造 | 意味 | 数 |
|:--|:---------|:-----|---:|
| **D** (随伴) | T1⊣T3, T2⊣T4 | 忘却と構成 | 12 |
| **H** (自然変換) | T1↔T2, T3↔T4 | 目的切替 | 12 |
| **X** (双対) | T1↔T4, T2↔T3 | 対極の対話 | 12 |

---

## カバレッジ総括

| 層 | 要素数 | 定義 | 証明 | 実装 |
|:---|------:|:----:|:----:|:----:|
| 公理 | 1 | ✅ | — | ✅ FEP Agent |
| 座標 | 6 | ✅ | ✅ | ✅ 座標系 |
| 定理² | 24 | ✅ | ✅ | ✅ 24 SKILL.md |
| 関係 (Series間) | 72 | ✅ | ✅ | ✅ x-series.json |
| 関係 (Series内) | 36 | ✅ | ✅ | — |
| **合計** | **139** | **✅** | **✅** | **部分的** |

> Series内36関係の実装 (WF レベル) は未完。圏論的構造としての定義は済み。

---

*Generated: 2026-02-13 — 存在証明カバレッジ監査*
