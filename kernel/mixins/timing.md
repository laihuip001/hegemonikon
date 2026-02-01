---
mixin: Timing
capability: "実行時間を計測"
outputs: [duration_ms, performance_log]
python_analog: "time.perf_counter, @timer decorator"
parameters:
  warn_threshold: "duration (optional)"
  log_level: "string (default: info)"
---

# Timing Mixin

> **「どれだけ時間がかかったか」**

## 機能

- 実行時間の精密計測
- 閾値超過時の警告
- パフォーマンスログ出力
- 統計情報の蓄積

## CCL 注入

```ccl
ccl_injection: |
  start = perf_counter()
  result = $target
  duration = perf_counter() - start
  
  @log{level=$log_level, msg="Duration: ${duration}ms"}
  
  if $warn_threshold and duration > $warn_threshold:
    @log{level="warn", msg="Slow execution: ${duration}ms > ${warn_threshold}"}
  
  return result with { duration_ms: duration }
```

## 使用例

```ccl
# 基本計測
@with(Timing) /noe+

# 1秒超で警告
@with(Timing{warn_threshold="1s"}) /sop{query="重い処理"}

# トレース + 計測
@with(Tracing, Timing) /zet+
```

## パラメータ

| パラメータ | 型 | デフォルト | 説明 |
|:-----------|:---|:-----------|:-----|
| `warn_threshold` | duration | - | 警告閾値 |
| `log_level` | string | info | ログレベル |

---

*Pythōsis B2 | Timing Mixin*
