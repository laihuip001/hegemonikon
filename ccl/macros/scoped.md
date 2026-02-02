# @scoped マクロ

> **Python 対応**: `@contextmanager`, `with` 文

## 定義

```yaml
macro: @scoped
parameters:
  scope: session | task | block
```

## 目的

WF の実行スコープを限定し、副作用を制御する。

## 構文

```ccl
@scoped(session) /boot    # セッション限定
@scoped(task) /s+         # タスク限定
@scoped(block) /noe+      # ブロック限定（即座に破棄）
```

## CCL 展開

```ccl
@scoped($scope) $target
→
/kho{scope=$scope} _$target _/kho{exit}
```

## 効果

| スコープ | 永続化 | 用途 |
|:---------|:------:|:-----|
| `session` | セッション終了まで | `/boot`, `/bye` |
| `task` | タスク完了まで | 一時的な設計 |
| `block` | 即座に破棄 | 探索的思考 |

---

*@scoped | Python contextmanager*
