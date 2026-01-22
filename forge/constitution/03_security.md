---
id: G-3
layer: Shield (Robustness & Security)
enforcement_level: L1
---

# G-3: Security Protocol

> Controls testing quality, security audits, resilience, API contracts, and performance.

---

## M-09: Mutation Testing (ADVANCED)

**Rule:** Passing tests provide false confidence. Verify tests by sabotaging code.

**Mutant Types:**

- Arithmetic Inversion: `+` → `-`
- Condition Flip: `>` → `>=`
- Return Sabotage: Force `None`/`False`
- Statement Deletion

**Outcome:**

- Test fails → Mutant killed ✅
- Test passes → Test is weak ❌ → Rewrite immediately

---

## M-11: Red Teaming (CRITICAL)

**Rule:** Assume Breach. Every input is malicious until sanitized.

**Attack Vectors:**

- **SQLi:** Never use f-strings for queries. Use parameterized (`?`)
- **XSS:** Always escape output or use safe frameworks
- **IDOR:** Verify ownership (`resource.owner_id == current_user.id`)
- **Secrets:** Scan for hardcoded keys

**Process:**

1. Generate draft code
2. Activate Red Team persona
3. Attack with vectors
4. Patch if breach succeeds

---

## M-12: Chaos Monkey (HIGH)

**Rule:** Assume every external call will fail.

**Chaos Scenarios:**

- **Timeout:** Implement `timeout` settings
- **Rate Limit 429:** Use Exponential Backoff (1s, 2s, 4s...)
- **Malformed Data:** Validate with Pydantic/Zod
- **Service Down 500:** Graceful Degradation (cached/error fallback)

**Code without error handling is rejected.**

---

## M-23: Mock First (HIGH)

**Rule:** Define "What comes out" before "How it works".

**Workflow:**

1. Design JSON Contract from UI needs
2. Implement mock endpoint (static data)
3. Get approval from frontend/user
4. Replace mock with real DB logic

---

## M-24: Performance Budget (HIGH)

**Limits:**

- Time Complexity: Max **O(n log n)**
- No N+1 Queries
- No `SELECT *`
- Payload Max **100KB** (paginate)

**Process:**

1. Draft solution
2. Estimate Big O
3. If O(n²) → Reject and optimize (Hash Map, Set, Batch)
4. Output with complexity comment
