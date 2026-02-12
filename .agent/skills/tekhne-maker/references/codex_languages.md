# Codex: 言語ベストプラクティス

> **消化元**: files.zip → codex-languages.md (SKILL v4.0 参照)
> **消化日**: 2026-02-12
> **第一原理**: 「言語固有の落とし穴を環境で排除する」 = 第零原則の実装
> **HGK 対応**: Code Protocols Skill, /dev, /ene

---

## Engineering Axioms

| 公理 | 意味 | HGK 対応 |
|:-----|:-----|:---------|
| NO_HAPPY_PATH | Happy Path だけでテストしない | /dia Pre-Mortem |
| TYPE_SAFETY | 型で不正を排除 | BC-6 確信度 = 型システム |
| OBSERVABILITY | 見えないバグは直せない | /now 現在地確認 |

---

## Python

### 必須

- Type Hinting (100%), Pydantic Validation
- `async/await`, `pathlib.Path`
- Specific Exceptions (`raise ValueError("context")`)
- `structlog` / `logging.config.dictConfig`

### 禁止

```python
# ❌ 禁止パターン
print("debug")           # → structlog.get_logger()
global state             # → dataclass/Pydantic
f"SELECT {user_input}"   # → parameterized query
except Exception:         # → except SpecificError:
os.path.join()           # → pathlib.Path()
```

---

## Rust

### 必須

- `Result<T, E>` + `?` operator
- `tokio` (async runtime)
- `tracing` (logging)
- `&str` / `&[T]` (所有権を渡さない)
- Builder Pattern (3+ params)

### 禁止

```rust
// ❌ 禁止パターン
.unwrap()    // → .map_err(|e| ...)?
.expect()    // → context-rich error
.clone()     // → borrow で代替可能か検証
unsafe { }   // → // SAFETY: {理由} なしなら禁止
```

---

## Go

### 必須

- `context.Context` (全関数の第1引数)
- Error Wrapping: `fmt.Errorf("op: %w", err)`
- 並行制御: `sync.Mutex` / `chan`
- `go vet`, `-race` flag

### 禁止

```go
// ❌ 禁止パターン
panic("...")     // → return err
func init() {}  // → explicit initialization
return err       // → return fmt.Errorf("context: %w", err)
```

---

## TypeScript

### 必須

```json
// tsconfig.json
{ "compilerOptions": { "strict": true, "noUncheckedIndexedAccess": true } }
```

- `Readonly<T>`, `as const`
- `async/await` (callback 禁止)
- Zod validation (外部入力)

### 禁止

```typescript
// ❌ 禁止パターン
any                // → unknown + type guard
object["key"]      // → typed accessor
callback(err, data) // → async/await
eval()             // → 絶対禁止
```

---

*Codex Languages v1.0 — SKILL v4.0 消化 (2026-02-12)*
