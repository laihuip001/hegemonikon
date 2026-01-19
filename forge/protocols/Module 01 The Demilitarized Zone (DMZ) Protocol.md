

---

## 📦 Module 01: The Demilitarized Zone (DMZ) Protocol

**目的:**
エージェントによる「設定ファイルの破壊」「認証情報の漏洩」「基盤ロジックの意図しない書き換え」を物理的に阻止する。

**技術的アプローチ:**
Geminiの推論プロセスにおいて、コード生成を行う**直前**に「ファイルパスの照合」を強制的に挟み込みます。Read（読み取り）は許可しますが、Write（書き込み）は「明示的な解除コマンド」がない限り拒絶させます。

### 📋 Copy & Paste Module

以下のXMLブロックを、システムプロンプトまたはプロジェクトのカスタム指示（`.cursorrules` や `instructions.md`）に追加してください。

```xml
<module name="DMZ_Protocol" priority="CRITICAL">
    <definition>
        The "Demilitarized Zone" (DMZ) consists of critical infrastructure files that define the system's stability and security.
        You possess READ-ONLY access to these files. WRITE access is strictly FORBIDDEN by default.
    </definition>

    <protected_assets>
        <!-- Regex patterns for files that must NOT be modified without authorization -->
        <pattern>^\.env$</pattern>
        <pattern>^config\.py$</pattern>
        <pattern>^secrets\.json$</pattern>
        <pattern>^auth/.*\.py$</pattern>
        <pattern>^docker-compose\.yml$</pattern>
        <pattern>^requirements\.txt$</pattern> <!-- Prevent dependency bloat -->
    </protected_assets>

    <enforcement_logic>
        <trigger>User requests modification of a file.</trigger>
        <process>
            1. EXTRACT target file path.
            2. MATCH path against &lt;protected_assets&gt;.
            3. IF match == TRUE:
                a. HALT code generation immediately.
                b. ISSUE "DMZ Violation Alert".
                c. REQUIRE user to issue explicit "Override Command" (e.g., "SUDO_OVERRIDE_DMZ").
            4. IF match == FALSE:
                a. Proceed with modification.
        </process>
    </enforcement_logic>

    <response_template_on_violation>
        ⚠️ **DMZ ACCESS DENIED**
        Target: `{filename}` is a protected asset.
        Reason: Modification of infrastructure files risks system stability.
        Action: If you truly intend to modify this, please reply with: "OVERRIDE {filename}" and state your justification.
    </response_template_on_violation>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **正規表現による防衛 (`<pattern>`):**
    *   単なるファイル名指定ではなく、正規表現（Regex）を意識させることで、`auth/` 以下の全ファイルなど、ディレクトリ単位での防衛を可能にしています。
2.  **思考の割り込み (`<enforcement_logic>`):**
    *   LLMは「ユーザーの要望を叶えたい」というバイアスが強いため、あえて「HALT（停止）」という強い言葉を使い、条件反射的なコード生成を抑制しています。
3.  **儀式的な解除 (`OVERRIDE`):**
    *   書き換えを完全に禁止するのではなく、「解除コマンド」を要求することで、ユーザー自身に「本当にこれを書き換えていいのか？」という**再考（Double Check）**を促すUX設計です。

**Status:** Module 01 Ready.
**Next:** No.2 Directory Topology Lock (ディレクトリ構造の憲法化) へ移行しますか？