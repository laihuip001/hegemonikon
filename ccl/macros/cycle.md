# @cycle マクロ

> **Python 対応**: `itertools.cycle()`
> **CCL**: `~` の無限版（収束まで反復）

## 定義

```yaml
macro: @cycle
parameters:
  items: CCL式の配列
  until: 終了条件 (default: converged)
  max: 最大反復数 (default: 10)
```

## 目的

複数の思考を収束するまで無限に往復する。

## 構文

```ccl
@cycle(/noe, /dia)                    # 収束まで
@cycle(/bou, /zet, until=?h2>0.9)     # 確信度 90% まで
@cycle(/s, /dia, max=5)               # 最大5回
```

## `~` との違い

| 演算子 | 反復 | 用途 |
|:-------|:-----|:-----|
| `~` | 1往復 | 対話的探索 |
| `@cycle` | 収束まで | 洗練的探索 |

## CCL 展開

```ccl
@cycle(A, B, until=cond, max=N)
→
~:cond{A ~B, depth=N}
```

## 適用例

```ccl
# 設計と検証を確信度が上がるまで繰り返す
@cycle(/s+, /dia-, until=?h2>0.9)
```

---

*@cycle | itertools.cycle()*
