
---

## 📦 Module 05: Domain Language Enforcement (Ubiquitous Language)

**目的:**
コード内の変数名、クラス名、コメントにおいて、プロジェクト固有の「ユビキタス言語（共通言語）」の使用を強制する。
汎用的な用語（Generic Terms）の使用を検知し、ドメイン用語への置換を自動化する。

**技術的アプローチ:**
`<vocabulary>` タグ内で「禁止用語」と「正解用語」のマッピングを定義します。コード生成時にこの辞書をルックアップさせ、違反があればリファクタリングを強制します。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。
※ `<vocabulary>` の中身は、貴殿のプロジェクトに合わせて書き換えてください。

```xml
<module name="Domain_Language_Enforcement" priority="HIGH">
    <definition>
        To maintain semantic consistency, you must strictly adhere to the project's "Ubiquitous Language".
        Generic programming terms are forbidden when a specific domain term exists.
        Code is not just logic; it is a description of the domain model.
    </definition>

    <vocabulary>
        <!-- Define the mapping: "Generic Term" -> "Domain Term" -->
        <!-- Example for a Logistics System -->
        <term generic="User" domain="Operator" />
        <term generic="Item" domain="Cargo" />
        <term generic="Send" domain="Dispatch" />
        <term generic="Delete" domain="Archive" /> <!-- Soft delete policy -->
        
        <!-- Example for a Creative AI System -->
        <term generic="Prompt" domain="Incantation" />
        <term generic="Output" domain="Artifact" />
    </vocabulary>

    <naming_conventions>
        <rule>Variable names must reflect the Domain Term (e.g., `current_operator` NOT `current_user`).</rule>
        <rule>Database tables must match the Domain Term pluralized (e.g., `cargoes` NOT `items`).</rule>
        <rule>Comments must use the Domain Term to explain logic.</rule>
    </naming_conventions>

    <enforcement_logic>
        <trigger>Code generation containing generic terms defined in &lt;vocabulary&gt;.</trigger>
        <process>
            1. SCAN generated code for "Generic Terms".
            2. IF found:
                a. STOP output.
                b. AUTO-CORRECT to "Domain Term".
                c. Add a comment: `# Refactored to match Ubiquitous Language`.
        </process>
    </enforcement_logic>

    <response_template_on_violation>
        📝 **Language Correction Applied**
        I detected generic terms. Aligning with the Domain Dictionary:
        
        *   `User` -> `Operator`
        *   `Item` -> `Cargo`
        
        **Revised Code:**
        ```python
        def dispatch_cargo(operator_id: int, cargo_list: list[Cargo]):
            # ...
        ```
    </response_template_on_violation>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **認知の矯正 (`generic` -> `domain`):**
    *   単なる置換ではなく、AIの「世界観」を書き換えます。例えば「削除（Delete）」を禁止し「アーカイブ（Archive）」と定義することで、物理削除によるデータ消失事故を、言葉のレベルで防ぎます。
2.  **自己文書化の促進:**
    *   コード自体が仕様書になります。`process_data(data)` よりも `dispatch_cargo(cargo)` の方が、何をしているか一目瞭然であり、将来のメンテナンスコストが激減します。
3.  **コンテキストロスト対策:**
    *   会話が長くなるとAIは汎用用語に戻りがちですが、このモジュールが常駐することで、常に「我々の言葉」で話すよう圧力をかけ続けます。

**Status:** Module 05 Ready.
**Next:** リストNo.8「複雑性予算の管理」を **Module 06** として実装しますか？