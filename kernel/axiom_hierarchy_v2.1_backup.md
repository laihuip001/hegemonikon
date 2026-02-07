---
doc_id: "AXIOM_HIERARCHY"
version: "5.0.0"
tier: "KERNEL"
status: "CANONICAL"
created: "2026-01-22"
updated: "2026-01-27"
backup_date: "2026-02-07"
backup_reason: |
  v3.0 実験 (1公理+6座標 再構成) の前にスナップショットとして保存。
  現行の7公理体系が正式版 (axiom_hierarchy.md) として維持されている間、
  このファイルは復元用バックアップとして保持する。
  関連: axiom_hierarchy_v3_experimental.md, .agent/projects/kalon/docs/axiom_v3_single_axiom.md
---

> **Kernel Doc Index**: [SACRED_TRUTH](SACRED_TRUTH.md) | [axiom_hierarchy](axiom_hierarchy.md) ← 📍 | [naming_conventions](naming_conventions.md)

# 📐 公理階層構造 (Axiom Hierarchy) v2.1

> **「予測誤差最小化から導出される認知の全体系」**

---

## 総数

| 項目 | 数 | 生成 |
|------|---|------|
| 公理 | **7** | 1+2+2+2 |
| 定理 | **24** | 6×4 |
| 関係 | **36** | 8+4+4+8+8+4 |
| **総計** | **60** | — |

---

## 公理体系（7軸）

```mermaid
graph TD
    subgraph "公理体系"
        L0["L0: What — FEP"]
        L1["L1: Who/Why — Flow, Value"]
        L15["L1.5: Where-When/How — Scale, Function"]
        L175["L1.75: Which/How much — Valence, Precision"]
        L0 --> L1 --> L15 --> L175
    end
```

| Level | Question | Axiom | Opposition |
|-------|----------|-------|------------|
| L0 | What | FEP | 予測誤差最小化 |
| L1 | Who | Flow | I (推論) ↔ A (行為) |
| L1 | Why | Value | E (認識) ↔ P (実用) |
| L1.5 | Where/When | Scale | Micro ↔ Macro |
| L1.5 | How | Function | Explore ↔ Exploit |
| L1.75 | Which | Valence | + ↔ - |
| L1.75 | How much | Precision | C ↔ U |

---

## 定理群（24 = 6×4）

### Poiēsis: 内容の具現化（生成層12）

| Level | 記号 | 名称 | 生成 | 定理 | ドキュメント |
|-------|------|------|------|------|-------------|
| L0 | O | **Ousia** | L1×L1 | O1-O4 | [ousia.md](ousia.md) |
| L1 | S | **Schema** | L1×L1.5 | S1-S4 | [schema.md](schema.md) |
| L2a | H | **Hormē** | L1×L1.75 | H1-H4 | [horme.md](horme.md) |

### Dokimasia: 条件の詳細化（審査層12）

| Level | 記号 | 名称 | 生成 | 定理 | ドキュメント |
|-------|------|------|------|------|-------------|
| L2b | P | **Perigraphē** | L1.5×L1.5 | P1-P4 | [perigraphe.md](perigraphe.md) |
| L3 | K | **Kairos** | L1.5×L1.75 | K1-K4 | [kairos.md](kairos.md) |
| L4 | A | **Akribeia** | L1.75×L1.75 | A1-A4 | [akribeia.md](akribeia.md) |

---

## 個別定理名（24）

### O-series (Ousia)

| ID | 名称 | 意味 |
|----|------|------|
| O1 | Noēsis | 認識推論 (Recursive Self-Evidencing) |
| O2 | Boulēsis | 意志推論 |
| O3 | Zētēsis | 探索行動 |
| O4 | Energeia | 実用行動 |

### S-series (Schema)

| ID | 名称 | 意味 |
|----|------|------|
| S1 | Metron | スケール流動 |
| S2 | Mekhanē | 方法流動 |
| S3 | Stathmos | スケール価値 |
| S4 | Praxis | 方法価値 |

### H-series (Hormē)

| ID | 名称 | 意味 |
|----|------|------|
| H1 | Propatheia | 流動傾向 |
| H2 | Pistis | 流動確信 |
| H3 | Orexis | 価値傾向 |
| H4 | Doxa | 価値確信 |

### P-series (Perigraphē)

| ID | 名称 | 意味 |
|----|------|------|
| P1 | Khōra | スケール場 |
| P2 | Hodos | スケール方法 |
| P3 | Trokhia | 方法スケール |
| P4 | Tekhnē | 方法場 |

### K-series (Kairos)

| ID | 名称 | 意味 |
|----|------|------|
| K1 | Eukairia | スケール傾向 |
| K2 | Chronos | スケール確信 |
| K3 | Telos | 方法傾向 |
| K4 | Sophia | 方法確信 |

### A-series (Akribeia)

| ID | 名称 | 意味 |
|----|------|------|
| A1 | Pathos | 二重傾向 |
| A2 | Krisis | 傾向確信 |
| A3 | Gnōmē | 確信傾向 |
| A4 | Epistēmē | 二重確信 |

---

## X-series: 関係層（36）

| X | 接続 | 数 | 意味 |
|---|------|---|------|
| X-OS | O→S | 8 | 本質→様態 |
| X-SH | S→H | 4 | 様態→傾向 |
| X-SP | S→P | 4 | 様態→条件 |
| X-PK | P→K | 8 | 条件→文脈 |
| X-KA | K→A | 8 | 文脈→精密 |
| X-HA | H→A | 4 | 傾向→精密 |
| **計** | | **36** | |

詳細: [taxis.md](taxis.md)

---

## 階層構造図

```mermaid
graph TD
    subgraph "Poiēsis: 内容"
        O[O: Ousia] --> S[S: Schema]
        S --> H[H: Hormē]
    end
    
    subgraph "Dokimasia: 条件"
        S --> P[P: Perigraphē]
        P --> K[K: Kairos]
        K --> A[A: Akribeia]
    end
    
    H --> A
```

---

## 参照

- **命名規則**: [naming_conventions.md](naming_conventions.md)
- **不変真理**: [SACRED_TRUTH.md](SACRED_TRUTH.md)

---

*Hegemonikón v2.1 — 60要素体系*
