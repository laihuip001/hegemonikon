
---

## 📦 Module 06: Complexity Budget Protocol

**目的:**
「サイクロマティック複雑度（Cyclomatic Complexity）」を制御し、人間が読解可能なコードのみを出力させる。
ネスト地獄（Arrow Code）を禁止し、早期リターン（Guard Clauses）と関数分割を強制する。

**技術的アプローチ:**
コード生成時に「インデントの深さ」と「関数の長さ」を監視します。閾値を超えた場合、AIは自律的に「リファクタリング（Extract Method）」を行わなければなりません。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Complexity_Budget" priority="HIGH">
    <definition>
        Cognitive load is a finite resource. Code must be written for humans to read, not just for machines to execute.
        You have a strict "Complexity Budget" for every function you write.
    </definition>

    <budget_limits>
        <limit type="nesting_depth">
            <max>3</max>
            <description>Maximum indentation levels allowed. Deep nesting indicates poor abstraction.</description>
        </limit>
        <limit type="function_length">
            <max_lines>30</max_lines>
            <description>If a function exceeds 30 lines, it is doing too much. Split it.</description>
        </limit>
        <limit type="argument_count">
            <max>4</max>
            <description>Functions with 5+ arguments require a data object (DTO) or dictionary.</description>
        </limit>
    </budget_limits>

    <refactoring_strategies>
        <strategy name="Guard_Clauses">
            Replace nested `if` statements with early returns.
            (e.g., Instead of `if x: if y: do()`, use `if not x: return; if not y: return; do()`)
        </strategy>
        <strategy name="Extract_Method">
            Identify blocks of code inside a loop or conditional and move them to a private helper function (`_helper_function`).
        </strategy>
    </refactoring_strategies>

    <enforcement_logic>
        <trigger>Generated code exceeds &lt;budget_limits&gt;.</trigger>
        <process>
            1. DETECT violation (e.g., depth = 4).
            2. PAUSE output.
            3. APPLY &lt;refactoring_strategies&gt; internally.
            4. OUTPUT only the refactored, simplified code.
            5. APPEND note: "Refactored for complexity reduction."
        </process>
    </enforcement_logic>

    <response_template_on_refactor>
        📉 **Complexity Budget Enforced**
        Original logic was too complex (Nesting Level: {level}).
        
        **Applied Strategy:** {strategy_name}
        
        ```python
        # Optimized Code (Flat & Readable)
        def process_data(data):
            if not data: return None  # Guard Clause
            # ... linear logic ...
        ```
    </response_template_on_refactor>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **ネストの深さ制限 (Max Nesting 3):**
    *   「ifの中にforがあり、その中にifがある」状態を禁止します。これにより、AIは強制的に**「ガード節（Guard Clauses）」**を使うようになり、コードが驚くほど平坦（Flat）で読みやすくなります。
2.  **引数地獄の回避 (Max Args 4):**
    *   `func(a, b, c, d, e, f)` のような関数は、後で呼び出す時に必ず間違えます。これを禁止し、`func(config_object)` のようにオブジェクトで渡す設計へ誘導します。
3.  **AIへの「自己検閲」:**
    *   このモジュールの肝は、**「出力する前に直させる」**ことです。ユーザーが「読みにくいから直して」と言う手間を省き、最初から洗練されたコードだけが提示される体験を作ります。

**Status:** Module 06 Ready.
**Next:** リストNo.9「異視点の悪魔 (The Devil's Advocate)」を **Module 07** として実装しますか？