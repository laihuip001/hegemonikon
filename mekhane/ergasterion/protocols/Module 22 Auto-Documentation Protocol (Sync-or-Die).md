
---

## 📦 Module 22: Auto-Documentation Protocol (Sync-or-Die)

**目的:**
「コードとドキュメントの乖離（Documentation Drift）」を物理的に防ぐ。
関数のシグネチャやロジックを変更した際、対応するDocstringやREADMEの更新を**「完了の定義（Definition of Done）」**に含める。

**技術的アプローチ:**
コード生成時、変更箇所に対応するドキュメント（インラインコメント、Docstring、Markdownファイル）を特定し、**「コードの変更」と「ドキュメントの変更」をセットで出力**させます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Auto_Documentation_Protocol" priority="MEDIUM">
    <definition>
        Documentation is not an afterthought. It is a compiled dependency of the code.
        Code and Documentation must be updated atomically.
        Changing logic without updating the corresponding documentation is a build failure.
    </definition>

    <sync_targets>
        <target type="Docstrings">
            Function/Class headers (e.g., Python Docstrings, JSDoc).
            *Rule:* Must update `@param`, `@return`, and description if logic changes.
        </target>
        <target type="README">
            Usage examples in `README.md`.
            *Rule:* If API signature changes, the example code in README must be updated.
        </target>
        <target type="ADR">
            Architecture Decision Records for major structural changes.
        </target>
    </sync_targets>

    <enforcement_logic>
        <trigger>Modification of any function signature, return type, or business logic.</trigger>
        <process>
            1. IMPLEMENT the code change.
            2. IDENTIFY affected documentation artifacts.
            3. REWRITE the documentation to match the new reality.
            4. OUTPUT both Code and Docs in the same response.
        </process>
    </enforcement_logic>

    <response_template_docs>
        📚 **Documentation Sync**
        I updated the code, so I must also update the manual.
        
        **1. Code Change:**
        ```python
        def calculate_tax(amount, region="JP"): # Added 'region' param
            """
            Calculates tax based on region.
            Args:
                amount (int): Raw amount.
                region (str): Country code (default: "JP").
            """
            # ...
        ```
        
        **2. README.md Update:**
        ```markdown
        ## Usage
        ```python
        # Old: calculate_tax(1000)
        # New: Support for regions
        calculate_tax(1000, region="US")
        ```
        ```
    </response_template_docs>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **アトミックな更新:**
    *   「コードは直しました。ドキュメントは後でやります」と言った瞬間、そのドキュメントは**「嘘の塊」**になります。このモジュールは、そのタイムラグをゼロにします。
2.  **README駆動の維持:**
    *   Module 02 (Readme Driven Development) で最初に書いたREADMEが、開発が進むにつれて陳腐化するのを防ぎます。APIを変えたら、使い方の例もその場で書き換えさせます。
3.  **型定義としてのDocstring:**
    *   Pythonなどの動的型付け言語では、Docstringこそが仕様書です。引数が増えたのにDocstringが古いままでは、IntelliSense（補完機能）も嘘をつくことになり、開発効率が激減します。

**Status:** Module 22 Ready.
**Next:** リストNo.37「APIモック先行 (Mock First)」を **Module 23** として実装しますか？

**目的:**
「コードとドキュメントの乖離（Documentation Drift）」を物理的に防ぐ。
関数のシグネチャやロジックを変更した際、対応するDocstringやREADMEの更新を**「完了の定義（Definition of Done）」**に含める。

**技術的アプローチ:**
コード生成時、変更箇所に対応するドキュメント（インラインコメント、Docstring、Markdownファイル）を特定し、**「コードの変更」と「ドキュメントの変更」をセットで出力**させます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Auto_Documentation_Protocol" priority="MEDIUM">
    <definition>
        Documentation is not an afterthought. It is a compiled dependency of the code.
        Code and Documentation must be updated atomically.
        Changing logic without updating the corresponding documentation is a build failure.
    </definition>

    <sync_targets>
        <target type="Docstrings">
            Function/Class headers (e.g., Python Docstrings, JSDoc).
            *Rule:* Must update `@param`, `@return`, and description if logic changes.
        </target>
        <target type="README">
            Usage examples in `README.md`.
            *Rule:* If API signature changes, the example code in README must be updated.
        </target>
        <target type="ADR">
            Architecture Decision Records for major structural changes.
        </target>
    </sync_targets>

    <enforcement_logic>
        <trigger>Modification of any function signature, return type, or business logic.</trigger>
        <process>
            1. IMPLEMENT the code change.
            2. IDENTIFY affected documentation artifacts.
            3. REWRITE the documentation to match the new reality.
            4. OUTPUT both Code and Docs in the same response.
        </process>
    </enforcement_logic>

    <response_template_docs>
        📚 **Documentation Sync**
        I updated the code, so I must also update the manual.
        
        **1. Code Change:**
        ```python
        def calculate_tax(amount, region="JP"): # Added 'region' param
            """
            Calculates tax based on region.
            Args:
                amount (int): Raw amount.
                region (str): Country code (default: "JP").
            """
            # ...
        ```
        
        **2. README.md Update:**
        ```markdown
        ## Usage
        ```python
        # Old: calculate_tax(1000)
        # New: Support for regions
        calculate_tax(1000, region="US")
        ```
        ```
    </response_template_docs>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **アトミックな更新:**
    *   「コードは直しました。ドキュメントは後でやります」と言った瞬間、そのドキュメントは**「嘘の塊」**になります。このモジュールは、そのタイムラグをゼロにします。
2.  **README駆動の維持:**
    *   Module 02 (Readme Driven Development) で最初に書いたREADMEが、開発が進むにつれて陳腐化するのを防ぎます。APIを変えたら、使い方の例もその場で書き換えさせます。
3.  **型定義としてのDocstring:**
    *   Pythonなどの動的型付け言語では、Docstringこそが仕様書です。引数が増えたのにDocstringが古いままでは、IntelliSense（補完機能）も嘘をつくことになり、開発効率が激減します。

**Status:** Module 22 Ready.
**Next:** リストNo.37「APIモック先行 (Mock First)」を **Module 23** として実装しますか？