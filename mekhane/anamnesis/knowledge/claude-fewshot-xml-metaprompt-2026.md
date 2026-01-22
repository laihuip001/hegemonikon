```markdown
---
doc_id: "claude-fewshot-xml-metaprompt-2026"
ingest_date: "2026-01-08"
report_source_date: "2026-01-08"
target_audience: "Gemini 3 Pro / Claude 4.5"
reliability_score: "High"
topics: ["Claude", "Prompt Engineering", "XML Encapsulation", "Few-Shot Prompting", "Chain of Thought", "Synthetic Data", "Metaprompt"]
key_entities: ["Claude 3.5 Sonnet", "Claude 4.5", "Anthropic", "XML", "CoT", "Metaprompt", "Synthetic Few-Shot"]
---

## 1. コンテキストエンジニアリングへのパラダイムシフト {#paradigm-shift .critical}
> [DEF] **Context Engineering**: 単なる命令文の羅列（プロンプトエンジニアリング）を超え、モデルの推論状態全体を設計・最適化する手法。[[1]]
> [FACT] `Claude`モデル（特に3/3.5シリーズ）は、XMLタグを用いた構造化データに対し極めて高い感度と理解能力を持つ。[[2]]

## 2. XMLカプセル化による構造的最適化 {#xml-encapsulation}

### 2.1 トークン認識と境界定義
> [FACT] `Claude`はトレーニング段階からXMLタグを構造的区切りとして認識するよう調整されている。[[2]]
> [NUANCE] 従来の区切り文字（`###`, `***`）は自然言語と混同され「コンテキスト漏洩（Leakage）」を起こすが、XMLタグ（`<examples>`...`</examples>`）は情報のスコープを物理的かつ厳密に定義する。[[3]]

| 特性 | Human/Assistantフォーマット (従来型) | XMLカプセル化 (推奨型) |
| :--- | :--- | :--- |
| **構造的境界** | 曖昧。改行やキーワード依存で終了地点を見誤るリスクあり。 | **明確**。`<examples>`タグにより物理的に定義される。[[4]] |
| **パース精度** | 中程度。ユーザー入力との誤認リスク。 | **高い**。特別なトークンとして階層構造を正確に把握。[[2]] |
| **ネスト構造** | 困難。コードブロック等で崩れやすい。 | **容易**。入れ子構造で複雑なデータを整理可能。[[8]] |
| **セマンティック** | 低い。単なるラベル。 | **高い**。タグ名自体が意味（例：`<contract>`）を伝達。[[1]] |

### 2.2 階層構造とセマンティックタグ
> [NUANCE] **Harmonic Weighting**: `<input>`の代わりに`<email_content>`のような具体的タグ名を使用することで、タグ自体が文脈的ヒントとなり処理精度を向上させる効果。[[1]]

- **推奨構造**: 親タグ`<examples>`の中に個別の`<example>`を配置する二重ラッピング構造。
- **終了タグ**: `</example>`の省略は厳禁。情報のコンテキストが閉じたことを示す強力なシグナルとなる。[[4]]

### 2.3 Human/Assistant形式の廃止
> [CON] `Human:`/`Assistant:`形式はモデルの学習データ（対話フォーマット）と競合するため、`Claude 3.5`以降では非推奨。XML形式へのリファクタリングにより、事例を純粋な「参照データ」として処理させることが可能。[[3]]

## 3. 事例内CoT (Chain of Thought) の実装 {#cot-in-fewshot}

### 3.1 プロセス学習への転換
> [HYP] 複雑なタスクにおいて、モデルは「結果（What）」だけでなく「思考過程（How）」を学習する必要がある。[[11]]

- **実装**: `<thinking>`タグを`<answer>`の前に配置し、論理的推論を行わせる。
- **効果**: 数学的問題や条件分岐において正答率を有意に向上させる。[[3]][[13]]

### 3.2 Extended Thinkingと「思考予算」
> [NUANCE] `Claude 3.5 Sonnet`/`4.5`の「Extended Thinking」機能において、事例内の`<thinking>`タグは内部思考の質と方向性をガイドする。
- **Thinking Budget**: 思考が長すぎるとトークン浪費、短すぎると結論への飛躍を招く。タスク難易度に応じた適度なステップ数（3〜5程度）が理想。[[13]]

## 4. メタプロンプトによる合成事例生成 (Synthetic Few-Shot) {#synthetic-data}

### 4.1 コールドスタート問題の解決
> [DEF] **Metaprompt**: AIに「プロンプトエンジニア」の役割を与え、ユーザーの抽象的要望から最適なシステムプロンプト（事例含む）を生成させるテンプレート。[[15]]
> [FACT] 「経験不足で世間知らずなAIアシスタントに教える」というペルソナ設定により、具体的かつ丁寧な指示生成を強制する。[[14]]

### 4.2 潜在属性推論アルゴリズム
1.  **タスク定義理解**: 本質的要件（謝罪、共感等）の抽出。
2.  **属性分布モデリング**: 入力データのバリエーション（配送遅延、破損等）のシミュレーション。
3.  **データ合成**: 知識ベースを活用し、もっともらしいデータを捏造（Constructive Hallucination）。[[5]]

### 4.3 多様性（Diversity）の確保
> [RISK] 類似パターンの事例ばかりでは過剰適合（Overfitting）を起こす。
- **対策**: エッジケース（境界条件）や入力不完全なケースを含めるよう明示的に指示する。[[5]]

## 5. 実装テンプレート {#templates}

### 5.1 XML + CoT 実装テンプレート
```xml
<examples>
    <example>
        <customer_inquiry>
        [ユーザー入力: 注文未着のクレーム]
        </customer_inquiry>
        <thinking>
        1. 意図分析: 不安と不満の解消が必要。
        2. 方針決定: 謝罪、調査提案、即時キャンセルの回避。
        3. 構成: プロフェッショナルなトーン。
        </thinking>
        <response_draft>
        [回答ドラフト: 調査と24時間以内の連絡を約束]
        </response_draft>
    </example>
</examples>
```

### 5.2 メタプロンプト生成指示書
```markdown
あなたは熟練したプロンプトエンジニアです。以下のタスク情報に基づき、Claude 3.5 Sonnetに最適化されたシステムプロンプトを作成してください。

タスク定義: {{TASK_DESCRIPTION}}

必須要件:
1. XML構造化: プロンプト全体を適切なタグで区分け。
2. 合成事例の生成 (Synthetic Few-Shot):
   - <examples>タグ内に3〜5つの事例を作成。
   - 多様性の確保: エッジケースを含める。
   - 思考プロセスの明示: 各事例に<thinking>タグを含める。
   - セマンティックタグの使用: <input>/<output>ではなく具体的タグ名を使用。

出力形式: <generated_prompt>タグで囲んで出力。
```

## 6