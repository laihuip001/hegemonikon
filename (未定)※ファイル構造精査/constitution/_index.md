# Development Constitution

> 25 modules → 6 files → **3 principles.**

---

## 🎯 Three Principles

| # | Principle | Meaning |
|---|---|---|
| 1 | **Guard** | 大事なものには触らせない (M-01, M-02, M-03) |
| 2 | **Prove** | 動くと言う前にテストで示せ (M-04, M-09, M-11) |
| 3 | **Undo** | 何をしても元に戻せる状態を保て (M-25, M-18) |

---

## 📚 Layer Reference

| File | Layer | Modules |
|---|---|---|
| [00_orchestration](file:///c:/Users/laihuip001/開発（太郎）/dev-rules/constitution/00_orchestration.md) | Core | State, Modes, Butler |
| [01_environment](file:///c:/Users/laihuip001/開発（太郎）/dev-rules/constitution/01_environment.md) | G-1 Iron Cage | M-01, M-02, M-03, M-19* |
| [02_logic](file:///c:/Users/laihuip001/開発（太郎）/dev-rules/constitution/02_logic.md) | G-2 Logic Gate | M-04, M-05, M-06, M-15, M-16, M-20, M-21 |
| [03_security](file:///c:/Users/laihuip001/開発（太郎）/dev-rules/constitution/03_security.md) | G-3 Shield | M-09, M-11, M-12, M-23, M-24 |
| [04_lifecycle](file:///c:/Users/laihuip001/開発（太郎）/dev-rules/constitution/04_lifecycle.md) | G-4 Lifecycle | M-10, M-13, M-14, M-17, M-18, M-22, M-25 |
| [05_meta_cognition](file:///c:/Users/laihuip001/開発（太郎）/dev-rules/constitution/05_meta_cognition.md) | G-5 Meta | M-07, M-08 |
| [06_style](file:///c:/Users/makaron8426/開発(maka)/dev-rules/constitution/06_style.md) | G-6 Style | Code DNA, Type Hints, Naming |
| [07_implementation](file:///c:/Users/makaron8426/開発(maka)/dev-rules/constitution/07_implementation.md) | G-7 Constructor | M-29〜M-34: Read-Before-Write, TDD強制, Termux First |

> *M-19 (Container First) is **Phase 2 only** — suspended during Termux development.

---

## ⚙️ Optimizations Applied

- YAML frontmatter (`id:`, `layer:`)
- XML → Markdown flattening
- Grouped by architectural layer
- Source: 26 files (~2,200 lines) → 7 files (~600 lines)
