---
mixin: Retry
capability: "失敗時にリトライ"
outputs: [attempt_count, final_result]
python_analog: "tenacity, @retry decorator"
parameters:
  max_attempts: "int (default: 3)"
  backoff: "duration (default: 1s)"
  on_fail: "CCL expression (optional)"
---

# Retry Mixin

> **「失敗しても諦めない」**

## 機能

- 指定回数までリトライ
- 指数バックオフ
- 失敗時のフォールバック処理
- リトライ条件のカスタマイズ

## CCL 注入

```ccl
ccl_injection: |
  for attempt in 1..$max_attempts:
    try:
      result = $target
      return result
    catch:
      @log{level="warn", msg="Attempt $attempt failed"}
      sleep($backoff * 2^(attempt-1))
  # 全リトライ失敗
  if $on_fail:
    $on_fail
  else:
    raise RetryExhausted
```

## 使用例

```ccl
# 3回リトライ
@with(Retry) /sop{query="外部API"}

# 5回、失敗時はメタ分析
@with(Retry{max_attempts=5, on_fail=L:{/dia^}}) /zet+

# トレース + リトライ
@with(Tracing, Retry) /ene
```

## パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|:-----------|:---|:-----------|:-----|
| `max_attempts` | int | 3 | 最大リトライ回数 |
| `backoff` | duration | 1s | 初期待機時間 |
| `on_fail` | CCL | - | 全失敗時の処理 |

---

*Pythōsis B2 | Retry Mixin*
