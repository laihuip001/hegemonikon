# THE_CODEX: Language Specifications

言語別ベストプラクティスの強制適用仕様。

---

## Engineering Axioms（全言語共通）

| Axiom | Rule | Violation = Rejection |
|:---|:---|:---|
| **NO_HAPPY_PATH** | 全I/OにError Handling必須 | try/catchなし = NG |
| **TYPE_SAFETY_ABSOLUTISM** | 動的言語でもStrict Types必須 | Any/Object = NG |
| **OBSERVABILITY_FIRST** | 構造化ログ(JSON) + Prometheusメトリクス | print/console.log = NG |

---

## Python Specifications

### Mandatory Patterns

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Type Hinting** | `typing`モジュールを使用、100%のtype coverage | 型なし関数 = NG |
| **Validation** | Pydantic `BaseModel`でデータ検証 | 手動バリデーション = NG |
| **Async** | `asyncio` + `async/await`、blocking I/O禁止 | `time.sleep()` = NG |
| **Path Handling** | `pathlib.Path`のみ使用 | 文字列パス操作 = NG |
| **Error Handling** | 具体的な例外を捕捉 | `except Exception` = NG |

### Banned Patterns

```python
# ❌ FORBIDDEN
print("debug")                  # → logging.info()
global state                    # → Class/Dependency Injection
f"SELECT {user_input}"          # → SQLパラメータ化
except Exception:               # → except SpecificException
os.path.join()                  # → pathlib.Path()
```

### Required Imports

```python
from typing import Optional, List, Dict, Any, TypeVar
from pydantic import BaseModel, Field, validator
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)
```

---

## Rust Specifications

### Mandatory Patterns

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Error Handling** | `Result<T, E>`と`?`演算子 | `.unwrap()`/`.expect()` = NG |
| **Async Runtime** | `tokio` + `tracing` | 独自asyncランタイム = NG |
| **Zero-Copy** | `&str`/`&[T]`で所有権移動回避 | 不要な`.clone()` = NG |
| **Builder Pattern** | 複雑な構造体はBuilderで構築 | 長いnew()引数リスト = NG |
| **Unsafe** | `unsafe`は最終手段、コメント必須 | 説明なしunsafe = NG |

### Banned Patterns

```rust
// ❌ FORBIDDEN
value.unwrap()                  // → value?
value.expect("reason")          // → value.map_err(|e| ...)?
let x = data.clone();           // → let x = &data;（可能な場合）
unsafe { ... }                  // → 安全な代替を検討
```

### Required Structure

```rust
use anyhow::{Context, Result};
use tracing::{info, error, instrument};
use tokio;

#[instrument]
async fn process(input: &str) -> Result<Output> {
    let result = operation(input)
        .await
        .context("operation failed")?;
    Ok(result)
}
```

---

## Go Specifications

### Mandatory Patterns

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Context Propagation** | `ctx context.Context`は常に第1引数 | ctxなし関数 = NG |
| **Error Wrapping** | `fmt.Errorf("...: %w", err)` | 生errリターン = NG |
| **Concurrency** | `sync.Mutex`/Channelsで明示的制御 | 暗黙的共有 = NG |
| **Race Detection** | `-race`フラグでテスト必須 | race検出未実施 = NG |

### Banned Patterns

```go
// ❌ FORBIDDEN
panic("error")                  // → return error
func init() { ... }             // → 明示的初期化関数
go func() { ... }()             // → errgroup/worker pool
if err != nil { return err }    // → return fmt.Errorf("...: %w", err)
```

### Required Structure

```go
import (
    "context"
    "fmt"
    "golang.org/x/sync/errgroup"
)

func Process(ctx context.Context, input string) (Output, error) {
    result, err := operation(ctx, input)
    if err != nil {
        return Output{}, fmt.Errorf("process failed: %w", err)
    }
    return result, nil
}
```

---

## TypeScript Specifications

### Mandatory Patterns

| Pattern | Implementation | Violation |
|:---|:---|:---|
| **Strict Mode** | `tsconfig.json`で`strict: true` | `any`型使用 = NG |
| **Immutability** | `const`/`Readonly<T>`優先 | 可変オブジェクト = NG |
| **Async/Await** | Promise chainより`async/await` | callback hell = NG |
| **Validation** | `zod`でランタイム検証 | 手動バリデーション = NG |

### Banned Patterns

```typescript
// ❌ FORBIDDEN
let value: any                  // → let value: SpecificType
object["key"]                   // → object.key（型安全）
.then().catch()                 // → async/await + try/catch
eval()                          // → 絶対禁止
```

### Required Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### Required Structure

```typescript
import { z } from 'zod';

const InputSchema = z.object({
  name: z.string().min(1),
  age: z.number().positive(),
});

type Input = z.infer<typeof InputSchema>;

async function process(input: Input): Promise<Output> {
  const validated = InputSchema.parse(input);
  return await operation(validated);
}
```

---

## Language Selection Matrix

| Criteria | Python | Rust | Go | TypeScript |
|:---|:---:|:---:|:---:|:---:|
| **Rapid Prototyping** | ✓ | - | - | ✓ |
| **High Performance** | - | ✓ | ✓ | - |
| **Memory Safety** | - | ✓ | - | - |
| **Concurrency** | - | ✓ | ✓ | - |
| **ML/Data** | ✓ | - | - | - |
| **Web Frontend** | - | - | - | ✓ |
| **CLI Tools** | ✓ | ✓ | ✓ | - |
| **Microservices** | - | ✓ | ✓ | ✓ |

---

## Compliance Check Protocol

```
□ Type coverage = 100%
□ Error handling = explicit (no silent failures)
□ Logging = structured (JSON format)
□ Tests = minimum 80% coverage
□ Linting = zero warnings
□ Banned patterns = zero occurrences
```
