
---

## 📦 Module 18: Feature Flag Protocol (Toggle Architecture)

**目的:**
「デプロイ（Deployment）」と「リリース（Release）」を分離する。
新しい機能や実験的な変更を、Feature Flag（トグルスイッチ）でラップし、デフォルトでは「無効（OFF）」の状態で実装させる。
緊急時に即座に機能を停止できる「キルスイッチ」としての役割を持たせる。

**技術的アプローチ:**
「新機能を追加して」という指示に対し、AIは直接ロジックを書き換えるのではなく、必ず `if (feature_flags.is_enabled("NEW_FEATURE")): ... else: ...` という構造でコードを生成します。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Feature_Flag_Protocol" priority="HIGH">
    <definition>
        Deployment is not Release. Code must be mergeable even if incomplete or risky.
        All new non-trivial features must be wrapped in a Feature Flag.
        This allows for "Dark Launches" and instant "Kill Switches" in case of bugs.
    </definition>

    <implementation_rules>
        <rule id="wrap_logic">
            Do NOT replace existing logic directly.
            Wrap the new logic in a conditional block checking the flag status.
        </rule>
        <rule id="default_off">
            New flags must default to `FALSE` (Disabled) to ensure safety during deployment.
        </rule>
        <rule id="fallback_required">
            Always provide an `else` block (Fallback) that executes the old, stable behavior.
        </rule>
        <rule id="naming_convention">
            Flag keys must be descriptive and snake_case (e.g., `enable_new_checkout_flow`).
        </rule>
    </implementation_rules>

    <enforcement_logic>
        <trigger>User requests a "New Feature", "Experimental Change", or "Major Refactor".</trigger>
        <process>
            1. DEFINE a unique Feature Flag Key.
            2. SCAFFOLD the conditional structure:
                `if flags.get("KEY"): [New Logic] else: [Old Logic]`
            3. IMPLEMENT the new logic inside the `if` block.
            4. ENSURE the code runs safely even if the flag is missing (graceful failure).
        </process>
    </enforcement_logic>

    <response_template_feature_flag>
        🚩 **Feature Flag Implemented**
        I have wrapped the new logic behind a flag to prevent regression.
        
        **Flag Key:** `enable_v2_search_algorithm`
        **Default:** `False` (OFF)
        
        ```python
        def search_products(query):
            # Safety Switch
            if feature_flags.is_enabled("enable_v2_search_algorithm"):
                return _search_v2_vector_db(query)  # New (Risky)
            else:
                return _search_v1_keyword(query)    # Old (Safe)
        ```
        
        *To test this, please set `ENABLE_V2_SEARCH_ALGORITHM=true` in your environment.*
    </response_template_feature_flag>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **「キルスイッチ」の確保:**
    *   AIが書いたコードは、特定の条件下で暴走する可能性があります。Feature Flagがあれば、深夜3時にバグが見つかっても、**コードを修正・デプロイし直すことなく、環境変数を変えるだけで鎮火**できます。
2.  **トランクベース開発の促進:**
    *   「完成するまでマージできない」という古い慣習を捨てられます。「未完成だけどフラグで隠されているからマージできる」状態を作ることで、開発スピードと統合頻度を劇的に向上させます。
3.  **A/Bテストへの布石:**
    *   この構造にしておけば、「ユーザーの50%だけに新機能を見せる」といったA/Bテストが簡単に実現できます。単なる安全策以上の、**「攻めの開発」**への第一歩です。

**Status:** Module 18 Ready.
**Next:** リストNo.31「コンテナ化の義務 (Docker First)」を **Module 19** として実装しますか？