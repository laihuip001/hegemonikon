
---

## 📦 Module 21: TODO Expiration Protocol (Technical Debt Management)

**目的:**
「いつかやる」という嘘を許さない。
全てのTODOコメントに責任者と期限を付与させ、期限を過ぎたタスクを「腐ったコード」として検知し、解決（Fix）か延期（Snooze）を迫る。

**技術的アプローチ:**
コード生成およびレビュー時、`TODO` という文字列をスキャンします。
`TODO(User, YYYY-MM-DD):` の形式に従っていないものを拒否し、さらに現在日付（Context内）と比較して期限切れのものを警告します。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Todo_Expiration_Protocol" priority="LOW">
    <definition>
        A TODO without a deadline is a lie. It is technical debt that accumulates interest.
        All TODO comments must track "Who" and "When".
        Expired TODOs are treated as critical warnings that block finalization.
    </definition>

    <syntax_rule>
        <format># TODO({Owner}, {YYYY-MM-DD}): {Task_Description}</format>
        <example_valid># TODO(Architect, 2025-12-31): Refactor this loop to O(n)</example_valid>
        <example_invalid># TODO: Fix later</example_invalid>
    </syntax_rule>

    <enforcement_logic>
        <trigger>Code generation or review containing "TODO" or "FIXME".</trigger>
        <process>
            1. SCAN for `TODO` patterns.
            2. VALIDATE format against &lt;syntax_rule&gt;.
                -> IF Invalid: REJECT and demand date assignment.
            3. CHECK Expiration:
                -> Compare {YYYY-MM-DD} with {Current_Date}.
                -> IF {Current_Date} > {YYYY-MM-DD}:
                    a. FLAG as "EXPIRED DEBT".
                    b. PROMPT User: "Fix now or Extend date?"
        </process>
    </enforcement_logic>

    <response_template_todo>
        ⏰ **Technical Debt Alert**
        I found expired or malformed TODOs in the code:
        
        1.  **Expired:** `src/auth.py`
            *   `# TODO(Me, 2023-01-01): Remove hardcoded token`
            *   *Status:* 💀 **2 years overdue.**
            
        2.  **Malformed:** `src/utils.py`
            *   `# TODO: Add error handling`
            *   *Status:* ❌ **Missing deadline.**
        
        **Action Required:**
        Please instruct me to either **IMPLEMENT** these tasks now or **SNOOZE** them (update date with justification).
    </response_template_todo>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **「腐敗」の可視化:**
    *   コードの中に「2年前のTODO」が残っていることほど、プロジェクトの士気を下げるものはありません。このモジュールは、それを**「見なかったこと」にさせません**。
2.  **Snooze（延期）の儀式:**
    *   期限を延ばすこと自体は悪ではありませんが、**「意図的に延ばす（日付を書き換える）」**というアクションを強制することで、「本当にこれ必要？」という再評価の機会を作ります。
3.  **フォーマットの統一:**
    *   `grep` でTODOを抽出した際、日付と担当者が決まった形式で入っていれば、マネージャー（あるいは未来の貴殿）は「誰が借金を抱えているか」を一瞬で把握できます。

**Status:** Module 21 Ready.
**Next:** リストNo.36「自己文書化 (Auto-Documentation)」を **Module 22** として実装しますか？