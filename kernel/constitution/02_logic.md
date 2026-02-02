---
id: G-2
layer: Logic Gate (Cognition & Quality)
enforcement_level: L1
---

# G-2: Logic Protocol

> Controls code quality, testing, naming, complexity, and UI structure.

---

## M-04: TDD Protocol (CRITICAL)

**Rule:** Code without tests is a hallucination.

**Workflow:**

1. **Red:** Write failing test first
2. **Green:** Write minimum implementation
3. **Refactor:** Optimize after test passes

**Process:**

1. REFUSE to generate implementation immediately
2. Generate test code first
3. Ask: "Please confirm test fails"
4. Upon confirmation → Generate implementation

---

## M-05: Domain Language (HIGH)

**Rule:** Enforce Ubiquitous Language. Reject generic terms when domain equivalents exist.

**Process:**

1. Scan generated code for generic terms
2. Auto-correct to domain terms
3. Add comment: `# Refactored to match Ubiquitous Language`

**Example Mappings:** *(Customize per project)*

- `User` → `Operator`
- `Item` → `Cargo`
- `Delete` → `Archive`

---

## M-06: Complexity Budget (HIGH)

**Limits:**

- Max nesting depth: **3**
- Max function lines: **30**
- Max arguments: **4** (else use DTO)

**Strategies:**

- **Guard Clauses:** Replace nested `if` with early returns
- **Extract Method:** Move logic blocks to `_helper` functions

---

## M-15: Atomic Design (HIGH)

**Hierarchy:**

- **Atoms:** Buttons, Inputs (no logic)
- **Molecules:** SearchBox = Input + Button (local state only)
- **Organisms:** Complex sections (business logic allowed)

**Constraints:**

- Max **120 lines** per UI component
- Separate logic (Hooks) from view (JSX)

---

## M-16: Accessibility (HIGH)

**WCAG 2.1 AA Required.**

**Anti-Patterns:**

- `<div onClick>` → Use `<button>`
- Icons without labels → Add `aria-label`
- `<input>` without `<label>` → Associate via `id`/`htmlFor`
- `<img>` without `alt` → Add descriptive text

---

## M-20: Dead Code Reaper (LOW)

**Targets:**

- Unused imports
- Zombie code (commented-out logic)
- Unreachable code (after `return`)
- Orphaned private functions

**Action:** Delete silently, rely on Git for history.

---

## M-21: TODO Expiration (LOW)

**Format Required:** `# TODO(Owner, YYYY-MM-DD): Task`

**Process:**

1. Scan for `TODO` patterns
2. Reject invalid format
3. Flag expired TODOs as "Critical Debt"
4. Prompt: "Fix now or Snooze with new date?"
