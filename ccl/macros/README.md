# CCL デコレータマクロ (Pythōsis B3)

> **Origin**: Python `@decorator` パターン
> **Version**: v1.0 | 2026-02-01

---

## 概要

デコレータマクロは、CCL 操作に「横断的関心事」を簡潔に付与する構文糖衣。
内部的には Mixin (`@with`) に展開される。

## マクロ一覧

| マクロ | Mixin 展開 | Python 対応 |
|:-------|:-----------|:------------|
| `@memoize` | `@with(Caching)` | `@functools.cache` |
| `@retry` | `@with(Retry)` | `tenacity` |
| `@log` | `@with(Tracing)` | `logging` |
| `@validate` | `@with(Validation)` | `pydantic` |
| `@timed` | `@with(Timing)` | `time` |
| `@scoped` | 特殊展開 | `contextmanager` |
| `@async` | 特殊展開 | `asyncio` |

---

## 個別定義

### @memoize — 結果キャッシュ

```yaml
macro: @memoize
parameters:
  ttl: duration (default: session)
expansion: "@with(Caching{ttl=$ttl}) $target"
```

**例**:
```ccl
@memoize /sop{query="重い検索"}
@memoize(ttl="1h") /zet+
```

---

### @retry — 失敗時リトライ

```yaml
macro: @retry
parameters:
  max: int (default: 3)
  on_fail: CCL (optional)
expansion: "@with(Retry{max_attempts=$max, on_fail=$on_fail}) $target"
```

**例**:
```ccl
@retry /sop{query="外部API"}
@retry(max=5, on_fail=L:{/dia^}) /ene
```

---

### @log — 実行ログ

```yaml
macro: @log
parameters:
  level: string (default: info)
expansion: "@with(Tracing{log_level=$level}) $target"
```

**例**:
```ccl
@log /noe+
@log(level="debug") /zet+
```

---

### @validate — 事前/事後検証

```yaml
macro: @validate
parameters:
  pre: CCL (optional)
  post: CCL (optional)
expansion: "@with(Validation{pre=$pre, post=$post}) $target"
```

**例**:
```ccl
@validate(pre=L:{$inputs != null}) /noe+
@validate(post=L:[r]{r.confidence > 0.7}) /dia
```

---

### @timed — 実行時間計測

```yaml
macro: @timed
parameters:
  warn: duration (optional)
expansion: "@with(Timing{warn_threshold=$warn}) $target"
```

**例**:
```ccl
@timed /noe+
@timed(warn="2s") /sop{query="長い処理"}
```

---

### @scoped — スコープ限定実行

```yaml
macro: @scoped
parameters:
  ctx: context (required)
expansion: |
  let _saved = $ctx
  try:
    $target
  finally:
    restore(_saved)
```

**例**:
```ccl
@scoped(ctx="temp_workspace") /ene
```

---

### @async — 非同期実行

```yaml
macro: @async
parameters:
  await: bool (default: false)
expansion: |
  spawn_async($target)
  if $await:
    await_result()
```

**例**:
```ccl
@async /sop{query="バックグラウンド検索"}
@async(await=true) /noe+
```

---

## 複雑度

| マクロ | pt |
|:-------|:--:|
| 単純 (`@log`, `@timed`) | 2 |
| パラメータ付き (`@memoize`, `@retry`, `@validate`) | 3 |
| 特殊 (`@scoped`, `@async`) | 4 |

---

*Pythōsis B3 | Decorator Macros v1.0*
