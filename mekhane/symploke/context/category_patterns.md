# Category Theory Patterns — Jules 向け圏論パターンガイド

## PURPOSE

Jules/Gemini が HGK プロジェクトのコードをレビューする際に、
圏論的概念がどう実装に反映されているかを理解するためのガイド。

## Core Patterns

### 随伴対 (Adjunction: L ⊣ R)

**定義**: 互いに「最良の近似」を提供する関手のペア。
HGK では Boot (L) と Bye (R) が随伴対を形成する。

| 実装パターン | 圏論 | コードでの現れ方 |
|:------------|:-----|:----------------|
| Boot → Bye | L ⊣ R | `boot.md` / `bye.md` が対になる設計 |
| Save → Load | R → L | `/rom` (Save) と Phase 3 ROM読込 (Load) |
| Explore → Exploit | EFE | `attractor_advisor.py` の Function 座標 |
| Inference → Action | FEP | `fep_field.py` の I↔A 軸 |

### 自然変換 (Natural Transformation)

**定義**: 関手間の構造を保つ変換。

| パターン | 意味 | コード |
|:---------|:-----|:-------|
| H-関係 | 目的切替 (T1↔T2, T3↔T4) | WF 間の切替: `/noe` ↔ `/bou` |
| η: Id → R∘L | Boot の単位 | Handoff → Boot → 新セッション |
| ε: L∘R → Id | Boot の余単位 | Boot 後の Drift 測定 |

### Trigonon (三角関係)

**定義**: 3つの Series 間の三角形で、
Bridge (遠い Series への接続) と Anchor (近い Series への定着) がある。

| 構成要素 | 意味 | 使い方 |
|:---------|:-----|:-------|
| Bridge | 結果を隣接領域に接続 | `/noe` 完了 → `/s` に戦略化 |
| Anchor | 結果を深く定着 | `/noe` 完了 → `/pis` で確信度測定 |

## Series 間関係 (X-series)

HGK の 6 Series は共有座標で接続される:

| 接続 | 共有座標 |
|:-----|:---------|
| O↔S (Ousia-Schema) | Flow |
| S↔P (Schema-Perigraphē) | Scale |
| H↔K (Hormē-Kairos) | Valence |

## Series 内関係

各 Series の 4 定理は 3 種の内部ペアリングを持つ:

| 型 | 圏論 | 意味 |
|:---|:-----|:-----|
| D (Diagonal) | 随伴 (⊣) | 忘却と構成: T1⊣T3, T2⊣T4 |
| H (Horizontal) | 自然変換 | 目的切替: T1↔T2, T3↔T4 |
| X (Cross) | 双対 | 対極の対話: T1↔T4, T2↔T3 |
