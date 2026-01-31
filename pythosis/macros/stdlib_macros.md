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

---

*stdlib Macros v1.0*
