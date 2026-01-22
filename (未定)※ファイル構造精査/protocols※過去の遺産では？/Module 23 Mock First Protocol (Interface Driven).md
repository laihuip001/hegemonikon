
---

## 📦 Module 23: Mock First Protocol (Interface Driven)

**目的:**
バックエンドとフロントエンドの並列開発を可能にする。
複雑なロジックを実装する前に、APIの**「契約（Contract = JSON Schema）」**を確定させる。
「作ってみたけど、画面に必要なデータが足りなかった」という手戻りを防ぐ。

**技術的アプローチ:**
APIエンドポイントの実装を求められた際、データベース接続や計算ロジックを書くことを一時的に禁止します。
代わりに、固定のJSONデータを返すだけの**「ダミー関数」**を即座に作成し、ユーザー（またはフロントエンド担当）の承認を得ます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Mock_First_Protocol" priority="HIGH">
    <definition>
        The Interface (API Contract) is more important than the Implementation.
        You must define "What comes out" before defining "How it works".
        Do not write backend logic until the JSON response structure is approved via a Mock.
    </definition>

    <workflow_steps>
        <step sequence="1">
            **Design the Contract:** Define the JSON response structure based on UI requirements.
        </step>
        <step sequence="2">
            **Implement the Mock:** Write an endpoint that returns static, hardcoded data (or uses a faker library).
        </step>
        <step sequence="3">
            **Verify:** Ask the user/frontend if this JSON structure satisfies the UI needs.
        </step>
        <step sequence="4">
            **Real Implementation:** Only AFTER approval, replace the mock with DB queries.
        </step>
    </workflow_steps>

    <enforcement_logic>
        <trigger>User requests a new API endpoint or Backend feature.</trigger>
        <process>
            1. PAUSE real implementation.
            2. GENERATE a Mock Response (JSON).
            3. OUTPUT the Mock Endpoint code.
            4. ASK: "Does this JSON shape work for the Frontend?"
        </process>
    </enforcement_logic>

    <response_template_mock>
        🎭 **Mock First Strategy**
        Before connecting to the database, let's agree on the API structure.
        
        **Proposed Response (JSON):**
        ```json
        {
          "user_id": "u_123",
          "balance": 5000,
          "recent_transactions": [
            {"id": 1, "amount": -500, "label": "Coffee"}
          ]
        }
        ```
        
        **Mock Implementation (FastAPI Example):**
        ```python
        @app.get("/api/dashboard")
        async def get_dashboard_mock():
            # TODO: Replace with real DB call after frontend approval
            return {
                "user_id": "u_123",
                "balance": 5000,
                "recent_transactions": [...]
            }
        ```
        *Is this structure sufficient for the UI?*
    </response_template_mock>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **契約（Contract）の早期締結:**
    *   API開発で最も揉めるのは「キー名が違う」「ネストが深すぎる」「欲しいデータがない」です。モック先行なら、コードを1行も書く前にこの議論を終わらせることができます。
2.  **フロントエンドのブロック解除:**
    *   モックさえあれば、フロントエンド担当（あるいは貴殿のフロントエンド人格）は、バックエンドの完成を待たずにUIを作り込めます。これが**「爆速開発」**の正体です。
3.  **テストデータとしての再利用:**
    *   ここで作ったモックデータは、捨てずにそのまま「ユニットテストの期待値（Fixture）」や「ストーリーブックのデータ」として再利用できます。無駄がありません。

**Status:** Module 23 Ready.
**Next:** リストNo.38「パフォーマンス予算 (Performance Budget)」を **Module 24** として実装しますか？