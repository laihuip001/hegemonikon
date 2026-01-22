
---

## 📦 Module 02: Directory Topology Lock

**目的:**
プロジェクトのディレクトリ構造（トポロジー）を固定し、エージェントによる無許可の「フォルダ作成」「ファイル移動/リネーム」を禁止する。

**技術的アプローチ:**
ファイル操作を行う前に、その操作が「既存の構造的整合性」を保っているかを判定させます。新しいディレクトリが必要な場合は、コードを書く前に**「構造変更の提案（Topology Amendment）」**を提出させます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Directory_Topology_Lock" priority="HIGH">
    <definition>
        The project's directory structure is the physical manifestation of its architecture.
        Arbitrary creation of directories or renaming of files increases entropy and is strictly PROHIBITED.
    </definition>

    <constraints>
        <rule id="no_shadow_structures">
            Do NOT create synonymous directories (e.g., do not create `utils/` if `common/` or `helpers/` already exists).
            Always check the existing file tree before deciding where to place a file.
        </rule>
        <rule id="immutable_paths">
            Do NOT move or rename existing files unless the user explicitly requests a "Refactor".
            Broken imports caused by unauthorized moves are considered a critical failure.
        </rule>
        <rule id="schema_first">
            If a NEW directory is absolutely necessary, you must propose it via a "Topology Amendment" BEFORE generating any code.
        </rule>
    </constraints>

    <enforcement_logic>
        <trigger>Intent to run `mkdir`, create new file path, or `mv`.</trigger>
        <process>
            1. SCAN existing directory structure.
            2. EVALUATE: Does the new path fit into the existing pattern?
            3. IF (New Directory) OR (Rename):
                a. PAUSE execution.
                b. OUTPUT: "Topology Change Proposal".
                c. WAIT for user confirmation.
            4. ELSE (Existing Directory):
                a. Proceed.
        </process>
    </enforcement_logic>

    <response_template_on_proposal>
        🏗️ **Topology Amendment Required**
        I intend to create a new directory structure:
        `{proposed_path}`
        
        **Reason:** {justification}
        **Impact:** This will affect {related_modules}.
        
        *Approve? [Y/N]*
    </response_template_on_proposal>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **エントロピーの抑制 (`no_shadow_structures`):**
    *   LLMは文脈によって `services`, `providers`, `managers` などを揺らぎで使い分けようとします。これを「既存のものを使え」と強制することで、プロジェクトの一貫性を保ちます。
2.  **インポートエラーの根絶 (`immutable_paths`):**
    *   「ファイル名を変える」という行為が、どれほど依存関係を破壊するかをAIに認識させます。リファクタリングは「コード生成」とは別の「重大なイベント」として扱わせます。
3.  **提案プロセス (`Topology Amendment`):**
    *   勝手にフォルダを掘らせず、一度人間に「ここに掘っていい？」と聞かせることで、ゴミ屋敷化を未然に防ぎます。

**Status:** Module 02 Ready.
**Next:** No.3 Dependency Quarantine (依存関係の検疫所) へ移行しますか？