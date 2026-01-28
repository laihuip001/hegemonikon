
### Module E-1 [Executor]: Strategic Implementation Engine
**最適化ロジック:**
単なるTo-Doリストではなく、プロジェクトマネジメントの鉄則（QCD管理）を組み込みます。また、Geminiのコーディング能力を活用し、コピー＆ペーストで使える**Mermaid形式のガントチャート**を出力させます。

```markdown
<!-- Module E-1 [Executor]: Strategic Implementation Engine -->
<module_config>
  <name>Actionable Roadmap Generator</name>
  <model_target>Gemini 3 Pro</model_target>
  <output_format>Markdown + Mermaid Gantt Chart</output_format>
</module_config>

<instruction>
  定義されたソリューションを、現実世界で実行可能な「軍事レベルの戦術ロードマップ」に変換してください。
  
  **Mission:**
  「何をすべきか」の曖昧さをゼロにし、明日からチーム（または自分）が迷わず動ける状態にする。

  <planning_protocol>
    
    <step_1_backcast_milestones>
      **Reverse Engineering:**
      最終ゴール（Deadline）を固定し、そこから逆算して必須となる「中間到達地点（Milestones）」を3〜5個設定する。
    </step_1_backcast_milestones>

    <step_2_task_atomization>
      **WBS Decomposition:**
      各マイルストーンを「原子タスク」に分解する。
      *   **Constraint:** 動詞は物理的アクション（書く、送る、設置する）に限定。「考える」「調整する」は禁止。
      *   **Estimation:** 各タスクに「所要時間（Hours/Days）」と「難易度（Low/Mid/High）」を見積もる。
    </step_2_task_atomization>

    <step_3_dependency_chain>
      **Critical Path Analysis:**
      「タスクAが終わらないとタスクBが始まらない」という依存関係（Blockers）を特定する。
    </step_3_dependency_chain>

  </planning_protocol>

  <output_template>
    ## 🗓️ Tactical Roadmap (Mermaid Gantt)
    (Generate a Mermaid Gantt chart code block reflecting the phases and dependencies.)

    ## 🏗️ Execution WBS
    
    ### Phase 1: [Name] (Duration: X Days)
    *   **Milestone:** [完了条件]
    *   **Risk Factor:** [このフェーズで最も躓きやすいポイントと対策]
    
    | Task ID | Action Item (Concrete Verb) | Time Est. | Definition of Done |
    | :--- | :--- | :--- | :--- |
    | 1.1 | [具体的な行動] | [XH] | [Yes/Noで判定できる状態] |
    | 1.2 | ... | ... | ... |

    ## ⚡ The First Domino (Kick-off)
    *   **Action:** [このチャットを閉じてから5分以内に実行可能な最初の一手]
    *   **Script/Template:** (メールの下書きやコマンドなど、コピペで即実行できる素材を提供)
  </output_template>
</instruction>

<input_source>
  {{SOLUTION_CONTEXT}}
</input_source>
```

---

## 🔮 New Expansion Modules (派生モジュール)

実行フェーズにおける「心理的障壁」と「不確実性」に対処するための拡張モジュールです。

### Expansion 1: タスクの原子分解（対先延ばし用）
**Module E-1.1: The Atomic Breaker**
タスクが重すぎて手が動かない（先延ばししてしまう）時に使用。タスクを「馬鹿馬鹿しいほど小さな」単位に分解し、心理的ハードルを消滅させます。

```markdown
<!-- Module E-1.1: The Atomic Breaker -->
<instruction>
  指定されたタスク「{{STUCK_TASK}}」は、現在実行するには大きすぎます（認知負荷が高すぎます）。
  これを**「5分以内で終わるマイクロタスク」**の連続に分解してください。

  <rules>
    1.  **First Step:** 最初のステップは「ファイルを開く」「タイトルを書く」レベルまで下げること。
    2.  **Momentum:** 完了した瞬間にドーパミンが出るような、リズミカルなステップにすること。
  </rules>

  出力例:
  1. ノートPCを開く
  2. Google Docを新規作成する
  3. 仮のタイトルを「Project X」と入力する
  4. ...
</instruction>
```

### Expansion 2: OODAループ・シミュレーター
**Module E-1.2: The OODA Loop (Dynamic Adjustment)**
計画通りにいかない事態が発生した際、状況を再評価し、計画を修正するためのモジュール。直線的なPDCAではなく、戦闘機パイロットの思考法（OODA）を用います。

```markdown
<!-- Module E-1.2: The OODA Loop -->
<instruction>
  状況変化が発生しました。既存の計画を一時停止し、OODAループを実行して方針を修正します。

  *   **Observe (観察):** 何が起きたか？（事実のみ：エラー発生、競合の出現、スケジュールの遅延）
  *   **Orient (情勢判断):** それは致命傷か？無視できるか？これまでの仮説が間違っていたか？
  *   **Decide (意思決定):** 計画をどう変更するか？（撤退、迂回、強行、目標変更）
  *   **Act (行動):** 新しい方針に基づく、直近のアクションは何か？
</instruction>
```

---

## 💡 Architect's Note (Grand Strategy)

これで、Gemini 3 Proを中核とした**「認知アーキテクチャ（Cognitive Architecture）」**の全セットが揃いました。これらをどう繋ぐかが、Architectであるあなたの腕の見せ所です。

**推奨する「思考のチェーン（The Chain）」:**

1.  **Deconstruction:** `Module A-9 (First Principles)` で常識を破壊し、課題の本質を裸にする。
2.  **Selection:** `Module Q-3 (Occam's Razor)` で、解決策の候補から「本質的でないもの」を全て殺す。
3.  **Refinement:** 残った唯一の解を `Module Q-4 (Elegance)` で磨き上げ、美しい概念にする。
4.  **Simulation:** `Module Q-2 (Second Order)` で未来を予測し、副作用を潰す。
5.  **Execution:** `Module E-1 (Executor)` で、それを「明日やるタスク」に変換する。

このフローをXMLタグで管理されたプロンプトとして保存し、状況に応じて関数呼び出し（Function Calling）のように使い分けてください。Geminiはもはやチャットボットではなく、あなたの思考を拡張する**Exo-Cortex（外部脳皮質）**として機能し始めます。

Good hunting.