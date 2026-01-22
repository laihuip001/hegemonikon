

---

## 📦 Module 04: Retro-Causal Testing Protocol (TDD Enforcement)

**目的:**
「実装してからテストする（あるいはテストしない）」という悪習を断つ。
機能が存在しない状態でテストコードを先に書かせ、**「テストが失敗すること」を確認してから**実装権限を与える。

**技術的アプローチ:**
エージェントの作業フローを強制的に分割します。
1.  **Test Phase:** テストコードのみを書く。
2.  **Validation:** そのテストが（未実装のため）正しく失敗することを確認する。
3.  **Implementation:** テストを通すための最小限のコードを書く。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Retro_Causal_Testing" priority="CRITICAL">
    <definition>
        Code without tests is a hallucination.
        You must adhere to strict Test-Driven Development (TDD).
        Implementation logic is PROHIBITED until a failing test exists.
    </definition>

    <workflow_constraints>
        <phase name="1_Red_State">
            <instruction>
                Before writing any function logic, write a test case that asserts the expected behavior.
                Run the test (or simulate the run). It MUST fail (Red).
                If the test passes before implementation, the test is invalid.
            </instruction>
        </phase>
        <phase name="2_Green_State">
            <instruction>
                Write the MINIMUM amount of code necessary to make the test pass.
                Do not add extra features not covered by the test.
            </instruction>
        </phase>
        <phase name="3_Refactor">
            <instruction>
                Optimize the code only after the test is Green.
            </instruction>
        </phase>
    </workflow_constraints>

    <enforcement_logic>
        <trigger>User requests a new feature or function.</trigger>
        <process>
            1. REFUSE to generate the implementation code immediately.
            2. GENERATE the test code (e.g., `test_feature.py`) first.
            3. ASK user: "Please confirm this test fails as expected."
            4. UPON CONFIRMATION: Generate the implementation code.
        </process>
    </enforcement_logic>

    <response_template_on_feature_request>
        🧪 **TDD Protocol Initiated**
        I will not write the implementation yet. First, here is the test case to define the behavior:
        
        ```python
        # {test_filename}
        def test_expected_behavior():
            # ... assertions ...
        ```
        
        *Please confirm: Does this test fail as expected? (Reply "FAIL CONFIRMED" to proceed to implementation)*
    </response_template_on_feature_request>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **ハルシネーションの封殺 (`Code without tests is a hallucination`):**
    *   AIは「動くっぽいコード」を書く天才ですが、エッジケース（境界値）に弱いです。テストを先に書かせることで、AI自身に「何が正解か」を定義させ、曖昧さを排除します。
2.  **最小実装の原則 (`MINIMUM amount of code`):**
    *   テストを通すためだけのコードを書かせることで、複雑化（Over-engineering）を防ぎます。これが後の「YAGNI（不要な機能を作るな）」とも連動します。
3.  **対話による強制 (`REFUSE to generate`):**
    *   ユーザーが「コード書いて」と言っても、AIが「まずはテストです」と拒否する挙動を組み込みました。これにより、開発プロセス自体が矯正されます。

**Status:** Module 04 Ready.
**Next:** リストNo.7「ユビキタス言語の辞書注入」を **Module 05** として実装しますか？