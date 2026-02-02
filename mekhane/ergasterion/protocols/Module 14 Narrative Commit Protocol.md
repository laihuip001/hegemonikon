
---

## 📦 Module 14: Narrative Commit Protocol

**目的:**
Gitのコミットログを、単なる変更履歴ではなく「意思決定のドキュメント」に昇華させる。
"fix bug" のような無味乾燥なメッセージを禁止し、**Context（背景）、Problem（問題）、Solution（解決策）**を含む構造化された物語を強制する。

**技術的アプローチ:**
コミットメッセージ生成時に、`git diff` の内容だけでなく、直前の「会話のコンテキスト（なぜその修正に至ったか）」を統合します。
Conventional Commits仕様（`feat:`, `fix:`）をベースにしつつ、Body部分に「思考の痕跡」を残させます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Narrative_Commit_Protocol" priority="MEDIUM">
    <definition>
        A commit message is a letter to the future maintainer.
        Lazy messages like "fix bug" or "update" are strictly PROHIBITED.
        You must document the "Why" and the "How", not just the "What".
    </definition>

    <structure_template>
        <header>
            {type}({scope}): {imperative_summary_under_50_chars}
        </header>
        <body>
            **Context:**
            {Why was this change necessary? What was the pain point?}

            **Solution:**
            {Technical explanation of the change. e.g., "Switched from List to Set for O(1) lookup."}

            **Alternatives Considered:**
            {What did we reject? e.g., "Considered Redis but chose local cache for simplicity."}
        </body>
        <footer>
            Refs: #{issue_number}
        </footer>
    </structure_template>

    <types_allowed>
        <type name="feat">New feature</type>
        <type name="fix">Bug fix</type>
        <type name="refactor">Code change that neither fixes a bug nor adds a feature</type>
        <type name="perf">Code change that improves performance</type>
        <type name="chore">Maintenance, dependencies, build tools</type>
        <type name="docs">Documentation only changes</type>
    </types_allowed>

    <enforcement_logic>
        <trigger>User asks to generate a commit message or perform a git commit.</trigger>
        <process>
            1. ANALYZE the `git diff` or the code changes made.
            2. RECALL the conversation context (the "Why").
            3. DRAFT the message using &lt;structure_template&gt;.
            4. CHECK against Anti-Patterns:
                *   Is the summary vague? ("Updated code") -> REJECT.
                *   Is the body empty? -> REJECT.
            5. OUTPUT the narrative commit message.
        </process>
    </enforcement_logic>

    <response_template_commit>
        📝 **Narrative Commit Generated**
        
        ```text
        fix(auth): resolve race condition in token refresh
        
        **Context:**
        Users were getting logged out randomly during high load. The token refresh logic was not atomic.
        
        **Solution:**
        Implemented a mutex lock around the refresh token endpoint. Added a 5-second grace period for overlapping requests.
        
        **Alternatives Considered:**
        Considered using optimistic locking in DB, but in-memory mutex is sufficient for current single-instance deployment.
        
        Refs: #42
        ```
    </response_template_commit>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **「なぜ（Why）」の保存:**
    *   コードを見れば「何（What）」が変わったかは分かりますが、「なぜ」はコードには残りません。このモジュールは、**「Alternatives Considered（検討したが採用しなかった案）」**を書かせることで、未来の「なぜRedisを使わなかったんだ！」という批判に対する防御策を残します。
2.  **コンテキストの結晶化:**
    *   AIとの長い対話の末に生まれたコードは、その対話自体が重要なドキュメントです。コミットメッセージにその要約を含めることで、Gitログを見るだけで**「開発のドラマ」**を追体験できるようにします。
3.  **検索性の向上:**
    *   `fix: resolve race condition` のように具体的に書かせることで、後で `git log --grep="race condition"` と検索した時に、即座に該当箇所を見つけられるようになります。

**Status:** Module 14 Ready.
**Next:** これで貴殿のSelectionリスト（No.1〜17）の実装が完了しました。
残りの **No.25, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40** についても、同様に実装を続けますか？
それとも、一度ここで区切り、**「統合（Integration）」**のステップへ進みますか？