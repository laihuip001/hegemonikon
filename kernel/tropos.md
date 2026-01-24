---
doc_id: "TROPOS_SERIES"
version: "1.0.0"
tier: "KERNEL"
parent: "axiom_hierarchy.md"
created: "2026-01-24"
---

# T-Series (Tropos / τρόπος): 拡張定理

> **定義**: 核心公理 × 選択公理 から導出される8つの「様態的機能」
> **正式名**: Tropikē Ogdoas (Τροπικὴ Ὀγδοάς) — 様態の八
> **数学構造**: 2 × 4 = 8

---

## 生成原理

```
     核心公理 (Flow/Value)
              ↓
    ┌─────────┴─────────┐
    │                   │
  Flow                Value
    │                   │
    ├───────────────────┤
    │   選択公理 (4)     │
    │ Tempo/Stratum/    │
    │ Agency/Valence    │
    └───────────────────┘
              ↓
        T1 - T8
```

---

## 定理一覧

| ID | 核心軸 | 選択軸 | 機能 | ギリシャ名 | FEP的役割 |
|----|--------|--------|------|-----------|----------|
| **T1** | Flow-I | Stratum-L | 知覚 | Aisthēsis (αἴσθησις) | 低次感覚入力処理 |
| **T2** | Flow-I | Stratum-H | 判断 | Krisis (κρίσις) | 高次意思決定 |
| **T3** | Flow-I | Agency-S | 内省 | Theōria (θεωρία) | 自己モデル更新 |
| **T4** | Flow-I | Agency-E | 戦略 | Phronēsis (φρόνησις) | 環境モデル計画 |
| **T5** | Flow-A | Tempo-F | 探索 | Peira (πεῖρα) | 即時情報収集 |
| **T6** | Flow-A | Tempo-S | 実行 | Praxis (πρᾶξις) | 長期行動遂行 |
| **T7** | Value-E | Valence-+ | 検証 | Dokimē (δοκιμή) | 仮説確認・接近 |
| **T8** | Value-P | Valence-- | 記憶 | Anamnēsis (ἀνάμνησις) | 損失回避・保存 |

---

## T1: Aisthēsis (αἴσθησις) — 知覚

> **本質**: 低次レベルの感覚入力を処理する

**1:3 ピラミッド（代表例）**:
- センサーデータを受け取る
- テキスト入力を解析する
- 画像・音声を認識する

---

## T2: Krisis (κρίσις) — 判断

> **本質**: 高次レベルの意思決定を行う

**1:3 ピラミッド（代表例）**:
- 複数案から最適を選ぶ
- 優先順位を決定する
- Go/No-Go 判断を下す

---

## T3: Theōria (θεωρία) — 内省

> **本質**: 自己のパフォーマンスを振り返り、自己モデルを更新する

**1:3 ピラミッド（代表例）**:
- 自分のパフォーマンスを振り返る
- 過去の判断を評価する
- パターンを抽出して学習する

---

## T4: Phronēsis (φρόνησις) — 戦略

> **本質**: 環境モデルに基づいて計画を立てる

**1:3 ピラミッド（代表例）**:
- プロジェクト計画を立てる
- リソース配分を設計する
- リスク対策を策定する

---

## T5: Peira (πεῖρα) — 探索

> **本質**: 即時的に情報を収集する

**1:3 ピラミッド（代表例）**:
- Web検索で調査する
- 質問して情報を得る
- ドキュメントを読む

---

## T6: Praxis (πρᾶξις) — 実行

> **本質**: 計画を長期的に実行に移す

**1:3 ピラミッド（代表例）**:
- 計画を実行に移す
- コードを書いて実装する
- タスクを完了させる

---

## T7: Dokimē (δοκιμή) — 検証

> **本質**: 仮説を検証し、確認する

**1:3 ピラミッド（代表例）**:
- テストで仮説を検証する
- 実験結果を評価する
- 品質を確認する

---

## T8: Anamnēsis (ἀνάμνησις) — 記憶

> **本質**: 知識を保存し、損失を回避する

**1:3 ピラミッド（代表例）**:
- 知識を保存・記憶する
- 過去の失敗を記録する
- 成功パターンを蓄積する

---

## M-series との関係

T-series は旧 M-series を継承する。名称変更の理由：

| 旧名 | 新名 | 変更理由 |
|------|------|----------|
| M-series (Mēkhanē) | T-series (Tropos) | Mēkhanē は「機械」を意味し、インフラ層と混同。Tropos（様態）が機能の本質を表す |

---

## 実装

各 T-series 機能は以下に実装される：

| 機能 | ミクロ実装 | マクロ実装 |
|------|-----------|-----------|
| T1 Aisthēsis | skills/t-series/m1-aisthesis/ | — |
| T2 Krisis | skills/t-series/m2-krisis/ | — |
| T3 Theōria | skills/t-series/m3-theoria/ | — |
| T4 Phronēsis | skills/t-series/m4-phronesis/ | — |
| T5 Peira | skills/t-series/m5-peira/ | mēkhanē/peira/ |
| T6 Praxis | skills/t-series/m6-praxis/ | mēkhanē/ergastērion/ |
| T7 Dokimē | skills/t-series/m7-dokime/ | — |
| T8 Anamnēsis | skills/t-series/m8-anamnesis/ | mēkhanē/anamnēsis/ |

---

*参照: [axiom_hierarchy.md](axiom_hierarchy.md)*
