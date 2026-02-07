---
description: A2 Krisis lex 派生の短縮形。プロンプト表現の教養・フィードバック。
hegemonikon: Akribeia
modules: [A2]
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
version: "1.1"
lcm_state: beta
lineage: "v1.0 + SEL 統合 → v1.1"
derivatives: [dict, mech, feed]
cognitive_algebra:
  "+": "詳細解説。作用機序を含む完全分析"
  "-": "要点のみ。推奨表現リスト"
  "*": "表現分析のメタ視点"
sel_enforcement:
  "+":
    description: "MUST provide full analysis with mechanism"
    minimum_requirements:
      - "作用機序 必須"
      - "完全分析 必須"
  "-":
    description: "MAY provide recommended expressions only"
    minimum_requirements:
      - "推奨表現リストのみ"
  "*":
    description: "MUST provide meta perspective on expression analysis"
    minimum_requirements:
      - "表現分析のメタ視点"
anti_skip: disabled
ccl_signature: "/lex mech"
---

# /lex: 表現教養ワークフロー

> **正本**: [A2 Krisis SKILL.md](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md)
> **本質**: `/dia lex` の短縮形。UX 改善のため独立コマンド化。

---

## 派生モード

| 派生 | コマンド | 機能 |
|:-----|:---------|:-----|
| **dict** | `/lex dict` | 推奨表現・避ける表現を一覧 |
| **mech** | `/lex mech` | 作用機序解説（なぜそう出力されるか） |
| **feed** | `/lex feed` | チャット履歴から改善点を抽出 |

---

## 使用例

### /lex mech — 作用機序解説

```text
/lex mech 「教えて」と「考えて」の違い
```

**出力**:

| 表現 | モード | 出力特性 |
|:-----|:-------|:---------|
| 「教えて」 | Retrieval | 事実ベース、簡潔 |
| 「考えて」 | Generation | 推論ベース、過程展開 |

**作用機序**:

1. Retrieval Mode vs Generation Mode
2. Token Probability Shift
3. Output Structure 変化

---

### /lex dict — 表現辞書

```text
/lex dict
```

**出力**: 推奨表現・避ける表現の一覧

| 状況 | ⭕ 推奨 | ❌ 避ける |
|:-----|:-------|:---------|
| 事実取得 | 「教えて」 | 「考えて」 |
| 分析依頼 | 「考えて」「分析して」 | 「教えて」 |
| 具体指示 | 「Xの条件でYを返す」 | 「適切に処理して」 |

---

### /lex feed — 履歴フィードバック

```text
/lex feed
```

**入力**: 現在のチャット履歴（自動取得）

**出力**: 改善すべき表現 + 取り入れるべき技法

---

## Hegemonikon Status

| Module | Workflow | 正本 | Status |
|:-------|:---------|:-----|:-------|
| A2 Krisis | /lex | a2-krisis/SKILL.md | v1.0 Ready |

---

*v1.0 — /dia lex の UX 改善版 (2026-01-30)*
