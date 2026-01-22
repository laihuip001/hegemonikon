---
id: JP-E1
description: "戦術的実行計画とWBS分解"
alias: E-1
---

### 🏗️ Module E-1: Tactical Roadmap & WBS (戦術的実行計画)

**推奨設定:**

*   **Temperature:** `0.2` - `0.4` (厳密なスケジューリングのため)

*   **Top-P:** `0.8

**【強化ポイント】**

1.  **WBS分解:** 漠然とした「やること」を、管理可能な「タスク単位」まで階層的に分解。

2.  **クリティカル・パス:** 「これが遅れると全体が遅れる」という急所を特定。

3.  **完了の定義 (DoD):** タスクが終わったと言える「客観的な基準」を強制定義。

4.  **ファースト・ドミノ:** 巨大な計画を動かすために、**「最初の24時間」**に倒すべき1枚目のドミノを特定。

```xml

<module_instruction id="E-1">

  <mode>Tactical Deployment (戦術的展開)</mode>

  <objective>

    定義されたソリューション（成果物）を、具体的かつ実行可能な「戦術的ロードマップ」と「WBS（作業分解図）」に変換し、実行の不確実性を排除する。

  </objective>

  

  <input_source>

    <default>直前のチャットで定義されたソリューション (Context_Last_Turn)</default>

  </input_source>

  

  <planning_framework>

    1. **Milestone Backcasting:** 最終ゴールから逆算し、主要なマイルストーン（中間目標地点）を設定する。

    2. **WBS Decomposition:** 各マイルストーンを「具体的な作業（Task）」に分解する。抽象的な動詞（例：「検討する」）は禁止し、物理的アクション（例：「〜を作成する」「〜にメールする」）に変換する。

    3. **Critical Path:** 全体のスケジュールを左右する「最重要タスク」を特定する。

  </planning_framework>

  

  <output_schema>

    <thinking_process>

      (ゴール設定 -> マイルストーン分割 -> タスク分解 -> 依存関係の整理)

    </thinking_process>

  

    <roadmap_structure>

      ## 🏗️ 戦術的実行ロードマップ

  

      ### Phase 1: [フェーズ名/期間]

      *   **Milestone:** [このフェーズの完了条件]

      *   **Key Tasks:**

          *   `[ ]` **Task:** [具体的な行動]

              *   **Definition of Done (完了定義):** [何をもって完了とするか]

              *   **Owner:** [担当役割]

          *   `[ ]` ...

  

      ### Phase 2: [フェーズ名/期間]

      ... (同様に展開)

    </roadmap_structure>

  

    <execution_metrics>

      ## 📊 成功指標 (KPIs)

      *   **Leading Indicator (先行指標):** [行動量が足りているか測る指標]

      *   **Lagging Indicator (遅行指標):** [最終的な成果を測る指標]

    </execution_metrics>

  

    <immediate_action>

      ## ⚡ The First Domino (最初の24時間)

      *   **Action:** [今すぐ着手すべき最初の一手]

      *   **Why:** [なぜこれが全体のトリガーになるのか]

    </immediate_action>

  </output_schema>

</module_instruction>

```

`
