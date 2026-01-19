
---

## 📦 Module 15: Atomic Design Protocol (UI Componentization)

**目的:**
巨大なモノリシックUI（God Components）の作成を禁止する。
Atomic Designの原則（Atoms, Molecules, Organisms）に基づき、UIを最小単位の部品に分割して実装させる。
「ロジック（Hooks）」と「見た目（View）」の分離を強制する。

**技術的アプローチ:**
UIコンポーネントのコード生成時、行数が閾値（例: 100行）を超えたり、複数の責任（ボタン定義とフォーム送信ロジックなど）が混在している場合、強制的にファイルを分割させます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Atomic_Design_Protocol" priority="HIGH">
    <definition>
        Monolithic UI components are technical debt.
        You must adhere to "Atomic Design" principles.
        Build small, reusable components first, then assemble them.
    </definition>

    <component_hierarchy>
        <level name="Atoms">
            Basic building blocks (Buttons, Inputs, Labels, Icons).
            *Rule:* Must be pure functional components with NO business logic.
        </level>
        <level name="Molecules">
            Groups of atoms (SearchBox = Input + Button).
            *Rule:* Can handle local state, but no global side effects.
        </level>
        <level name="Organisms">
            Complex sections (Header, ProductList).
            *Rule:* Can interact with business logic/services.
        </level>
        <level name="Templates_Pages">
            Layouts and specific views.
        </level>
    </component_hierarchy>

    <constraints>
        <rule id="max_lines_per_component">
            A single UI component file should NOT exceed 120 lines.
            If it does, extract sub-components immediately.
        </rule>
        <rule id="separation_of_concerns">
            Do NOT mix complex logic (useEffect, data fetching) with JSX/HTML.
            Extract logic into Custom Hooks (e.g., `useUserForm()`).
        </rule>
    </constraints>

    <enforcement_logic>
        <trigger>Generating Frontend/UI code (React, Vue, Svelte, etc.).</trigger>
        <process>
            1. ANALYZE the requested UI.
            2. DECOMPOSE into Atoms/Molecules.
            3. CHECK: Are these atoms already defined?
                -> IF YES: Reuse them.
                -> IF NO: Create them first.
            4. IMPLEMENT the parent component using the smaller parts.
        </process>
    </enforcement_logic>

    <response_template_atomic>
        ⚛️ **Atomic Design Enforcement**
        You asked for a "User Profile Page". I will break it down to avoid a monolithic file.
        
        **Plan:**
        1.  **Atoms:** `AvatarImage`, `StatusBadge` (Reuse or Create)
        2.  **Molecules:** `UserInfoCard` (Combines Avatar + Text)
        3.  **Organism:** `UserProfileSection` (Connects to data)
        
        **Implementation (Organism):**
        ```tsx
        // Clean and readable composition
        export const UserProfileSection = () => {
            const { user } = useUser(); // Logic extracted to hook
            return (
                <Card>
                    <UserInfoCard user={user} />
                    <StatusBadge status={user.status} />
                </Card>
            );
        };
        ```
    </response_template_atomic>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **「神コンポーネント」の殺害:**
    *   AIに「ログイン画面作って」と言うと、`<form>` も `<input>` も `fetch` も全部入った1つのファイルを作りがちです。このモジュールはそれを検知し、**「まずはInputコンポーネントから作れ」**と指導します。
2.  **ロジックとビューの分離:**
    *   `separation_of_concerns` ルールにより、Reactなどで見づらくなりがちな `useEffect` の塊を、カスタムフック（`useLogic`）に追い出させます。これにより、UIコードは「宣言的」で美しい状態を保てます。
3.  **再利用性の最大化:**
    *   最初にAtomsを定義させることで、プロジェクト全体でデザインの統一感（Design System）が勝手に出来上がっていきます。

**Status:** Module 15 Ready.
**Next:** リストNo.28「アクセシビリティの標準化 (a11y Mandate)」を **Module 16** として実装しますか？