
---

## 📦 Module 24: Performance Budget Protocol

**目的:**
「機能すればいい」という考えを捨て、非機能要件（速度・効率）を最初から満たすコードを書かせる。
計算量（Big O Notation）とI/Oコストに対する意識を強制し、スケーラビリティのない実装を未然に防ぐ。

**技術的アプローチ:**
ループ処理やデータベース操作を含むコードを生成する際、必ず**「計算量（Time Complexity）」**を自己申告させます。
また、N+1問題やフルスキャン（全件検索）などの「パフォーマンス・アンチパターン」を静的解析で検知します。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Performance_Budget_Protocol" priority="HIGH">
    <definition>
        Performance is a feature. Latency causes user churn.
        You must adhere to strict resource budgets.
        Implementations that exceed these budgets are considered "Bugs" even if they produce the correct output.
    </definition>

    <budgets>
        <limit type="Time_Complexity">
            <max>O(n log n)</max>
            <description>O(n^2) or worse is FORBIDDEN for any dataset > 100 items.</description>
        </limit>
        <limit type="Database_Queries">
            <rule>NO "N+1" Queries.</rule>
            <rule>NO `SELECT *` (Select only needed columns).</rule>
            <rule>Indices MUST be defined for filter columns.</rule>
        </limit>
        <limit type="Payload_Size">
            <max>100KB</max>
            <description>API responses must be paginated. Never return "All Items".</description>
        </limit>
    </budgets>

    <enforcement_logic>
        <trigger>Code generation involving Loops, Sorting, or Database Access.</trigger>
        <process>
            1. DRAFT the solution.
            2. ESTIMATE Big O Complexity (Time & Space).
            3. CHECK against &lt;budgets&gt;.
            4. IF violation (e.g., O(n^2)):
                a. REJECT draft.
                b. OPTIMIZE (e.g., use Hash Map, Set, or Batch Query).
            5. OUTPUT the optimized code with complexity analysis comment.
        </process>
    </enforcement_logic>

    <response_template_perf>
        ⚡ **Performance Budget Check**
        
        *   **Initial Idea:** Nested loop to find duplicates. -> **O(n^2)** (Too Slow)
        *   **Optimization:** Used a Hash Set for lookups. -> **O(n)** (Approved)
        
        ```python
        def find_duplicates(items):
            seen = set()
            duplicates = []
            # O(n) complexity
            for item in items:
                if item in seen:
                    duplicates.append(item)
                else:
                    seen.add(item)
            return duplicates
        ```
    </response_template_perf>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **`n=10` の罠:**
    *   AIはサンプルコードを書く時、無意識に「データは数個」と仮定します。しかし本番環境ではデータは数万件になります。このモジュールは、常に**「n=1,000,000」**を想定してコードを書くよう強制します。
2.  **N+1問題の根絶:**
    *   ORM（DjangoやRailsなど）を使うと、AIは簡単にN+1問題（1回のリスト取得のために、N回の追加クエリを発行する）を引き起こします。これを「禁止事項」として明記することで、`select_related` や `preload` の使用を促します。
3.  **ページネーションの義務化:**
    *   「全データを取得するAPI」は、サービスダウンの主犯です。`Payload Size` 制限により、最初からページネーション（`limit`, `offset`）を実装させ、サーバーを守ります。

**Status:** Module 24 Ready.
**Next:** リストNo.39「YAGNIの守護神 (You Aren't Gonna Need It)」ですが、これは **Module 06 (Complexity Budget)** の一部として既に組み込まれています。
スキップして、リストNo.40「ロールバック・プラン (Undo Strategy)」を **Module 25 (Final Module)** として実装しますか？