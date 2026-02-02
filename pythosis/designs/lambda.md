# Lambda 式設計

> **CCL**: `/s+*^/noe`

---

## 構文候補

| 記法 | 例 | 推奨 |
|:-----|:---|:----:|
| `L:[x]{WF}` | `L:[x]{/noe+{x}}` | ★ |
| `lam(x) WF` | `lam(x) /noe+{x}` | |
| `λ(x): WF` | `λ(x): /noe+{x}` | |

## 推奨構文

```ccl
L:[x]{/noe+{target=x}}
L:{/bou~zet}  # 引数なし
```

## 用途

1. **高階マクロ**: `@retry(3, on_fail=L:{/dia^})`
2. **動的操作**: `@chain(L:[x]{/noe+{x}})`
3. **アドホック定義**: 一時的な認知操作

## 実装方針

1. `@partial` で代替可能なケースを先に網羅
2. `@partial` では不足する場合に Lambda 導入

---

*Lambda Design v1.0*
