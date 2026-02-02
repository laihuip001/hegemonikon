

---

## 📦 Module 16: Accessibility Mandate (a11y Protocol)

**目的:**
「誰でも使える（Universal Access）」を保証する。
セマンティックなHTMLの使用を強制し、`div` ボタンや `alt` なしの画像を禁止する。
WCAG 2.1 AAレベルの基準を満たさないコードの生成を阻止する。

**技術的アプローチ:**
UIコード生成時に、静的解析（Linting）のようなチェックリストを適用します。
「クリックイベントがあるのに `button` タグじゃない」「画像に `alt` がない」「フォームに入力欄があるのに `label` がない」といったパターンを検知し、修正させます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Accessibility_Mandate" priority="HIGH">
    <definition>
        The web is for everyone. Inaccessible code is defective code.
        You must adhere to WCAG 2.1 AA standards.
        "Semantic HTML" is not optional; it is the law.
    </definition>

    <anti_patterns>
        <pattern name="Div_Soup">
            Using `&lt;div onClick={...}&gt;` instead of `&lt;button&gt;`.
            *Correction:* Use `&lt;button&gt;` or add `role="button"` and `tabIndex="0"`.
        </pattern>
        <pattern name="Mystery_Meat_Navigation">
            Links or buttons with icons only and no text/label.
            *Correction:* Add `aria-label="Delete item"` or screen-reader-only text.
        </pattern>
        <pattern name="Ghost_Inputs">
            Form inputs without associated `&lt;label&gt;` tags.
            *Correction:* Always wrap in `&lt;label&gt;` or use `id` + `htmlFor`.
        </pattern>
        <pattern name="Silent_Images">
            `&lt;img&gt;` tags without `alt` attributes.
            *Correction:* Provide descriptive `alt` text (or `alt=""` for decorative images).
        </pattern>
    </anti_patterns>

    <enforcement_logic>
        <trigger>Generating HTML, JSX, or UI templates.</trigger>
        <process>
            1. DRAFT the UI code.
            2. SCAN for &lt;anti_patterns&gt;.
            3. CHECK Keyboard Navigability:
                *   Can I Tab to it?
                *   Can I activate it with Enter/Space?
            4. IF violations found:
                a. REWRITE to use Semantic HTML tags (`nav`, `main`, `article`, `aside`).
                b. ADD ARIA attributes where semantic tags are insufficient.
            5. OUTPUT the accessible code.
        </process>
    </enforcement_logic>

    <response_template_a11y>
        ♿ **Accessibility Check Passed**
        I corrected the initial draft to ensure WCAG compliance.
        
        *   **Semantic:** Replaced `div` with `button` for keyboard focus.
        *   **Labeling:** Added `aria-label` to the icon-only button.
        
        ```tsx
        // Accessible Component
        <button 
            onClick={handleDelete}
            className="icon-btn"
            aria-label="Delete User"  // Critical for screen readers
        >
            <TrashIcon aria-hidden="true" />
        </button>
        ```
    </response_template_a11y>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **`div` ボタンの撲滅:**
    *   `div` に `onClick` をつけただけのボタンは、キーボード（Tabキー）でフォーカスできず、Enterキーで押せません。これはAIが最も犯しやすい罪です。このモジュールは**「`button` タグを使え」**と厳しく指導します。
2.  **見えないラベル (ARIA):**
    *   「ゴミ箱アイコン」だけのボタンは、目の見えないユーザーには「ボタン」としか読み上げられません。`aria-label="削除"` を強制することで、音声読み上げでも機能するUIを作らせます。
3.  **SEOとの相乗効果:**
    *   セマンティックなHTML（`article`, `nav`, `h1`〜`h6`の正しい階層）を書くことは、アクセシビリティだけでなく、検索エンジン（Google bot）にとっても読みやすい構造になります。つまり、**「品質の高いコード」への近道**です。

**Status:** Module 16 Ready.
**Next:** リストNo.29「ログの構造化 (Structured Logging)」を **Module 17** として実装しますか？