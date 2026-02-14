# stdlib 消化済みマクロ

> **Phase 2 成果物**

---

## itertools 由来 (3)

| マクロ | Python | 用途 |
|:-------|:-------|:-----|
| `@chain` | `itertools.chain` | 直列化（エラー継続）|
| `@cycle` | `itertools.cycle` | 無限反復 |
| `@repeat` | `itertools.repeat` | N回反復 |

## functools 由来 (2)

| マクロ | Python | 用途 |
|:-------|:-------|:-----|
| `@reduce` | `functools.reduce` | 累積融合 |
| `@partial` | `functools.partial` | 部分適用 |

---

## 使用例

```ccl
@chain(/bou+, /zet+, /s+)
@cycle(/s, /dia, until=?h2>0.9)
@repeat(/u+*^/noe, 2)
@reduce(*, /o, /s, /h)
@partial(context="Heg") /zet+
```

## Lambda 式 (Phase 2b)

> **正式構文**: `L:[x]{WF}` (ccl/operators.md v6.52)

```ccl
# 高階マクロへの渡し
@retry(3, on_fail=L:{/dia^})

# マッピング
F:[tasks]{L:[t]{/noe+{target=t}}}

# アドホック操作
L:{/bou*zet}
```

---

*stdlib Macros v1.1 | Lambda 正式化*
