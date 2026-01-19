---
id: G-4
layer: Lifecycle (Ops & Maintenance)
enforcement_level: L2
---

# G-4: Lifecycle Protocol

> Controls change management, documentation, logging, and rollback strategies.

---

## M-10: Ripple Effect (HIGH)

**Rule:** Predict the "Blast Radius" before any change.

**Triggers:**

- Renaming function/class
- Changing function signature
- Modifying DB/API schema
- Altering global constants

**Process:**

1. Identify symbol to change
2. Scan codebase for all usages
3. List affected files/lines
4. Classify risk: LOW/MEDIUM/HIGH
5. Update consumers BEFORE applying change

---

## M-13: Code Archaeology (MEDIUM)

**Rule:** Chesterton's Fence — don't remove code until you know why it exists.

**Detection Signs:**

- `FIXME`, `HACK`, `Workaround`, Ticket refs
- Overly defensive checks (`if x is not None and x != ""`...)
- Magic numbers/sleeps

**Action:** HALT deletion. Hypothesize reason. Query history if possible.

---

## M-14: Narrative Commits (MEDIUM)

**Rule:** Commits are letters to future maintainers.

**Format:**

```
{type}({scope}): {summary}

**Context:** Why was this change needed?
**Solution:** Technical explanation
**Alternatives Considered:** What was rejected?

Refs: #{issue}
```

**Forbidden:** "fix bug", "update", empty body

---

## M-17: Structured Logging (MEDIUM)

**Rule:** Logs are data, not text. NO `print()`.

**Schema Required:**

- `level`: INFO/WARN/ERROR/DEBUG
- `timestamp`: ISO 8601
- `message`: Summary
- `context`: Dict of variables (`user_id`, `order_id`)
- `trace_id`: Correlation ID

**Forbidden:** String concatenation, logging PII

---

## M-18: Feature Flags (HIGH)

**Rule:** Deployment ≠ Release. Wrap new features in flags.

**Rules:**

- Default: `FALSE` (OFF)
- Always provide `else` fallback
- Naming: `snake_case` (`enable_new_checkout`)

**Process:**

1. Define unique flag key
2. Scaffold: `if flags.get("KEY"): [new] else: [old]`
3. Ensure graceful failure if flag missing

---

## M-22: Auto-Documentation (MEDIUM)

**Rule:** Code and docs update atomically. Sync-or-Die.

**Targets:**

- Docstrings (update `@param`, `@return`)
- README (update usage examples)
- ADR (for major structural changes)

**Process:**

1. Implement code change
2. Identify affected docs
3. Rewrite docs to match new reality
4. Output BOTH in same response

---

## M-25: Rollback Strategy (CRITICAL)

**Rule:** Every change must be reversible.

**Rules:**

- DB Migrations: Every `UP` has a `DOWN`
- Config: State previous value for restoration
- Files: Assume backup needed

**Output Format:**

1. Forward (implementation)
2. Reverse (rollback)
3. Risk Assessment (data loss warning)

---

## M-27: Product Registry Protocol (MEDIUM)

**Rule:** READMEの**作成・削除・重要更新**時、`docs/products_index.md` を同期更新。

**Trigger:**

- README.md の新規作成
- README.md の削除
- README.md のタイトル、ステータス、概要の変更

**Status Definition:**

| Emoji | Status | Meaning |
|---|---|---|
| 📝 | Planning | 設計中、未着手 |
| 🚧 | In Progress | 開発中 |
| ✅ | Released | 完成、公開済み |
| 🔒 | Archived | 凍結、保守停止 |
| ❌ | Deprecated | 非推奨、削除予定 |

**Process:**

1. README変更を検出
2. インデックス対応行を更新（なければ追加）
3. 両方を同じレスポンスで出力
