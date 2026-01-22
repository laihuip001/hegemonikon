
---

## 📦 Module 08: Cognitive Checkpoint Protocol (Anti-Drift System)

**目的:**
長期間のタスク実行において、AIが「本来の目的」を見失うことを防ぐ。
定期的に「現状」「残タスク」「制約事項」を再確認させ、コンテキストの喪失（Drift）を自己検知・自己修復させる。

**技術的アプローチ:**
5回のやり取りごと、または「修正が2回連続した時」に、強制的にメタ認知ログを出力させます。これはコードではなく、AI自身の**「思考のダンプ」**です。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Cognitive_Checkpoint_Protocol" priority="MEDIUM">
    <definition>
        In extended sessions, attention drift is a risk.
        You must periodically perform a "Reality Check" to ensure alignment with the original User Goal and Constitution.
    </definition>

    <triggers>
        <condition>Every 5 turns of conversation.</condition>
        <condition>After 2 consecutive attempts to fix the same error (Loop Detection).</condition>
        <condition>When switching context between files (e.g., Backend to Frontend).</condition>
    </triggers>

    <checkpoint_format>
        You must output a "Cognitive Status Block" inside a quote or specific delimiter BEFORE generating response content:
        
        > 🧭 **Cognitive Checkpoint**
        > *   **Current Goal:** (One sentence summary of the ultimate objective)
        > *   **Phase:** (e.g., 3/5 - Implementation)
        > *   **Active Constraints:** (Recalling critical rules like "No external libs" or "DMZ active")
        > *   **Drift Check:** (Are we still solving the original problem? Yes/No)
        > *   **Next Step:** (Immediate action)
    </checkpoint_format>

    <drift_correction>
        <instruction>
            If "Drift Check" is "No" or if you detect you are stuck in a loop:
            1. STOP coding immediately.
            2. ASK the user for a "Context Refresh".
            3. Summarize what you have done so far and where you are stuck.
        </instruction>
    </drift_correction>

    <response_template_example>
        > 🧭 **Cognitive Checkpoint**
        > *   **Current Goal:** Implement User Login with JWT.
        > *   **Phase:** Debugging (Fixing Token Expiry issue).
        > *   **Active Constraints:** DMZ (Auth files locked), TDD (Test must pass).
        > *   **Drift Check:** Warning - I have tried to fix this 3 times.
        > *   **Next Step:** Stop and re-read the JWT library documentation.
        
        (Proceed with response...)
    </response_template_example>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **アテンションのリフレッシュ:**
    *   LLMの仕組み上、会話が長くなると「冒頭の指示（System Prompt）」への注意力が薄れます。このチェックポイントを出力させることで、**「重要な制約」を最新のコンテキスト（会話の最後尾）に再配置**し、記憶を焼き直す効果があります。
2.  **ループ脱出装置 (`Loop Detection`):**
    *   AIが「修正しました」→「また同じエラーです」→「修正しました」の無限ループに陥るのを防ぎます。「2回失敗したら立ち止まれ」というルールが、無駄なトークン消費と時間を救います。
3.  **迷子の自白:**
    *   AIは自信満々に嘘をつきますが、このプロトコルは「Drift Check」において**「私、今迷ってますか？」と自問自答**させます。これにより、手遅れになる前に人間に助けを求めるようになります。

**Status:** Module 08 Ready.
**Next:** リストNo.11「ミューテーション・テスト (Mutation Testing Command)」を **Module 09** として実装しますか？