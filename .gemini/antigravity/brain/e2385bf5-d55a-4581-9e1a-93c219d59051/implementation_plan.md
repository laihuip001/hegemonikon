# 認知の代数学 — 実装計画

> **Origin**: 2026-01-29 Cognitive Algebra 発見
> **Phase**: 1-2 (+ - * の実装)

---

## 記号定義 (確定)

| 記号 | 名称 | 効果 |
|:-----|:-----|:-----|
| `+` | 増量 | 出力を詳細化。量的増加。同層で拡張 |
| `-` | 縮約 | 出力を簡潔化。本質のみ。TL;DR モード |
| `*` | 展開 | メタ層移行。前提を問う。次元を増やす |

---

## Tier 1 ワークフロー実装

### 1. /noe (O1 Noēsis)

**追加 frontmatter:**

```yaml
operators:
  "+":
    description: "詳細分析。各フェーズで3倍の出力"
    output_multiplier: 3
  "-":
    description: "要点分析。結論+理由1つのみ"
    output_format: "TL;DR"
  "*":
    description: "メタ分析。分析の前提を問い直す"
    meta_shift: true
```

**出力形式例:**

| 呼び出し | 出力 |
|:---------|:-----|
| `/noe` | 5フェーズ分析 (標準) |
| `/noe+` | 5フェーズ × 詳細 (出力3倍) |
| `/noe-` | 結論 + 理由1つ (5行以内) |
| `/noe*` | 前提列挙 + 反転実験 + メタ問い |

---

### 2. /s (Schema 戦略)

**追加 frontmatter:**

```yaml
operators:
  "+":
    description: "詳細計画。代替案比較、却下理由を含む"
    output_multiplier: 2
  "-":
    description: "最小計画。Core Goals + Actions のみ"
    output_format: "minimal"
  "*":
    description: "戦略のメタ分析。この計画を立てる意味を問う"
    meta_shift: true
```

---

### 3. /zet (O3 Zētēsis)

**追加 frontmatter:**

```yaml
operators:
  "+":
    description: "深い問い。5層の問いを展開"
    layers: 5
  "-":
    description: "核心の問い。最も重要な1つだけ"
    layers: 1
  "*":
    description: "問いのメタ分析。なぜこの問いを問うのか"
    meta_shift: true
```

---

### 4. /bou (O2 Boulēsis)

**追加 frontmatter:**

```yaml
operators:
  "+":
    description: "詳細な意志分析。優先度 + 理由 + トレードオフ"
    include_tradeoffs: true
  "-":
    description: "端的な意志。最優先1つのみ"
    output_format: "single"
  "*":
    description: "意志のメタ分析。なぜこれを望むのか"
    meta_shift: true
```

---

## 実装手順

// turbo-all

### Step 1: /noe.md 更新

```bash
view_file /home/makaron8426/oikos/.agent/workflows/noe.md
# frontmatter に operators セクションを追加
```

### Step 2: /s.md 更新

```bash
view_file /home/makaron8426/oikos/.agent/workflows/s.md
# frontmatter に operators セクションを追加
```

### Step 3: /zet.md 更新

```bash
view_file /home/makaron8426/oikos/.agent/workflows/zet.md
# frontmatter に operators セクションを追加
```

### Step 4: /bou.md 更新

```bash
view_file /home/makaron8426/oikos/.agent/workflows/bou.md
# frontmatter に operators セクションを追加
```

### Step 5: 検証

- `/noe+` を実行して詳細出力を確認
- `/noe-` を実行して簡潔出力を確認
- `/noe*` を実行してメタ分析を確認

---

## 出力フォーマット標準

### `+` モード (増量)

```markdown
# /[wf]+ 結果

## [標準セクション1]
[詳細な内容 - 通常の3倍]

## [標準セクション2]
[詳細な内容 - 通常の3倍]

## 追加分析
[標準では省略される詳細]
```

### `-` モード (縮約)

```markdown
# /[wf]- 結果

**TL;DR**: [1文の結論]

理由: [1つだけ]
```

### `*` モード (展開)

```markdown
# /[wf]* 結果

## 暗黙の前提
1. [前提1]
2. [前提2]

## 前提への問い
- [問い1]
- [問い2]

## メタ分析
[この分析を行う意味は何か]
```

---

*v1.0 — 2026-01-29*
