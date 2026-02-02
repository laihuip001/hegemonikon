# Gemini 3 Pro / Jules API プロンプト最適化レポート

> **Source**: Perplexity /sop 調査 2026-01-29
> **Purpose**: M10 TARGET_AGENT 最適化パラメータの確定

---

## Executive Summary

**Gemini 3 Paradigm Shift** (2025年11月):

- 詳細で説明的なプロンプト → **逆効果** (output 2-3倍, latency +20-30%)
- **「Less is More」**: プロンプト長 30-50%削減推奨
- **Constraint Pinning 廃止**: 制約の反復は -2-4% accuracy

**Jules API**:

- **plan-based workflow** + **explicit completion criteria**
- Single comprehensive task > Multiple subtasks

**共通パターン**: Context → Task → Format (3段構成)

---

## Gemini 3 Pro 最適化

### 推奨構造 (5セクション)

1. **ROLE** — 1-2文のみ ("Code reviewer" 程度)
2. **TASK** — 1-2文の直接指示
3. **CONTEXT** — 必須情報のみ (長文OK, 2M token対応)
4. **CONSTRAINTS** — **1回のみ** (重複厳禁)
5. **OUTPUT FORMAT** — "JSON" or "bullet points" (最小限)

### Constraint Pinning = アンチパターン

```yaml
# ❌ 悪い (Gemini 3 で -2-4% accuracy)
"Avoid deprecated APIs.
Do not suggest deprecated APIs.
Never use deprecated APIs."

# ✅ 良い
"Avoid deprecated APIs."
```

### System vs User Prompt

- System Prompt: **50-100トークン** (最小限)
- User Prompt: タスク固有の詳細

### 出力形式

```yaml
# ❌ 冗長
"Please provide your response in a valid JSON format..."

# ✅ 簡潔
"Output: {issues: [string], priority: 'high'|'low'}"
```

---

## Jules API 最適化

### 推奨構造

1. **Objective** — 1-2文でゴール
2. **Scope** — 対象ファイル/ディレクトリ明記
3. **Acceptance Criteria** — 完了条件明示
4. **Do NOT** — やらないこと明記

### 単一タスク推奨

```yaml
# ✅ 推奨 (1 task)
"Implement login feature:
1. Update database schema
2. Create React form
3. Add API endpoint
4. Write unit tests"

# ❌ 非推奨 (4 tasks)
Task 1: "Update schema"
Task 2: "Create form"
...
```

---

## 効果 (Benchmark)

| モデル | 標準prompt | 最適化prompt | 改善 |
|:-------|:-----------|:-------------|:-----|
| Claude 3.5 | 88% | 92% | +4% |
| Gemini 3 | 83% | 89% | **+6%** |
| GPT-4o | 77% | 83% | +6% |

---

*Digested for M10 TARGET_AGENT v6.7*
