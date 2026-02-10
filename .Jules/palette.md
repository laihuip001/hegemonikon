## 2025-02-28 - Missing Form Labels Pattern
**Learning:** Many form inputs in the application (Search, Postcheck forms) rely solely on placeholders or nearby text without explicit programmatic association (missing `for` attribute or `aria-label`).
**Action:** Always check for unassociated labels in form-heavy views like Postcheck and add `.sr-only` labels for search bars that rely on placeholders.
