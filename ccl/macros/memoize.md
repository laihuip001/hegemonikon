# @memoize マクロ

> **Python 対応**: `@functools.cache`, `@lru_cache`

## 定義

```yaml
macro: @memoize
parameters:
  ttl: duration (default: session)
```

## 目的

WF の実行結果をキャッシュし、同一入力に対する再計算を省略する。

## 構文

```ccl
@memoize /sop+           # セッション中キャッシュ
@memoize(ttl=1h) /sop+   # 1時間キャッシュ
@memoize(ttl=∞) /sop+    # 永続キャッシュ
```

## CCL 展開

```ccl
@memoize(ttl=$ttl) $target
→
/dox{lookup=true} I:hit{$target:cached} 
                  I:miss{$target _/dox{persist=true, ttl=$ttl}}
```

## 適用例

| WF | キャッシュ理由 |
|:---|:---------------|
| `/sop+` | API 呼び出しコスト |
| `/syn+` | 評議会コスト |
| `/eat+` | 消化コスト |

---

*@memoize | Python functools.cache*
