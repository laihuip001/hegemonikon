# Hegemonikón

> **認知エージェントフレームワーク** — 変分自由エネルギー最小化原理に基づく AI 認知制御システム

---

## 理論的基盤: 自由エネルギー原理 (FEP)

Hegemonikón（ヘゲモニコン）は、ストア派哲学における「統率中枢」の概念と、現代の**自由エネルギー原理**（Free Energy Principle）を融合した AI 認知アーキテクチャです。

> **核心原理**: 知覚・認知・行動・学習は全て**変分自由エネルギー最小化**という同一原理の異なる側面である。

### FEP の AI への適用

| 概念 | 人間の脳 | Hegemonikón |
|------|----------|-------------|
| **知覚** | 感覚器官 | M1 Aisthēsis |
| **予測** | 内部モデル | M3 Theōria |
| **行動** | 運動制御 | M6 Praxis |
| **記憶** | 海馬 | M8 Anamnēsis |

---

## 公理階層構造

```
Level 0: FEP統一原理 (メタ公理) ← 1
    │
    ▼
Level 1: 核心公理 ← 2
    │   ├── Flow (推論 ↔ 行為)
    │   └── Value (情報 ↔ 目標)
    │
    ├─────────────────────────────────┐
    ▼                                 ▼
Level 2a: P-series (4)          Level 1.5: 選択公理 (4)
    │   核心 × 核心                   Tempo, Stratum
    │                                 Agency, Valence
    │                                     │
    │            ┌────────────────────────┴────────┐
    │            ▼                                 ▼
    │    Level 2b: M-series (8)         Level 2c: Kairos (12)
    │        核心 × 選択                    選択 × 選択
    │                                      (文脈定理)
    └────────────────────────────────────────────────┘
                        │
                基本機能: 12 + 文脈: 12 = 24
```

### 数学的構造

| シリーズ | 数式 | 数 | 性質 |
|---------|------|-----|------|
| **P-series** | 2 × 2 | 4 | 本質的 (何であるか) |
| **M-series** | 2 × 4 | 8 | 様態的 (どう在るか) |
| **K-series** | 4 × 3 | 12 | 文脈的 (どの状況で) |

> **美しさ**: 4 → 8 → 12 の等差数列 (+4)

---

## P-Series 純粋定理

> 核心公理 × 核心公理 = 4 純粋定理

| Module | 軸 | 機能 |
|--------|-----|------|
| **P1** | I × E | 情報推論 (Epistemic Inference) |
| **P2** | I × P | 目標推論 (Pragmatic Inference) |
| **P3** | A × E | 情報行為 (Epistemic Action) |
| **P4** | A × P | 目標行為 (Pragmatic Action) |

---

## M-Series 認知モジュール

> 核心公理 × 選択公理 = 8 拡張定理

| Module | ギリシャ語 | 機能 |
|--------|------------|------|
| **M1** | Aisthēsis | 知覚・文脈認識 |
| **M2** | Krisis | 判断・優先順位決定 |
| **M3** | Theōria | 理論構築・因果モデル |
| **M4** | Phronēsis | 実践知・戦略策定 |
| **M5** | Peira | 探求・情報収集 |
| **M6** | Praxis | 行為・実行 |
| **M7** | Dokimē | 検証・テスト |
| **M8** | Anamnēsis | 記憶・長期保存 |

---

## K-Series 文脈定理

> 選択公理 × 選択公理 = 12 文脈修飾子

| 第1軸 | 組み合わせ |
|-------|------------|
| **Tempo ×** | Stratum, Agency, Valence (3) |
| **Stratum ×** | Tempo, Agency, Valence (3) |
| **Agency ×** | Tempo, Stratum, Valence (3) |
| **Valence ×** | Tempo, Stratum, Agency (3) |

詳細: [kernel/axiom_hierarchy.md](kernel/axiom_hierarchy.md)

---

## 二重実装体系

> **M-series は2つのスケールで具現化する**

| レベル | 実装 | 役割 |
|--------|------|------|
| **ミクロ** | skills/, workflows/ | AI主体の行動 |
| **マクロ** | mēkhanē/ | システム基盤 |

---

## ディレクトリ構造

```
Hegemonikon/
├── kernel/               # 公理層 (IMMUTABLE)
│   ├── axiom_hierarchy.md
│   ├── SACRED_TRUTH.md
│   └── constitution/     # ルール群
├── skills/               # ミクロ実装 (AI行動)
├── mekhane/              # マクロ実装 (機構層)
│   ├── peira/            # M5: 収集
│   ├── ergasterion/      # M6: 製造
│   ├── anamnesis/        # M8: 記憶 (gnosis)
│   └── exagoge/          # M6: 出力
└── docs/                 # ドキュメント
```


---

## AI エージェント向けドキュメント

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | **Start Here** — ルールと境界 |
| [kernel/axiom_hierarchy.md](kernel/axiom_hierarchy.md) | 公理階層の正規定義 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 技術詳細 (English) |

---

## 設計哲学

> **「真理は美しく、美しさは真理に近づく道標である」**

| 原則 | 意味 |
|------|------|
| **Form Follows Logic** | 構造が論理を反映する |
| **Logic Follows Beauty** | 論理が美しさを生む |
| **Zero Entropy** | 曖昧さの排除 = 構造の純粋化 |

---

## ライセンス

MIT License

---

*Hegemonikón — 変分自由エネルギー最小化による認知制御*
