# Security Specialist Review (Krisis)

**Domain Focus:** 認証、権限、インジェクション攻撃
**Cognitive Lens:** Is the judgment correct?

## Findings

### 1. SQL Injection in Library Code
- **Severity:** Major
- **Location:** `mekhane/anamnesis/index.py:165` (approximate, `get_by_primary_key` method)
- **Issue:** The `get_by_primary_key` method constructs a LanceDB query using F-string interpolation with the `primary_key` argument: `f"primary_key = '{primary_key}'"`. This allows SQL-like injection if `primary_key` contains quotes or logic operators (e.g., `' OR '1'='1`). While this method is not currently used by the MCP server, it is a vulnerable public method in the library. The judgment that string interpolation is safe here is incorrect.
- **Recommendation:** Validate `primary_key` format (e.g., alphanumeric only) or use parameterized queries if supported by the LanceDB Python SDK.

### 2. Insecure Credential Display in Test Logic
- **Severity:** Minor
- **Location:** `mekhane/symploke/jules_client.py:204`
- **Issue:** The CLI test block attempts to mask the API key using `api_key[:8]...{api_key[-4:]}`. If the API key is short (less than 12 characters), this logic will display the full key twice (e.g., "short...short"). The judgment that this logic always safely masks the key is incorrect for edge cases.
- **Recommendation:** Add a length check before masking. Only display masked key if length > 12, otherwise display `(redacted)`.

### 3. Prompt Injection Risk in Generator
- **Severity:** Info
- **Location:** `mcp/prompt_lang_mcp_server.py:108`
- **Issue:** The `generate_prompt_lang` function injects the raw `requirements` string into the `@goal:` section of the generated code. If `requirements` contains Prompt-Lang directives (e.g., `@role:`), it could alter the structure of the generated skill. The judgment that the input text can be directly embedded is risky.
- **Recommendation:** Sanitize the input or use a block scalar format (e.g., indented block or quoted string) to encapsulate the requirements safely.
