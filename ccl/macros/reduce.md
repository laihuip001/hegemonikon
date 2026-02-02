# @reduce マクロ

> **Python 対応**: `functools.reduce()`
> **CCL**: `*` の累積版（多→一）

## 定義

```yaml
macro: @reduce
parameters:
  op: 二項演算子 (*, ~)
  items: CCL式の配列
```

## 目的

複数の思考を左から順に累積的に融合し、単一の結果を得る。

## 構文

```ccl
@reduce(*, /noe, /dia, /bou)
# = ((/noe * /dia) * /bou)

@reduce(~, /s, /a, /h)
# = ((/s ~ /a) ~ /h)
```

## `*` との違い

| 演算子 | 適用 | 結果 |
|:-------|:-----|:-----|
| `A*B*C` | 同時融合 | 3つを一度に統合 |
| `@reduce(*, A, B, C)` | 累積融合 | (A*B) の結果と C を融合 |

## 認知的意味

累積融合は「段階的な統合」を可能にする。

- 第1段階で A と B を統合
- その結果を踏まえて C を統合
- 各段階で文脈が蓄積される

## CCL 展開

```ccl
@reduce(op, A, B, C, D)
→
((A op B) op C) op D
```

## 適用例

```ccl
# 6つの Hub を順次統合
@reduce(*, /o, /s, /h, /p, /k, /a)
```

---

*@reduce | functools.reduce()*
