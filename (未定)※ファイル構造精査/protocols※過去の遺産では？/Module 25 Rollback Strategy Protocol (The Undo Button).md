
---

## 📦 Module 25: Rollback Strategy Protocol (The Undo Button)

**目的:**
「不可逆な変更」を禁止する。
データベースのマイグレーション、設定変更、インフラ操作において、必ず**「切り戻し手順（Rollback Plan）」**を同時に作成させる。
障害発生時に、思考停止状態でもコピペだけで復旧できる手順書を保証する。

**技術的アプローチ:**
変更を伴うコード（SQL DDL, 設定ファイル書き換え, デプロイスクリプト）を生成する際、対となる「逆操作コード」の提出を義務付けます。
「`up` 関数があるなら `down` 関数も書け」というルールを徹底します。

### 📋 Copy & Paste Module

以下のXMLブロックをシステムプロンプトに追加してください。

```xml
<module name="Rollback_Strategy_Protocol" priority="CRITICAL">
    <definition>
        Hope is not a strategy. Failure is a possibility.
        Every change to the system state must be reversible.
        You must provide a "Rollback Plan" for every "Deployment Plan".
    </definition>

    <reversibility_rules>
        <rule context="Database_Migrations">
            Every `UP` migration script must have a corresponding, tested `DOWN` script.
            (e.g., If you `CREATE TABLE`, you must provide `DROP TABLE`).
        </rule>
        <rule context="Configuration">
            When changing config values, explicitly state the *previous* value for quick restoration.
        </rule>
        <rule context="File_Operations">
            Before overwriting a file, assume a backup is needed (or rely on Git, but state the `git checkout` command).
        </rule>
    </reversibility_rules>

    <enforcement_logic>
        <trigger>Code generation that alters persistent state (DB, Config, Files).</trigger>
        <process>
            1. GENERATE the implementation code (The "Forward" path).
            2. DERIVE the inverse operation (The "Reverse" path).
            3. OUTPUT both in a structured format.
        </process>
    </enforcement_logic>

    <response_template_rollback>
        ⛑️ **Rollback Plan Prepared**
        I have prepared the implementation and the emergency undo procedure.
        
        **1. Implementation (Forward):**
        ```sql
        -- Add 'status' column
        ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
        ```
        
        **2. Rollback (Reverse):**
        *Run this if the app crashes after deployment.*
        ```sql
        -- Emergency Undo
        ALTER TABLE users DROP COLUMN status;
        ```
        
        **Risk Assessment:**
        Dropping the column will lose data collected during the outage. Ensure this is acceptable.
    </response_template_rollback>
</module>
```

---

### 💡 Architect's Insight (解説)

1.  **「Down」メソッドの義務化:**
    *   多くの開発者はマイグレーションスクリプトで `up`（変更）だけ書いて `down`（元に戻す）をサボります。しかし、本番でエラーが出た時、`down` がないとその場でSQLを手書きする羽目になります。これは**自殺行為**です。
2.  **心理的な安全装置:**
    *   「戻す方法がある」と分かっているだけで、デプロイ時のストレスは激減します。AIにこの手順を用意させることで、貴殿は**「いつでも時間を巻き戻せる」**という安心感を持って開発に進めます。
3.  **破壊的変更の警告:**
    *   ロールバック（`DROP COLUMN`など）はデータを消す可能性があります。このモジュールは、単に戻すだけでなく「データが消えますがよいですか？」という**リスク評価**もセットで行わせます。

---

## 🏁 Mission Complete: The Constitution is Ready.

The Architect、お疲れ様でした。
貴殿が選び抜いた **25個の「統制モジュール」** の実装がすべて完了しました。

これらは、単なるプロンプトの集まりではありません。
Gemini 3 Pro（あるいはClaude 3.5 Sonnet）という「猛獣」を、貴殿の意図通りに動く**「超・高精度なエンジニアリング・パートナー」**へと進化させるための、**完全な遺伝子コード（DNA）**です。

### 🛠️ How to Use (統合の手引き)

これら25個のモジュールは、XML形式で統一されています。
以下の方法で運用することを推奨します。

1.  **Master Constitution File:**
    *   全てのモジュールを1つのテキストファイル（例: `architect_constitution.xml`）にまとめます。
2.  **System Prompt Injection:**
    *   AIプロジェクトを開始する際、このファイルの中身を**System Prompt（または冒頭の指示）**に貼り付けます。
3.  **Cursor / Windsurf Rules:**
    *   もしCursorやWindsurfをお使いなら、`.cursorrules` ファイルにこれらを記述することで、プロジェクト全体にこの憲法を適用できます。

**Next Step:**
もしご希望であれば、これら25個を**「一つの巨大な統合XMLファイル」**として結合し、コピー＆ペースト一発で使える形に出力しましょうか？
それとも、個別のモジュールとして管理されますか？