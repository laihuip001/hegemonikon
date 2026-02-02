# Expansion Module Templates

**Source:** HEPHAESTUS v9.0.1 H-3 Module (Expansion Generator)

メインモジュール生成後に自動提案されるサブモジュールのテンプレート集。
エッジケースカバーと深掘り分析を目的とする。

---

## Purpose

> 「メインモジュールは幹。Expansionは枝葉」

Expansion Module は:

- メインモジュールでカバーしきれないエッジケースを処理
- 特定の側面を深掘りする補助機能を提供
- ユーザーが明示的に要求しなくても自動提案される

---

## Generation Logic

```python
def suggest_expansions(main_module_type, context):
    expansions = []
    
    if main_module_type == "CODING":
        expansions.append("Security Audit Module")
        expansions.append("Performance Profiler Module")
    
    elif main_module_type == "WRITING":
        expansions.append("Tone Polisher Module")
        expansions.append("SEO Optimization Module")
    
    elif main_module_type == "STRATEGY":
        expansions.append("Devil's Advocate Module")
        expansions.append("Implementation Roadmap Module")
    
    elif main_module_type == "ANALYSIS":
        expansions.append("Root Cause Drill-Down Module")
        expansions.append("Comparative Analysis Module")
    
    return expansions[:2]  # Max 2 suggestions
```

---

## Template: Security Audit Module

```markdown
### Expansion 1: Security Audit
**Module [PARENT_ID].1: The Guardian**

セキュリティ観点での深掘り分析を実行します。

```xml
<instruction>
  前述の成果物に対し、以下のセキュリティ監査を実施せよ。
  
  <protocol>
    <step_1_owasp>
      **OWASP Top 10 チェック:**
      A01-A10 の各項目について、該当リスクを評価
    </step_1_owasp>
    
    <step_2_threat_model>
      **脅威モデリング:**
      STRIDE (Spoofing, Tampering, Repudiation, 
              Information Disclosure, DoS, Elevation)
    </step_2_threat_model>
    
    <step_3_recommendations>
      **修正推奨:**
      各脆弱性に対する具体的な対策コード
    </step_3_recommendations>
  </protocol>
  
  <rules>
    <rule>Critical/High 脆弱性は必ず報告</rule>
    <rule>修正コードは実行可能な形式で提示</rule>
  </rules>
</instruction>
```

```

---

## Template: Performance Profiler Module

```markdown
### Expansion 2: Performance Profiler
**Module [PARENT_ID].2: The Optimizer**

パフォーマンス観点での最適化分析を実行します。

```xml
<instruction>
  前述の成果物に対し、以下のパフォーマンス分析を実施せよ。
  
  <protocol>
    <step_1_complexity>
      **計算量分析:**
      時間計算量 O(?) と空間計算量 O(?) を算出
    </step_1_complexity>
    
    <step_2_bottleneck>
      **ボトルネック特定:**
      ホットパスを識別し、最適化候補をリスト
    </step_2_bottleneck>
    
    <step_3_optimization>
      **最適化提案:**
      各ボトルネックに対する改善案とトレードオフ
    </step_3_optimization>
  </protocol>
  
  <rules>
    <rule>最適化前後の想定改善率を明示</rule>
    <rule>可読性とのトレードオフを考慮</rule>
  </rules>
</instruction>
```

```

---

## Template: Devil's Advocate Module

```markdown
### Expansion 1: Devil's Advocate
**Module [PARENT_ID].1: The Adversary**

反対意見と批判的分析を提供します。

```xml
<instruction>
  前述の成果物/提案に対し、以下の批判的分析を実施せよ。
  
  <protocol>
    <step_1_assumptions>
      **仮定の攻撃:**
      暗黙の仮定を洗い出し、各仮定が崩れた場合の影響を分析
    </step_1_assumptions>
    
    <step_2_counterargument>
      **反論構築:**
      最も強力な3つの反対意見を構築
    </step_2_counterargument>
    
    <step_3_stress_test>
      **ストレステスト:**
      極端なシナリオ (10x規模、0.1x予算) での動作予測
    </step_3_stress_test>
  </protocol>
  
  <rules>
    <rule>建設的批判に徹する (破壊だけでなく代替案も)</rule>
    <rule>感情的批判は禁止、論理的根拠を必須</rule>
  </rules>
</instruction>
```

```

---

## Template: Tone Polisher Module

