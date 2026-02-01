---
mixin: Tracing
capability: "実行過程を記録"
outputs: [trace_log, execution_path]
python_analog: "logging, @trace decorator"
---

# Tracing Mixin

> **「何が起きたかを記録する」**

## 機能

- 実行開始/終了のタイムスタンプ
- 入力パラメータのキャプチャ
- 出力結果の記録
- 例外発生時のスタックトレース

## CCL 注入

```ccl
ccl_injection: |
  @log.start{target=$target, inputs=$inputs}
  _ $target
  @log.end{result=$result}
  /dox{key="trace_$id"} _
```

## 使用例

```ccl
# 深い思考の過程を記録
@with(Tracing) /noe+{target="複雑な問題"}

# 複合: トレース + キャッシュ
@with(Tracing, Caching) /zet+
```

## 出力形式

```yaml
trace_log:
  id: "trace_001"
  target: "/noe+"
  started_at: "2026-02-01T16:25:00Z"
  ended_at: "2026-02-01T16:25:03Z"
  duration_ms: 3000
  inputs: { target: "複雑な問題" }
  result: { ... }
```

---

*Pythōsis B2 | Tracing Mixin*
