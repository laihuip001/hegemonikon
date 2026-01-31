# @chain マクロ

> **Python 対応**: `itertools.chain()`
> **CCL**: `_` の強化版（エラー時も継続）

## 定義

```yaml
macro: @chain
parameters:
  items: CCL式の配列
  on_error: continue | stop (default: continue)
```

## 目的

複数の思考を直列化し、途中でエラーがあっても継続する。

## 構文

```ccl
@chain(/bou+, /zet+, /s+)
@chain(/noe, /dia, /ene, on_error=stop)
```

## `_` との違い

| 演算子 | エラー時 | 用途 |
|:-------|:---------|:-----|
| `_` | 停止 | 依存関係のある逐次処理 |
| `@chain` | 継続 | 独立した処理の直列化 |

## CCL 展開

```ccl
@chain(A, B, C)
→
A | continue _B | continue _C
```

## 適用例

```ccl
# 複数の探索を全て試行
@chain(/zet+[A], /zet+[B], /zet+[C])
```

---

*@chain | itertools.chain()*
