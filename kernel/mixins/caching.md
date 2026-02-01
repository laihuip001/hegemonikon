---
mixin: Caching
capability: "結果をキャッシュ"
outputs: [cached_result, cache_hit]
python_analog: "@functools.cache, @lru_cache"
parameters:
  ttl: "duration (default: session)"
  key: "string (default: auto-generated)"
---

# Caching Mixin

> **「同じ入力には同じ結果を」**

## 機能

- 入力のハッシュ化
- キャッシュヒット/ミス判定
- TTL (Time-to-Live) 管理
- キャッシュ無効化

## CCL 注入

```ccl
ccl_injection: |
  let cache_key = hash($inputs)
  if /dox.exists{key=cache_key}:
    return /dox.get{key=cache_key}
  else:
    _ $target
    /dox{key=cache_key, ttl=$ttl} _
```

## 使用例

```ccl
# セッション中キャッシュ
@with(Caching) /sop{query="FEP研究"}

# 1時間キャッシュ
@with(Caching{ttl="1h"}) /zet+

# トレース + キャッシュ
@with(Tracing, Caching) /noe+
```

## パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|:-----------|:---|:-----------|:-----|
| `ttl` | duration | session | キャッシュ有効期間 |
| `key` | string | auto | カスタムキャッシュキー |

---

*Pythōsis B2 | Caching Mixin*
