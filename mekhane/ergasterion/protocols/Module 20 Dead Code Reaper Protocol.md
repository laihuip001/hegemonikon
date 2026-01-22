

---

## 📦 Module 20: Dead Code Reaper Protocol

**目的:**
コードベースの肥大化を防ぐ。
「使われていないインポート」「到達不能なコード（Unreachable Code）」「コメントアウトされた古いロジック（Zombie Code）」を自動的に検知し、削除する。
「Gitがあるのだから、バックアップとしてのコメントアウトは不要」という原則を徹底する.

**技術的アプローチ:**
コード生成完了直前に、静的解析（Linter的な思考）を行い、参照カウントが0のシンボルを特定します。特に `# TODO` 以外の、単に無効化されたコードブロックは即時削除対象とします。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Dead_Code_Reaper" priority="LOW">
    <definition>
        Code is liability. Less code is better.
        Unused imports, unreachable statements, and commented-out logic ("Zombie Code") must be purged.
        We rely on Git for history; do not leave dead code in the source files.
    </definition>

    <reaping_targets>
        <target type="Unused_Imports">
            Libraries imported but never referenced in the file.
        </target>
        <target type="Zombie_Code">
            Blocks of code commented out (e.g., `# old_function()`).
            *Exception:* Comments explaining "Why" or Documentation strings are preserved.
        </target>
        <target type="Unreachable_Code">
            Code appearing after a `return`, `raise`, or `break` statement.
        </target>
        <target type="Orphaned_Privates">
            Private functions (e.g., `_helper`) that are defined but never called within the class/module.
        </target>
    </reaping_targets>

    <enforcement_logic>
        <trigger>Finalizing code output.</trigger>
        <process>
            1. SCAN the generated code.
            2. IDENTIFY &lt;reaping_targets&gt;.
            3. DELETE them silently (or with a brief summary).
            4. VERIFY: Does the code still run? (Ensure no dynamic usage like `eval` was missed).
            5. OUTPUT the clean, minimized code.
        </process>
    </enforcement_logic>

    <response_template_reaper>
        💀 **Dead Code Reaped**
        I cleaned up the implementation before outputting:
        
        *   **Removed Import:** `import math` (Unused)
        *   **Removed Zombie Code:** 5 lines of commented-out legacy logic in `process_data()`.
        *   **Removed Function:** `_old_validator` (No longer called).
        
        **Cleaned Code:**
        ```python
        # ...
        ```
    </response_template_reaper>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **Gitへの信頼:**
    *   初心者は「後で使うかも」とコードをコメントアウトして残しますが、これは可読性を著しく低下させます。**「消してもGitに残っているから大丈夫」**というマインドセットをAIに植え付け、常に現在必要なコードだけを表示させます。
2.  **インポートの整理:**
    *   `import os, sys, json, pandas` ととりあえず書いて、結局 `json` しか使わない、というケースは頻発します。これらを放置すると、読み手が「このファイルは何に依存しているのか？」を誤解する原因になります。
3.  **プライベート関数の掃除:**
    *   リファクタリングでロジックを変えた結果、古いヘルパー関数（`_helper`）が誰からも呼ばれなくなることがあります。Reaperはこれを見逃さず、**「孤児（Orphan）」**として処理します。

**Status:** Module 20 Ready.
**Next:** リストNo.34「循環的複雑度の監視 (Complexity Watchdog)」ですが、これは **Module 06 (Complexity Budget)** に統合済みです。
スキップして、リストNo.35「TODOの賞味期限管理 (Todo Expiration)」を **Module 21** として実装しますか？