
---

## 📦 Module 17: Structured Logging Protocol

**目的:**
「人間が読むためのログ（Unstructured Text）」を禁止し、「機械が読むためのログ（Structured JSON）」を強制する。
デバッグ効率を最大化するため、全てのログに「コンテキスト（User ID, Request ID, 変数値）」を自動的に付与させる。

**技術的アプローチ:**
`print()` や `console.log("text")` の使用を検知し、構造化ロガー（Pythonなら `structlog` や `logging` のJSONフォーマッタ、JSなら `pino` や `winston`）への置き換えを指示します。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Structured_Logging_Protocol" priority="MEDIUM">
    <definition>
        Logs are data, not text.
        Unstructured logging (e.g., `print` statements) is strictly PROHIBITED in production code.
        All logs must be emitted as JSON objects to allow for automated parsing and alerting.
    </definition>

    <log_schema>
        <field name="level">Severity (INFO, WARN, ERROR, DEBUG)</field>
        <field name="timestamp">ISO 8601 format</field>
        <field name="message">Human-readable summary</field>
        <field name="context">Dictionary containing relevant variables (e.g., `user_id`, `order_id`)</field>
        <field name="trace_id">Correlation ID for distributed tracing</field>
    </log_schema>

    <forbidden_practices>
        <practice>Using `print()` or `console.log()` for anything other than local debugging scripts.</practice>
        <practice>String concatenation in logs (e.g., `log.info("User " + id + " failed")`).</practice>
        <practice>Logging sensitive data (Passwords, PII) in plain text.</practice>
    </forbidden_practices>

    <enforcement_logic>
        <trigger>Code generation involving logging or error handling.</trigger>
        <process>
            1. IDENTIFY the logging mechanism.
            2. IF `print` is used -> REJECT and replace with Logger.
            3. IF string interpolation is used -> REJECT and replace with Context Dictionary.
            4. ENSURE output format is JSON-compatible.
        </process>
    </enforcement_logic>

    <response_template_logging>
        📝 **Structured Logging Enforced**
        I replaced the `print` statements with a structured logger.
        
        **Bad:**
        ```python
        print(f"Failed to process order {order_id} for user {user_id}")
        ```
        
        **Good (Structured):**
        ```python
        logger.error("order_processing_failed", extra={
            "order_id": order_id,
            "user_id": user_id,
            "error_code": "PAYMENT_DECLINED"
        })
        # Output: {"level": "error", "msg": "order_processing_failed", "order_id": 123, ...}
        ```
    </response_template_logging>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **Grepからの解放:**
    *   テキストログの場合、「エラー」を探すのに正規表現と格闘する必要があります。JSONログなら `log.level == "ERROR" && log.user_id == "123"` のように、**SQL感覚でログをクエリ**できます。
2.  **コンテキストの分離:**
    *   `"User 123 error"` という文字列にしてしまうと、後で「ユーザーID」だけを抽出するのが困難です。`message="User error", context={"id": 123}` と分けることで、データとしての価値が生まれます。
3.  **`print` の撲滅:**
    *   `print` は標準出力に吐くだけで、ログレベル（重要度）の概念がありません。本番環境で「デバッグログ」が大量に流れてディスクを圧迫する事故を防ぐため、ロガーの使用を徹底させます。

**Status:** Module 17 Ready.
**Next:** リストNo.30「機能のスイッチ化 (Feature Flags)」を **Module 18** として実装しますか？