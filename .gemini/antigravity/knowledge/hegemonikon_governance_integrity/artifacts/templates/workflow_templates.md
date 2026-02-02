# Workflow Output Templates (SE Enforced)

> **Status**: Mandatory for v6.7+ (mek) and v5.6+ (s)

## 1. /mek Output Template

```markdown
# /mek 出力

> **CCL**: `{ccl_expression}`
> **目的**: {purpose}
> **Scale**: {🔬 Micro | 🔭 Meso | 🌍 Macro}

---

## 失敗シナリオ ⚠️ [必須: Meso以上]

| 質問 | 回答 |
|:-----|:-----|
| Q1: 失敗するとしたら？ | {answer} |
| Q2: 最悪のケース？ | {answer} |
| Q3: 回避策？ | {answer} |

---

## 生成物
{content}

---

## メタ情報
⏱️ 所要時間: {N}m

---
→ **初版**です。`/dia-` でレビュー推奨。
```

## 2. /s Output Template

```markdown
# /s 出力

> **CCL**: `{ccl_expression}`
> **目的**: {purpose}
> **Scale**: {🔬 Micro | 🔭 Meso | 🌍 Macro}

---

## STAGE 0: Blindspot + Scale [必須]
📊 `✅ STAGE 0: Scale = {scale}`

... (STAGE 1-4) ...

## STAGE 5: 振り返り [必須]
| 項目 | 内容 |
|:-----|:-----|
| Keep | {1つ以上} |
| Problem | {1つ以上} |
| Try | {1つ以上} |

### 失敗パターン
| 躓き | 原因 | 対策 |
|:---|:---|:---|
| {where} | {why} | {how} |

⏱️ 合計: {N}m/45m
📊 `✅ STAGE 5: Retrospective → Doxa記録完了`
```

---
*Templates: 2026-02-01 | Governance v1.0*
