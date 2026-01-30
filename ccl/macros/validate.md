# @validate マクロ

> **Python 対応**: `@validator`, `assert`

## 定義

```yaml
macro: @validate
parameters:
  pre: CCL式 (事前条件)
  post: CCL式 (事後条件)
```

## 目的

WF 実行の前後で検証を行い、品質を保証する。

## 構文

```ccl
@validate(pre=?h2>0.5) /ene
# 確信度 0.5 以上なら実行

@validate(post=/dia-) /s+
# 設計後に軽量検証

@validate(pre=?k1, post=/dia-) /ene
# 事前: タイミング確認、事後: 検証
```

## CCL 展開

```ccl
@validate(pre=$pre, post=$post) $target
→
$pre _$target _$post
```

## 適用例

| WF | 事前条件 | 事後条件 |
|:---|:---------|:---------|
| `/ene` | `?k1` (タイミング) | `/dia-` |
| `/s+` | `?h2>0.7` (確信度) | `/sta-` |

---

*@validate | Python validator pattern*