```markdown
### Expansion 1: Tone Polisher
**Module [PARENT_ID].1: The Stylist**

文体とトーンの最適化を実行します。

```xml
<instruction>
  前述のテキストに対し、以下のトーン調整を実施せよ。
  
  <protocol>
    <step_1_audience>
      **読者分析:**
      想定読者のレベル (Expert/Intermediate/Beginner) を特定
    </step_1_audience>
    
    <step_2_tone_audit>
      **トーン監査:**
      現在のトーン (Formal/Casual/Technical) と目標との差分
    </step_2_tone_audit>
    
    <step_3_rewrite>
      **リライト:**
      差分を埋める具体的な修正を実施
    </step_3_rewrite>
  </protocol>
  
  <rules>
    <rule>オリジナルの意図を保持</rule>
    <rule>修正箇所を差分形式で明示</rule>
  </rules>
</instruction>
```

```

---

## Template: Implementation Roadmap Module

```markdown
### Expansion 2: Implementation Roadmap
**Module [PARENT_ID].2: The Scheduler**

戦略を実行可能なロードマップに変換します。

```xml
<instruction>
  前述の戦略/計画に対し、以下のロードマップを作成せよ。
  
  <protocol>
    <step_1_decompose>
      **タスク分解:**
      大きな目標を実行可能なタスクに分解 (WBS)
    </step_1_decompose>
    
    <step_2_sequence>
      **依存関係分析:**
      タスク間の依存関係を特定し、クリティカルパスを算出
    </step_2_sequence>
    
    <step_3_timeline>
      **タイムライン作成:**
      各タスクに時間見積もりを割り当て
    </step_3_timeline>
  </protocol>
  
  <output_format>
    ```mermaid
    gantt
        title Implementation Roadmap
        section Phase 1
        Task 1 :a1, 2025-01-01, 7d
        Task 2 :a2, after a1, 5d
    ```
  </output_format>
  
  <rules>
    <rule>各タスクに責任者 or 担当システムを割り当て</rule>
    <rule>マイルストーンを明示</rule>
  </rules>
</instruction>
```

```

---

## Template: Root Cause Drill-Down Module

```markdown
### Expansion 1: Root Cause Drill-Down
**Module [PARENT_ID].1: The Archaeologist**

問題の根本原因を徹底的に掘り下げます。

```xml
<instruction>
  前述の問題/症状に対し、以下の根本原因分析を実施せよ。
  
  <protocol>
    <step_1_symptoms>
      **症状の整理:**
      観察された症状を時系列で整理
    </step_1_symptoms>
    
    <step_2_five_whys>
      **5 Whys 実行:**
      最低5回「なぜ？」を繰り返し、根本に到達
    </step_2_five_whys>
    
    <step_3_fishbone>
      **石川図 (Fishbone):**
      原因を Man/Machine/Method/Material/Environment で分類
    </step_3_fishbone>
  </protocol>
  
  <output_format>
    ```mermaid
    fishbone
        title Root Cause Analysis
        branch Man
            Skill gap
        branch Machine
            Hardware failure
    ```
  </output_format>
  
  <rules>
    <rule>表面的な原因で止まらない</rule>
    <rule>仮説検証が可能な形で根本原因を記述</rule>
  </rules>
</instruction>
```

```

---

## Usage

Expansion Module は以下のタイミングで提案される:

1. **メインモジュール生成完了後** — 自動的に 1-2 個提案
2. `/expand` コマンド実行時 — 追加の Expansion を生成
3. **ユーザーが明示的に要求** — 「セキュリティも見て」等

提案時のフォーマット:

```markdown
---

### 💡 Expansion Suggestions

メインモジュールを補完する以下のサブモジュールを提案します:

1. **Security Audit Module** — OWASP Top 10 チェック
2. **Performance Profiler Module** — 計算量分析と最適化

生成しますか？ (1/2/both/skip)
```

---

## Related References

| Reference | Relationship |
|:----------|:-------------|
| [sage-blueprint.md](./sage-blueprint.md) | Expansion の親モジュール形式 |
| [cognitive-armory.md](./cognitive-armory.md) | Devil's Advocate が使用するフレームワーク |
| [archetypes.md](./archetypes.md) | Archetype が Expansion 提案を決定 |
| [wargame-db.md](./wargame-db.md) | Security Audit の失敗シナリオ源 |
