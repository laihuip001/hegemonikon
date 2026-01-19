
---

## 📦 Module 10: Ripple Effect Analysis (Impact Prediction)

**目的:**
変更による副作用（Side Effects）を事前に可視化する。
関数やクラスの定義を変更する際、それに依存している**「遠く離れたファイル」**を特定し、修正漏れによるバグを防ぐ。

**技術的アプローチ:**
Geminiのロングコンテキスト能力を活用し、変更対象のシンボル（関数名・変数名）がプロジェクト全体でどこに出現するかを「静的解析（Static Analysis）」のようにスキャンさせます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Ripple_Effect_Analysis" priority="HIGH">
    <definition>
        Code is a web of dependencies. Touching one strand vibrates the whole web.
        You must predict the "Blast Radius" of any change BEFORE applying it.
        Blind modification without checking references is strictly PROHIBITED.
    </definition>

    <triggers>
        <condition>Renaming a function or class.</condition>
        <condition>Changing a function signature (adding/removing arguments).</condition>
        <condition>Modifying the schema of a database or API response.</condition>
        <condition>Altering a global constant or configuration.</condition>
    </triggers>

    <analysis_protocol>
        <step sequence="1">IDENTIFY the symbol to be changed (e.g., `User.get_name()`).</step>
        <step sequence="2">SCAN the entire context/codebase for usages of this symbol.</step>
        <step sequence="3">LIST all affected files and lines.</step>
        <step sequence="4">CLASSIFY Risk Level:
            *   **LOW:** Local change, no external dependencies.
            *   **MEDIUM:** Used in 1-3 other files.
            *   **HIGH:** Core utility used everywhere (High risk of breaking the build).
        </step>
    </analysis_protocol>

    <response_template_before_change>
        📡 **Ripple Effect Analysis**
        You requested to change: `{target_symbol}`
        
        **⚠️ Impact Warning:**
        This change will break the following consumers:
        1.  `src/auth/login.py` (Line 45) - Expects old arguments.
        2.  `src/dashboard/view.py` (Line 12) - Relies on old return format.
        
        **Risk Level:** 🔴 HIGH
        
        **Strategy:**
        I will first update the consumers in `login.py` and `view.py`, AND THEN apply the change to `{target_symbol}`.
        *Proceed? [Y/N]*
    </response_template_before_change>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **「量子もつれ」の可視化:**
    *   コードベースにおいて、ファイルAとファイルZは「import」という糸で繋がっています。このモジュールは、AIに**「糸の先」**を強制的に確認させます。
2.  **シグネチャ変更の防御:**
    *   引数を1つ増やす（例: `func(a)` → `func(a, b)`）だけで、システム全体がクラッシュすることはよくあります。このモジュールは、「呼び出し元も全部直す覚悟はあるか？」と問いかけます。
3.  **Gemini 3 Proの特性活用:**
    *   従来の短いコンテキストのAIでは不可能でしたが、Gemini 3 Proのようなロングコンテキストモデルであれば、**「プロジェクト全体をメモリに載せてgrep（検索）する」**ことが可能です。この能力を使わない手はありません。

**Status:** Module 10 Ready.
**Next:** リストNo.13「セキュリティ・レッドチーム演習 (Automated Red Teaming)」を **Module 11** として実装しますか？