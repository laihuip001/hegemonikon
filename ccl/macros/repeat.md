# @repeat マクロ

> **Python 対応**: `itertools.repeat()`
> **CCL**: 同一思考の N 回反復

## 定義

```yaml
macro: @repeat
parameters:
  target: CCL式
  n: 反復回数
```

## 目的

同じ思考を複数回実行し、結果を累積する。

## 構文

```ccl
@repeat(/u+*^/noe, 2)   # 2回実行
@repeat(/dia+, 3)       # 3回検証
```

## 用途

| 用途 | 例 |
|:-----|:---|
| 深掘り | 同じ問いを複数回掘り下げる |
| 検証強化 | 複数回の独立した検証 |
| サンプリング | 確率的出力の複数サンプル |

## CCL 展開

```ccl
@repeat(A, N)
→
F:N{A}
```

## 適用例

```ccl
# 同じ主観的分析を2回行い、一貫性を確認
@repeat(/u+*^/noe, 2) _/dia[compare]
```

---

*@repeat | itertools.repeat()*
