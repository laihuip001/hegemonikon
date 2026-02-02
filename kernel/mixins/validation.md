---
mixin: Validation
capability: "事前/事後検証"
outputs: [validation_result, errors]
python_analog: "pydantic, @validator, assert"
parameters:
  pre: "CCL expression (optional)"
  post: "CCL expression (optional)"
  schema: "type definition (optional)"
---

# Validation Mixin

> **「正しさを保証する」**

## 機能

- 事前条件 (precondition) 検証
- 事後条件 (postcondition) 検証
- スキーマ検証
- 型チェック

## CCL 注入

```ccl
ccl_injection: |
  # 事前検証
  if $pre:
    assert $pre, "Precondition failed"
  
  result = $target
  
  # 事後検証
  if $post:
    assert $post(result), "Postcondition failed"
  
  # スキーマ検証
  if $schema:
    validate(result, $schema)
  
  return result
```

## 使用例

```ccl
# 入力検証
@with(Validation{pre=L:{$inputs.target != null}}) /noe+

# 出力検証
@with(Validation{post=L:[r]{r.confidence > 0.7}}) /dia

# スキーマ検証
@with(Validation{schema=ThoughtResult}) /noe+
```

## パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|:-----------|:---|:-----------|:-----|
| `pre` | CCL | - | 事前条件 |
| `post` | CCL | - | 事後条件 |
| `schema` | type | - | 出力スキーマ |

---

*Pythōsis B2 | Validation Mixin*
