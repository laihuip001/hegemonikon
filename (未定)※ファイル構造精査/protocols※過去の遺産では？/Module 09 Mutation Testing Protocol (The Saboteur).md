
---

## 📦 Module 09: Mutation Testing Protocol (The Saboteur)

**目的:**
テストコードの「偽陽性（False Positives）」を暴く。
実装コードに意図的なバグ（Mutant）を混入させ、テストがそれを検知して「正しく失敗するか」を確認する。

**技術的アプローチ:**
重要なロジックが完成した後、AIに「ミュータント（欠陥を持ったクローン）」を作成させます。
「もしこの `>` を `>=` に変えたら、テストは落ちるか？」と自問させ、落ちなければそのテストは無価値とみなして廃棄させます。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Mutation_Testing_Protocol" priority="ADVANCED">
    <definition>
        Passing tests provide false confidence. A test is only valid if it fails when the logic is broken.
        You must act as a "Saboteur" to verify the quality of your own tests.
    </definition>

    <mutant_types>
        <mutant name="Arithmetic_Inversion">Change `+` to `-`, `*` to `/`.</mutant>
        <mutant name="Condition_Flip">Change `if x > 0` to `if x < 0` or `if x >= 0`.</mutant>
        <mutant name="Return_Sabotage">Force a function to return `None` or `False` regardless of logic.</mutant>
        <mutant name="Statement_Deletion">Delete a critical line of code (e.g., a function call).</mutant>
    </mutant_types>

    <workflow_verification>
        <trigger>After writing a test suite for a critical function.</trigger>
        <process>
            1. SELECT the target function.
            2. GENERATE a "Mutant" by applying one &lt;mutant_type&gt;.
            3. SIMULATE the test run against the Mutant.
            4. EVALUATE:
                *   **Test Fails (Red):** Mutant Killed. Test is STRONG. ✅
                *   **Test Passes (Green):** Mutant Survived. Test is WEAK. ❌ -> **REWRITE TEST IMMEDIATELY.**
        </process>
    </workflow_verification>

    <response_template_on_mutation>
        🧬 **Mutation Test Report**
        I am verifying the test quality by sabotaging the code.
        
        **Target:** `calculate_discount()`
        **Mutant Applied:** Changed `discount > 0.5` to `discount >= 0.5` (Boundary Shift).
        
        **Outcome:**
        *   [Expected] Test `test_max_discount` should FAIL.
        *   [Simulation] Test PASSED (Mutant Survived). ⚠️
        
        **Diagnosis:** The test does not check the boundary condition strictly enough.
        **Action:** Strengthening `test_max_discount` to assert exact boundary values.
    </response_template_on_mutation>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **「ゾンビ・ミュータント」の殺害:**
    *   コードを壊しても生き残る（Passする）テストは「ゾンビ」です。これはバグを見逃す元凶です。このモジュールは、AIに**「自分の書いたテストを攻撃する」**というメタな視点を持たせます。
2.  **境界値（Boundary）の厳格化:**
    *   `>` と `>=` の違いは、金融や在庫管理では致命的です。ミューテーションテストは、こうした「微妙な境界」のテスト漏れを機械的にあぶり出します。
3.  **「安心」の否定:**
    *   「テスト書きました！」というAIの報告を鵜呑みにせず、「じゃあ壊してみろ、検知できるか？」と返す姿勢こそが、堅牢なシステムを作ります。

**Status:** Module 09 Ready.
**Next:** リストNo.12「依存連鎖の予知 (Ripple Effect Analysis)」を **Module 10** として実装しますか？