---
name: Macro Registry
version: "1.0"
description: CCL マクロの定義と演算子ルール
---

# CCL マクロレジストリ

> **目的**: 定理の合成をマクロとして再利用可能にする

---

## 登録マクロ

### Tier 0: 基本マクロ

| マクロ | 定義 | 用途 |
|:-------|:-----|:-----|
| `@tak` | `/s1 _ /sta _ /kho _ /zet _ /chr _ /euk _ /bou` | タスク整理 |
| `@考` | `/noe- _ /zet- _ /dia-` | 思考 (thinking) |
| `@u` | `/u+` | Claudeの主観意見 |

### Tier 1: 標準ライブラリ

| マクロ | 定義 | 用途 | 由来 |
|:-------|:-----|:-----|:-----|
| `@mece` | `/kho_/sta` | 漏れなく重複なく分類 | 問題分解 |
| `@ooda` | `/noe_/bou_/dia_/ene` | 観察→判断→決定→行動 | 意思決定 |
| `@pdca` | `F:{/s_/ene_/dia_/ene}` | Plan→Do→Check→Act | 改善サイクル |
| `@5why` | `F:5{/zet}` | 根本原因分析 | Five Whys |
| `@design` | `/ore_/kho_/zet_/ene-_/dia` | 共感→定義→発想→試作→検証 | デザイン思考 |

### Tier 2: ユーザーライブラリ

> **完全版**: [TIER2_LIBRARY.md](file:///home/makaron8426/oikos/.agent/macros/TIER2_LIBRARY.md)
>
> **166モード派生 + 71マクロ** — 全ての王道思考法を包括

### メタマクロ

| マクロ | 定義 | 用途 |
|:-------|:-----|:-----|
| `@naturalize` | `F:{/eat_(@dia~)_IF{!green}:/mek+}[until:all_green]` | 完全消化 |
| `@dia~` | `(/dia~/noe)~(\dia~/noe)` | 弁証法的診断 |

---

## マクロ演算子ルール

### 単項演算子（伝播）

```yaml
"+": 
  meaning: 詳細化
  behavior: 内部全WFに + を伝播
  example: "@tak+ → /s1+ _ /sta+ _ ..."

"^":
  meaning: メタ化  
  behavior: マクロ自体を問う
  example: "@tak^ → この分類ロジックは正しいか"
```

### 二項演算子

```yaml
"~": 
  meaning: 振動
  syntax: "@macro~/wf"
  behavior: マクロと他WFの反復サイクル
  example: "@tak~/s → 分類 ↔ 戦略 の振動"

"*":
  meaning: 融合
  syntax: "@macro*/wf"
  behavior: マクロ出力を次WFの入力に
  example: "@tak*/ene → 分類結果を即実行"

"_":
  meaning: チェイン
  syntax: "@macro _ /wf"
  behavior: 順次実行
  example: "@tak _ /ene → 分類後に実行"
```

---

## 演算子優先順位

```
1. ^ (メタ) — 最高
2. + (詳細)
3. * (融合)
4. ~ (振動)
5. _ (チェイン) — 最低
```

**括弧で明示**:

```ccl
(@tak+)~/s   # 詳細版タスク分類と戦略の振動
(@tak~/s)^   # 振動サイクル自体を問う
```

---

## 新規マクロ追加手順

1. `.agent/macros/{name}.md` を作成
2. CCL 定義を記述
3. このレジストリに登録
4. (任意) Python 実装を `mekhane/` に追加

---

*v1.0 — Macro Registry (2026-01-30)*
