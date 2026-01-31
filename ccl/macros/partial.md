# @partial マクロ

> **Python 対応**: `functools.partial()`
> **CCL**: 部分適用（文脈固定）

## 定義

```yaml
macro: @partial
parameters:
  bindings: key=value のペア
  target: CCL式
```

## 目的

WF に事前に文脈やパラメータを固定し、特化した WF を作成する。

## 構文

```ccl
@partial(context="Hegemonikón開発") /zet+
@partial(scope="session", depth=3) /noe+
```

## 用途

| 用途 | 例 |
|:-----|:---|
| 文脈固定 | 特定のプロジェクト文脈で探求 |
| パラメータプリセット | 深度やスコープの事前設定 |
| WF のカスタマイズ | 汎用 WF を特化 WF に変換 |

## CCL 展開

```ccl
@partial(context=$ctx) $target
→
/kho{context=$ctx} _$target
```

## 適用例

```ccl
# Hegemonikón 開発専用の探求
@hege_zet := @partial(context="Hegemonikón") /zet+

# 使用
@hege_zet  # 文脈が固定済み
```

## Lambda との関係

`@partial` は Python の `partial()` と同様に、
将来的な Lambda 式 (匿名 WF) の基盤となりうる。

```ccl
# 将来的な Lambda 構文案
λ(x): /noe+{target=x}
```

---

*@partial | functools.partial()*
