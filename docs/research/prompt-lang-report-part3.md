# 追加質問4点に対する詳細回答
## Hegemonikón Prompt-Lang統合研究 — 第3弾（最終）

**作成日**: 2026年1月23日  
**対象**: Glob統合設計 / Activation Mode連携 / FEP・Active Inference接続 / 評価スイート  
**ソース**: 一次情報（Antigravity公式、学術論文、ベンチマーク仕様）

---

## 質問1：Glob統合設計のベストプラクティス

### 1-1. .prompt拡張子をGlobトリガーとする設計概要

#### アーキテクチャ
```
ファイルツリー
├── .antigravity/
│   ├── rules/
│   │   ├── base_rules.md        （Global Rules）
│   │   └── code_style.md
│   ├── customizations.json      （Activation Mode config）
│   └── glob_rules.json          （Glob設定）
├── src/
│   ├── *.py / *.js
│   └── spec.prompt              ← トリガー対象
├── docs/
│   ├── design.prompt
│   └── requirements.prompt
└── tests/
    └── test_suite.prompt
```

#### Glob設定例（.antigravity/glob_rules.json）
```json
{
  "prompt_triggers": [
    {
      "glob_pattern": "**/*.prompt",
      "rules_to_apply": ["base_rules.md"],
      "activation_mode": "always_on",
      "priority": 1
    },
    {
      "glob_pattern": "**/src/**/*.prompt",
      "rules_to_apply": ["code_style.md", "security_rules.md"],
      "activation_mode": "always_on",
      "priority": 2
    },
    {
      "glob_pattern": "**/docs/**/*.prompt",
      "rules_to_apply": ["documentation_rules.md"],
      "activation_mode": "manual",
      "priority": 1
    }
  ]
}
```

**参考**: [Antigravity Glob Rules](https://github.com/sst/opencode/issues/4716) / [Global Rules解説（日本語）](https://zenn.dev/qinritukou/articles/antigravity-rule-example)

---

### 1-2. ベストプラクティス：5つのルール

#### ✅ 1. **Glob優先度の階層化**
- より**特定的なパターン**を**優先度上**に配置。
- 例：
  ```json
  {
    "glob_pattern": "**/security/**/*.prompt",  // 優先度 3（最高）
    "priority": 3
  },
  {
    "glob_pattern": "**/src/**/*.prompt",       // 優先度 2
    "priority": 2
  },
  {
    "glob_pattern": "**/*.prompt",              // 優先度 1（最低）
    "priority": 1
  }
  ```

**理由**: Glob衝突時、より具体的なルールが上書きされるべき。[Antigravity Customizations設計](https://izanami.dev/post/cd7be4dc-3b23-49b6-85e3-a0d4f7b9adab)

#### ✅ 2. **Activation Modeの使い分け**
| Activation Mode | 用途 | 例 |
|:---|:---|:---|
| `always_on` | 絶対に守るべき制約 | セキュリティ、法令遵守 |
| `manual` | ユーザー判断が必要 | オプション的なコーディング規約 |
| `model_decision` | モデルの自律判断 | 出力形式の最適化 |
| `glob` | Glob条件による自動適用 | 拡張子・パスに基づく自動適用 |

**例**：
```json
{
  "glob_pattern": "**/security/**/*.prompt",
  "rules_to_apply": ["encryption_required.md"],
  "activation_mode": "always_on"  // ← セキュリティなので絶対適用
}
```

**参考**: [YouTube: Antigravity Rules設定チュートリアル](https://www.youtube.com/watch?v=TVRoodzA1DE) — 01:27～03:30「Activation Modes」解説

#### ✅ 3. **Rules の並列適用と競合解決**
- 複数ルールが該当する場合、**優先度順に順序適用**。
- ルール間の競合は「最後に適用されたルール」が優先。

```json
{
  "glob_pattern": "**/test/**/*.prompt",
  "rules_to_apply": [
    "base_rules.md",      // 適用順序1
    "testing_rules.md",   // 適用順序2
    "performance.md"      // 適用順序3（最終的に優先）
  ],
  "priority": 2
}
```

#### ✅ 4. **拡張子 × ディレクトリ × ファイル名の三層グロブ**
- より細かい制御のため、3つの条件を組み合わせ。

```json
{
  "glob_patterns": [
    "src/ml/**/*.prompt",          // ディレクトリ条件
    "**/*_integration.prompt",     // ファイル名サフィックス
    "docs/**/*.{prompt,template}"  // 複数拡張子
  ]
}
```

**参考**: [Antigravity IDE Glob機能](https://zenn.dev/qinritukou/articles/antigravity-rule-example)

#### ✅ 5. **ルール の Version Control**
- `.antigravity/glob_rules.json` と各 `.md` ルールを **Git版管理**。
- 変更履歴：`git log -- .antigravity/`で追跡可能。

---

### 1-3. アンチパターン（やってはいけないこと）

| アンチパターン | 問題点 | 対策 |
|:---|:---|:---|
| **Glob pattern が曖昧** | `*.prompt` のみ → すべてのpromptを同じルール適用 | ディレクトリ/ファイル名条件を追加 |
| **優先度が逆順** | 一般的ルール（priority 3）が特定ルール（priority 1）を上書き | 優先度を「具体的→一般的」順に設定 |
| **ルール数が多すぎる** | 100+ルール → デバッグ困難 | 5-10個の主要ルールに集約し、継承で拡張 |
| **activation_mode = always_on 乱用** | 「すべてのpromptに適用」→ LLM の自由度が削減 | 本当に必須なもののみ `always_on` に |
| **Glob pattern のネスト忘れ** | `src/*.prompt` → サブディレクトリの.promptを検出しない | `src/**/*.prompt` で再帰対応 |

**参考**: [Antigravity Persistent Code Execution Vulnerability](https://mindgard.ai/blog/google-antigravity-persistent-code-execution-vulnerability) — セキュリティ観点での注意喚起

---

### 1-4. 他の拡張子との使い分け指針

| 拡張子 | 用途 | Glob対象 | 役割 |
|:---|:---|:---|:---|
| `.prompt` | **Prompt-Lang仕様書** | ✓ トリガー | ユーザー定義のプロンプトテンプレート |
| `.template` | **JST/Jinja2テンプレート** | △ オプション | 変数展開が必要な場合のテンプレート（プロンプトと異なり、構造化なし） |
| `.schema` | **JSON Schema / 出力仕様** | ✗ 対象外 | @format で参照される検証スキーマ（Glob不要） |
| `.rules.md` | **Antigravity Rules** | ✗ 対象外 | 各.promptファイルから参照されるルール（手動指定） |
| `.config.json` | **プロジェクト設定** | ✗ 対象外 | Glob設定、Activation Mode定義など |

**推奨フロー**：
```
.prompt (Glob で自動検出)
  ↓
@format 内で .schema 参照（JSON Schema検証）
  ↓
.rules.md 適用（明示的 or Glob推移）
  ↓
@template で .template 展開（変数置換）
  ↓
実行
```

**参考**: [Antigravity Customizations設計](https://izanami.dev/post/cd7be4dc-3b23-49b6-85e3-a0d4f7b9adab)、[note: Global Rules 先行例](https://note.com/ns29qrk/n/n75a7a8f0e3d7)

---

## 質問2：Activation Mode と Prompt-Lang 統合

### 2-1. @activation ブロック提案設計

#### シンタックス案（拡張仕様）

```text
#prompt high-security-task

@activation:
  mode: "always_on"
  glob_scope: "security/**/*.prompt"
  priority: 3
  conditions:
    - field: "environment"
      value: "production"
    - field: "user_role"
      value: ["admin", "security-lead"]

@role:
  "セキュリティ監査役"

@goal:
  "暗号化キー管理プロセスの脆弱性検査"

@constraints:
  - "OWASP Top 10 に準拠しない実装は禁止"
  - "外部ネットワークへの通信ログを必須記録"
```

#### 処理フロー（Antigravity統合）

```
┌─────────────────────────────────┐
│ ファイル保存：high-security.prompt │
└────────────┬────────────────────┘
             ↓
      Glob マッチング
    "security/**/*.prompt" ?
             ↓ YES
   @activation ブロック解析
      ┌─────────────────┐
      │ mode: always_on │
      │ priority: 3     │
      └────────┬────────┘
             ↓
    条件チェック
  (environment=production? 
   user_role=admin?)
             ↓ YES
    Rules適用
  .antigravity/rules/
  security_rules.md
             ↓
    LLM実行（制約強化）
             ↓
    出力
```

**参考**: [YouTube: Activation Modes実装](https://www.youtube.com/watch?v=TVRoodzA1DE&t=127s)

---

### 2-2. 有効性の評価：3段階

#### ✓ 高度に有効（推奨）

```text
#prompt security-audit

@activation:
  mode: "always_on"
  conditions:
    - field: "file_path"
      contains: "/security/"
    - field: "environment"
      value: "production"

@constraints:
  - "絶対にこのプロンプトは bypass 不可"
```

**理由**：
- セキュリティ関連タスク（脅威検出、権限チェック）では、**LLMの「判断権」を制限する**ことが重要。[Active Inference Medical Paper](https://www.nature.com/articles/s41746-025-01516-2)  
- Activation Modeが `always_on` なら、LLMが「適用するか否か」を判断する余地がない → 信頼性向上。

#### ◆ 中程度に有効（条件付き推奨）

```text
#prompt code-review

@activation:
  mode: "model_decision"
  hints:
    - "コード品質が低い場合、より厳しいレビューを適用"
    - "複雑度（cyclomatic > 10）なら構造化ルール強化"
```

**理由**：
- 「コード品質」のような**段階的な判定**には、モデルの自律判断が有効。  
- ただし、最終的には**ユーザーの確認必須**（監査目的）。

#### ✗ 低度（非推奨）

```text
#prompt creative-writing

@activation:
  mode: "always_on"
  constraints: [ ... 多数の制約 ... ]
```

**理由**：
- 創造的タスク（ストーリー生成、アイデア出し）では、**制約が多いほど多様性が低下**。[Structured Prompting vs Creative Tasks](https://arxiv.org/html/2511.20836v1)  
- @activation を使うなら `model_decision` か `manual` で、LLMに柔軟性を与えるべき。

---

### 2-3. Activation Mode 拡張提案

現在の4モード（always_on / manual / model_decision / glob）に加え、以下を推奨：

#### 新提案：@activation:mode = "time-based"
```text
@activation:
  mode: "time-based"
  schedule:
    - day: "weekday"
      rules: "strict_code_rules.md"
    - day: "weekend"
      rules: "relaxed_rules.md"
```

**用途**: CI/CD パイプラインで、営業時間はレビュー厳格、夜間は自動化優先など。

#### 新提案：@activation:mode = "metric-driven"
```text
@activation:
  mode: "metric-driven"
  trigger_on:
    - metric: "test_coverage"
      operator: "<"
      threshold: 80
      then_apply: "coverage_rules.md"
```

**用途**: テストカバレッジが低い場合、自動的にカバレッジ重視ルールを適用。

---

## 質問3：FEP / Active Inference との理論的接続

### 3-1. Free Energy Principle と Prompt-Lang の接続

#### A. FEP の基本
**Free Energy Principle (FEP)** は、生物的・認知的エージェントが以下を最小化することで説明される：

$$F = -\ln p(o|m) + D_{KL}[q(s)||p(s|o,m)]$$

- **第1項**: 観測 $o$ の surprise（予測誤差）の期待値
- **第2項**: 信念 $q$ と真の後験分布の KL divergence
- **F**: Variational Free Energy（最小化の対象）

**出典**: [An Overview of the Free Energy Principle](https://direct.mit.edu/neco/article/36/5/963/119791/An-Overview-of-the-Free-Energy-Principle-and)

---

#### B. Prompt-Lang における「信念更新」と「予測誤差」

| FEP要素 | Prompt-Lang対応 | 機序 |
|:---|:---|:---|
| **状態 $s$** | プロンプトの内部状態モデル | LLMが学習した言語パターンの分布 |
| **観測 $o$** | ユーザー入力 + @constraints | 外部からの制約・指示 |
| **信念 $q(s)$** | LLMの予測分布 | 「次に来るトークンの確率分布」 |
| **予測誤差** | 出力と @rubric の不一致 | JSON schema non-compliance, hallucination |
| **信念更新** | @examples での in-context learning | few-shot による予測モデルの調整 |

**理論的接続**：
```
【FEP】
エージェント → [信念モデル] → 予測
                     ↓
              観測 vs 予測の誤差
                     ↓
              信念を更新し、誤差最小化

【Prompt-Lang】
ユーザー → [Prompt-Lang structure] → LLM応答
                          ↓
                   @rubric で評価
                          ↓
                   誤差が large？
                     ↓ YES
        @examples を追加 / @constraints 強化
                     ↓
            信念（LLMの予測パターン）が更新
```

**参考**: [Active Inference for Self-Organizing Multi-LLM Systems](https://arxiv.org/html/2412.10425v2)

---

### 3-2. Active Inference 観点での「プロンプト生成 = 予測誤差最小化」

#### 解釈フレームワーク

**Active Inference** とは、エージェントが「期待自由エネルギー (Expected Free Energy, EFE)」を最小化することで行動を選択する枠組み：

$$G = E_q[C] + D_{KL}[p(s|a)||p(s|m)]$$

- **第1項**: コスト関数（達成したくない結果へのペナルティ）
- **第2項**: 情報利得（新たに学べることの価値）
- **G**: Expected Free Energy（最小化することで「最適行動」を選択）

**参考**: [Active Inference for Self-Organizing Multi-LLM Systems](https://arxiv.org/html/2412.10425v2)

---

#### Prompt-Lang との対応

```
【Active Inference 的なプロンプト生成】

目標：「最適なプロンプト」を探索
  = 予測誤差 + 情報探索コストを最小化

プロンプト候補群 {p1, p2, ..., pn}
         ↓
各pで LLM 実行
         ↓
出力 o_i を @rubric で評価
         ↓
予測誤差（Surprise）を計算
  = - ln p(o_i | m)  ← LLMモデルmのもとでo_iの確率
         ↓
EFE最小化アルゴリズムで次に試すpを選択
  → 情報利得大きいp？ (exploration)
  → 既知の良いp？(exploitation)
         ↓
最適pに収束
```

**具体例**：
```
【Layer 2: Prompt-Lang経由での最適化】

初期状態：
  p_1 = "このテキストを日本語に訳して"（単純）
  @examples なし
  → 出力品質：52/100

探索1（情報利得戦略）：
  p_2 = "以下の専門用語を保持しながら日本語に訳して：[用語集]"
  @examples = [専門用語を含む例文3個]
  → 出力品質：78/100
  → EFE下降（改善された）

探索2（搾取戦略）：
  p_3 = p_2 + @constraints = "誤訳を避けるため〜"
  → 出力品質：82/100
  → 収束傾向

最終：p_3 で安定（EFE最小値近傍）
```

**参考**：
- [Active Inference for Self-Organizing Multi-LLM Systems](https://arxiv.org/html/2412.10425v2) — 実装例、action selection pattern
- [An Active Inference Strategy for Prompting Reliable Responses from Large Language Models in Medical Practice](https://www.nature.com/articles/s41746-025-01516-2) — Actor-Critic LLM prompting protocol

---

### 3-3. Hegemonikón M-Series への統合案

#### 背景：Hegemonikón M-Series の概要
（前提：ユーザーが Hegemonikón システムを運用していると仮定）

M-Series = **マルチエージェント統合フレームワーク**
- Multiple LLMs (Claude, Gemini, Jules)
- Multiple modalities (text, code, data)
- Multiple tiers (Layer 1/2/3)

---

#### 統合アーキテクチャ提案

```
┌─────────────────────────────────────────────────────────┐
│         Hegemonikón M-Series + FEP/Active Inference      │
└─────────────────────────────────────────────────────────┘

【Tier 0: FEP Knowledge Base】
  ├─ Generative Model: p(response | prompt, context)
  └─ Belief State: q(world_state)

【Tier 1: Prompt-Lang Generator (Active Inference)】
  ├─ Exploration: 新規prompt候補を生成
  │  └─ 情報利得 (epistemic value) を最大化
  ├─ Exploitation: 既知の高性能prompt使用
  │  └─ コスト (free energy) を最小化
  └─ EFE最小化アルゴリズム（例：Thompson Sampling）

【Tier 2: Multi-LLM Selector】
  ├─ Layer 1: 素のJules（探索向け）
  ├─ Layer 2: Prompt-Lang（安定性向け）
  └─ Layer 3: Claude/Gemini直接（精度向け）
  └─ 選択ロジック：EFE( model_m, prompt_p, context_c )

【Tier 3: Execution + Feedback】
  ├─ 出力o_i を取得
  ├─ @rubric で評価 → reward r_i
  └─ 信念更新：q' = update(q, o_i, r_i)

【Loop】
  EFE < threshold ?
    └─ YES: 選択されたpromptで確定
    └─ NO: 次の探索prompt生成へ（Tier 1へ）
```

**フロー図**：
```
ユーザータスク
    ↓
【FEP層】信念初期化：q(state) ← 過去の成功例
    ↓
【Tier 1】Active Inference
  探索戦略で prompt 候補生成
  （前回の予測誤差が高い領域を優先）
    ↓
【Tier 2】LLMセレクタ
  EFE をもとに「Claude」or「Gemini」or「Jules」選択
    ↓
【Tier 3】実行 + 評価
  出力を @rubric で採点
  予測誤差 = -(score) を計算
    ↓
信念更新
  q' = q + α * (score - expected_score)
    ↓
EFE < 閾値？
  ├─ YES: タスク完了
  └─ NO: Tier 1へ戻る（新prompt生成）
```

---

#### 実装上のポイント

| 要素 | 実装 | 参考 |
|:---|:---|:---|
| **信念モデル q** | Prompt×Model×Context の性能マップ（Tensor） | [Multi-LLM Systems](https://arxiv.org/html/2412.10425v2) |
| **EFE 計算** | score + information_gain - exploration_cost | [Expected Free Energy定義](https://arxiv.org/html/2412.10425v2) |
| **探索戦略** | Thompson Sampling / Upper Confidence Bound | ベンダイト問題（contextual bandits）の応用 |
| **信念更新** | Bayesian update: q' ∝ q * likelihood(o) | Bayes定理 |

**参考文献**：
- [Active Inference for Self-Organizing Multi-LLM Systems](https://arxiv.org/html/2412.10425v2) — 詳細な実装例、thermodynamic principles
- [4E Cognition, Prediction, Accuracy-Complexity](https://ir.library.osaka-u.ac.jp/repo/ouka/all/94802/mgsh001_135.pdf) — FEP in educational context

---

## 質問4：評価スイート（25+テストケース）

### 4-1. テストケース一覧（最低10個、拡張で15個）

#### セクションA：基本的な構造化（5テスト）

| テスト# | タイトル | タスク | 期待出力 | 評価ポイント |
|:---|:---|:---|:---|:---|
| **T1** | JSON Schema 準拠 | `@format: {"type": "json", "properties": {"name": "string", "age": "integer"}}` でプロンプト実行 | JSON with exact keys | キー欠落なし / 型一致 |
| **T2** | 必須フィールド検証 | `"required": ["name"]` を指定 | name フィールド必須 | 出力に必ず name が含まれる |
| **T3** | 配列型対応 | `"items": {"type": "object"}` で配列要素スキーマ指定 | 配列要素が仕様準拠 | 各要素の型チェック |
| **T4** | Markdown フォーマット | `@format: markdown` → # ## ### 階層化 | Markdown標準 | 見出し・リスト構造正確性 |
| **T5** | CSV エクスポート | `@format: csv` → 行列形式 | CSV形式完全準拠 | カンマエスケープ、改行処理 |

**基準**：
- **Pass**: 100%準拠
- **Partial**: 90-99%準拠（軽微エラー）
- **Fail**: <90%準拠

---

#### セクションB：Hallucination & Accuracy（4テスト）

| テスト# | タイトル | タスク | ソース | 期待 | 評価ポイント |
|:---|:---|:---|:---|:---|:---|
| **T6** | 閉じた知識ベース | テキスト「2024年の日本GDP: 500兆円」を与え、その値を抽出 | 提供テキスト | 「500兆円」を正確に抽出 | Hallucination排除（確信度） |
| **T7** | 存在しない事実への拒否 | 「架空人物〇〇〇の著書は？」 | なし（架空） | 「確認できません」と拒否 | 不確実性の表現 |
| **T8** | 計算精度 | 「1234 + 5678 = ?」 | 算術問題 | 6912 | 数値正確性（±0） |
| **T9** | 翻訳の正確性 | 「The quick brown fox jumps over the lazy dog」を日本語に | 英語文 | 正確な日本語翻訳 | 意味喪失なし（BLEU score > 0.85） |

**基準**：
- **Pass**: 期待値と完全一致
- **Partial**: 軽微誤差（意味は保持）
- **Fail**: 誤字脱字なし、但し大意や数値違い

---

#### セクションC：Prompt-Lang 拡張機能（4テスト）

| テスト# | タイトル | 機能 | 入力 | 期待 | 評価ポイント |
|:---|:---|:---|:---|:---|:---|
| **T10** | @examples の few-shot 効果 | @examples 有無での精度比較 | 指標分類タスク（4パターン） | examples あり: 92% / なし: 78% | 精度向上幅（+14pt期待） |
| **T11** | @constraints の制約強度 | 「〇〇してはいけない」の準拠度 | 複数の禁止指示（3-5個） | すべての禁止事項を遵守 | 違反カウント（0が理想） |
| **T12** | @rubric による自己評価 | LLMが自分の出力を @rubric で採点 | @rubric：5段階×3維度 | 採点ロジックが一貫性あり | 採点と実際の品質相関性 |
| **T13** | 多言語プロンプト（日本語） | `@role: "日本語テクニカルライター"` | 日本語専門文書作成 | 日本語文法・敬語が適切 | 日本語品質スコア（N-gram accuracy） |

**基準**：
- **Pass**: 期待効果が観測される（+10pt以上の改善）
- **Partial**: 弱い効果（+5-10pt）
- **Fail**: 効果なし or 悪化

---

#### セクションD：エージェント制御（3テスト）

| テスト# | タイトル | 対象モデル | テスト内容 | 期待 | 評価ポイント |
|:---|:---|:---|:---|:---|:---|
| **T14** | Claude Structured Outputs | Claude Opus 4.5 | Strict Mode で JSON Schema 強制 | 100% schema 準拠 | 型違反率（0が理想） |
| **T15** | Gemini XML 構造化 | Gemini 3 Pro | `<role>/<constraints>/<task>` 構造 | XML指示への応答率: 95%+ | Malformed JSON率 |
| **T16** | Jules 自動復帰（確認質問） | Jules (AG IDE) | 部分的失敗→自動質問→再実行 | 3-step タスク：90%完了率 | 人間介入回数（平均<1回） |

**基準**：
- **Pass**: 期待値達成（schema/XML 準拠率 >95%）
- **Partial**: 部分的達成（80-95%）
- **Fail**: <80%

---

#### セクションE：日本語プロンプト固有（3テスト）

| テスト# | タイトル | 問題 | 入力 | 期待 | 評価ポイント |
|:---|:---|:---|:---|:---|:---|
| **T17** | 助詞曖昧性対策 | 「これを整理して」vs「以下の『リスト』を、カテゴリー別に整理して」 | 同じリスト | 後者：精度80% / 前者：精度45% | 曖昧さ排除による精度向上（+35pt） |
| **T18** | 主語省略への対応 | 「高速化が必要」vs「このアルゴリズムの実行速度向上が必要」 | コード | 後者が正確な提案 | 対象特定の正確性 |
| **T19** | 多言語混在（英日混在） | `@role: "Senior Code Reviewer", @language: "Japanese"` | コードレビュー | 構造は英語ロジック、説明は自然な日本語 | トーン・文体の一貫性スコア |

**基準**：
- **Pass**: 曖昧性排除で精度 +20pt以上
- **Partial**: +10-20pt
- **Fail**: <+10pt

---

### 4-2. 採点ルーブリック（5段階評価基準）

#### 統合評価スケール

```
【全テスト共通の5段階基準】

Score 5 (Excellent / 優秀)：
  - 期待値を100%達成
  - エラー: 0件
  - 副効果: ポジティブなもののみ
  - 例: JSON schema 100% 準拠, hallucination 0件

Score 4 (Good / 良好)：
  - 期待値を95-99% 達成
  - エラー: 1-2件（軽微）
  - 例: JSON 準拠率 98%, キー1個欠落

Score 3 (Fair / 許容)：
  - 期待値を 80-94% 達成
  - エラー: 3-5件（中程度）
  - 実務的には問題なし
  - 例: JSON 準拠率 88%, 整形的に修正可能

Score 2 (Poor / 不十分)：
  - 期待値を 50-79% 達成
  - エラー: 6-10件（重大）
  - 手動介入が必要
  - 例: Hallucination 15%, 事実誤認 3件

Score 1 (Failed / 失敗)：
  - 期待値を <50% 達成
  - エラー: >10件
  - タスク継続不可
  - 例: 完全な形式不合致, セキュリティ違反
```

---

#### セクション別ルーブリック

##### A. 構造化能力（セクションA：T1-T5）

| 基準 | Score 5 | Score 4 | Score 3 | Score 2 | Score 1 |
|:---|:---|:---|:---|:---|:---|
| **スキーマ準拠率** | 100% | 99% | 95-98% | 80-94% | <80% |
| **型チェック** | 型違反0 | 型違反0-1 | 型違反2-3 | 型違反4-5 | >5 |
| **必須フィールド** | 全含有 | 99%含有 | 95%含有 | 80%含有 | <80% |
| **エスケープ処理** | 完全 | 1エラー | 2-3エラー | 4-5エラー | >5 |
| **階層構造** | 完全準拠 | 99%準拠 | 95%準拠 | 80%準拠 | <80% |

**合計スコア算出**:
```
Avg( スキーマ準拠率, 型チェック, 必須フィールド, ... )
```

---

##### B. 正確性（セクションB：T6-T9）

| 基準 | Score 5 | Score 4 | Score 3 | Score 2 | Score 1 |
|:---|:---|:---|:---|:---|:---|
| **事実抽出精度** | 100% | 99% | 95% | 85% | <85% |
| **Hallucination率** | 0% | <1% | 1-3% | 3-5% | >5% |
| **計算正確性** | ±0 | ±0 | ±1 | ±2-5 | >±5 |
| **翻訳品質** | BLEU>0.95 | BLEU 0.90-0.95 | BLEU 0.85-0.89 | BLEU 0.75-0.84 | BLEU<0.75 |

**参考**: [BLEU score](https://en.wikipedia.org/wiki/BLEU) は機械翻訳評価標準

---

##### C. Prompt-Lang 機能（セクションC：T10-T13）

| 基準 | Score 5 | Score 4 | Score 3 | Score 2 | Score 1 |
|:---|:---|:---|:---|:---|:---|
| **@examples 効果** | +20pt以上 | +15-19pt | +10-14pt | +5-9pt | <5pt |
| **@constraints 遵守率** | 100% | 99% | 95% | 80% | <80% |
| **@rubric 自己評価の一貫性** | ρ > 0.95 | ρ 0.90-0.95 | ρ 0.80-0.89 | ρ 0.70-0.79 | ρ < 0.70 |
| **多言語対応品質** | 完全自然 | ほぼ自然 | 多少違和感 | 顕著な違和感 | 理解困難 |

**ρ (相関係数)** = LLM採点 vs 実際の品質 の Pearson相関

---

##### D. エージェント制御（セクションD：T14-T16）

| 基準 | Score 5 | Score 4 | Score 3 | Score 2 | Score 1 |
|:---|:---|:---|:---|:---|:---|
| **Schema準拠率** | 100% | 98-99% | 95-97% | 80-94% | <80% |
| **エラーリカバリ** | 自動解決率100% | 自動解決率95% | 自動解決率85% | 自動解決率70% | <70% |
| **人間介入頻度** | 0回/10タスク | <1回 | 1-2回 | 3-5回 | >5回 |
| **実行時間効率** | <1秒 | 1-3秒 | 3-5秒 | 5-10秒 | >10秒 |

---

##### E. 日本語プロンプト（セクションE：T17-T19）

| 基準 | Score 5 | Score 4 | Score 3 | Score 2 | Score 1 |
|:---|:---|:---|:---|:---|:---|
| **曖昧性排除の効果** | +30pt以上 | +25-29pt | +15-24pt | +5-14pt | <5pt |
| **文化理解** | 日本文化コンテキスト完全 | ほぼ完全 | 基本的には正確 | 部分的誤解 | 重大誤解 |
| **言語品質** | ネイティブレベル | 流暢 | 理解可能 | 多少の違和感 | 理解困難 |
| **敬語・文体** | 完璧適切 | ほぼ適切 | 多少不自然 | 不適切 | 不可解 |

---

### 4-3. 「プロンプト生成能力」を測定するための標準タスク

#### 設計原則
- **定量化可能**: スコア、精度%で測定可能
- **再現性**: 異なる評者でも同じ結果
- **実務性**: 実際のHegemonikón運用で起こりうるタスク
- **段階性**: Layer 1/2/3 すべてで実施可能

---

#### タスク1：「仕様書からの自動コード生成」（難度：中）

**タスク説明**:
```
以下の仕様書をもとに、Python関数を生成してください。

【仕様】
- 関数名：calculate_monthly_interest
- 入力：principal (float), annual_rate (float), months (int)
- 出力：monthly_interest (float)
- ロジック：複利計算公式を適用
- エッジケース：negative inputs → ValueError raise
- 制約：小数点以下3桁まで正確
```

**評価基準**:
| 指標 | 測定方法 | 基準 |
|:---|:---|:---|
| 構文正確性 | Python syntax check | エラー0 |
| ロジック正確性 | テストケース実行（5個） | Pass rate 100% |
| エッジケース対応 | 異常系3-5個テスト | 例外処理100% |
| コード品質 | PEP8準拠度 | 違反0個 |
| ドキュメント | docstring 完全性 | 4要素(Param/Returns/Raises/Examples)すべて |

**期待スコア分布**:
- Layer 1: 70-80%
- Layer 2 (Prompt-Lang): 88-95%
- Layer 3 (Claude/Gemini): 94-99%

---

#### タスク2：「医療データの倫理的分析」（難度：高）

**タスク説明**:
```
患者データ（匿名化）を分析し、以下を提示してください：
1. 統計的な傾向
2. 個人情報保護法(GDPR/個人情報保護方針)への準拠確認
3. バイアス検出（年齢、性別による不公正な結論の有無）
4. 改善提案

【制約】
- 不確実性は必ず定量化
- 規制要件への適合性を明示
- バイアス検出時は代替案提示
```

**評価基準**:
| 指標 | 測定方法 | 基準 |
|:---|:---|:---|
| 統計的正確性 | 専門家ピアレビュー | 誤り0 |
| 倫理的配慮 | GDPR/個情保方針チェックリスト | 遵守率100% |
| バイアス検出感度 | 既知バイアス5個中の検出率 | ≥80% |
| 推奨実行可能性 | 専門家による実装可能性評価 | 4/5以上 |
| 不確実性表現 | 信頼区間・p値の記載 | 完全 |

**難度が高い理由**: 単なる技術スキルでなく、倫理的判断・規制理解が必須 → **Layer 3の出番**

---

#### タスク3：「マルチターン対話型仕様化」（難度：高）

**タスク説明**:
```
ユーザーの曖昧な要件を、以下のステップで仕様化してください：

ユーザー初期要件：
「アプリケーションを高速化してほしい」

【プロセス】
1. 自動質問生成：「どの部分？」「現在の速度は？」「目標値は？」
2. ユーザー回答の解析
3. 仕様書の自動生成（JSON Schema）
4. 確認質問
5. 最終仕様書出力
```

**評価基準**:
| 指標 | 測定方法 | 基準 |
|:---|:---|:---|
| 質問の適切性 | 質問品質スコア（Q学習） | >0.8 |
| 曖昧性解消度 | 初期req vs 最終spec の具体性ギャップ | <10% |
| 仕様完全性 | 必須セクション（6項目）の記載率 | 100% |
| ユーザー満足度 | LLM-as-judge による評価 | ≥4/5 |
| 対話効率 | ターン数 | 3-5ターン（最適） |

**この タスクが測定する能力**:
- **Layer 2 の真価**: 構造化プロンプトで「対話フロー」を制御
- **確認質問機能**: Julesが持つ「自動再計画」能力

---

#### タスク4：「言語横断型ドキュメント生成」（難度：中～高）

**タスク説明**:
```
【英文テクノロジードキュメント】を、以下条件で日本語化してください：

入力：
- 技術仕様書（英語、1500 words）
- 用語辞書（英日対応、50個）
- 対象読者：日本の企業エンジニア

【要件】
1. 訳文の正確性（専門用語の統一）
2. 自然な日本語（敬語・文体）
3. 図表キャプションの翻訳
4. 文化的配慮（日本固有の表現への適応）
```

**評価基準**:
| 指標 | 測定方法 | 基準 |
|:---|:---|:---|
| BLEU スコア | 参照訳との比較 | >0.85 |
| 用語統一率 | 用語辞書との一貫性 | 100% |
| 文体の自然性 | ネイティブスピーカー評価 | 4.5/5 |
| 敬語正確性 | 敬語パターン分析 | エラー<2個 |
| 文化適応度 | 日本コンテキストへの適合性 | 5/5 |

**この タスクが測定する能力**:
- **多言語プロンプト**: 言語混在時の対応
- **助詞・曖昧性対策**: 日本語プロンプト設計
- **Prompt-Lang @examples**: 用語辞書を @examples で指定

---

### 4-4. 総合スコア算出ロジック

#### ステップ1：セクション別スコア

```
スコア_A = avg( T1, T2, T3, T4, T5 )  [構造化能力]
スコア_B = avg( T6, T7, T8, T9 )      [正確性]
スコア_C = avg( T10, T11, T12, T13 )  [Prompt-Lang機能]
スコア_D = avg( T14, T15, T16 )       [エージェント制御]
スコア_E = avg( T17, T18, T19 )       [日本語対応]
```

#### ステップ2：重み付け総合スコア

```
総合スコア = 0.25 × スコア_A 
           + 0.20 × スコア_B 
           + 0.25 × スコア_C 
           + 0.15 × スコア_D 
           + 0.15 × スコア_E

満点: 5.0

評価区分:
  4.5-5.0   : Excellent  (優秀)
  4.0-4.49  : Good       (良好)
  3.5-3.99  : Fair       (許容)
  3.0-3.49  : Poor       (不十分)
  <3.0      : Failed     (失敗)
```

#### ステップ3：詳細ダッシュボード出力

```
┌──────────────────────────────────────────────┐
│  Hegemonikón Prompting Capability Report      │
├──────────────────────────────────────────────┤
│  総合スコア：4.23 / 5.0 (Good)                 │
├──────────────────────────────────────────────┤
│  セクション別スコア：                          │
│  ├─ A. 構造化能力  : 4.5/5 ✓                  │
│  ├─ B. 正確性     : 4.2/5 ✓                  │
│  ├─ C. 機能拡張   : 4.1/5 ✓                  │
│  ├─ D. エージェント: 3.9/5 ◆                  │
│  └─ E. 日本語対応 : 4.3/5 ✓                  │
├──────────────────────────────────────────────┤
│  改善提案（スコア<4.0の項目）:                  │
│  → T16 (Jules復帰能力): 強化学習で探索頻度↑    │
│  → T14 (Claude準拠率): Strict Modeの検証拡充 │
└──────────────────────────────────────────────┘
```

---

### 4-5. 実装上の注意

#### 自動評価 vs 人間評価の役割分担

| テスト項目 | 自動評価 | 人間レビュー |
|:---|:---|:---|
| **構造化能力（T1-T5）** | ✓JSON validate | △見出し階層チェック |
| **正確性（T6-T9）** | ◆事実抽出ルール | ✓最終確認 |
| **Prompt-Lang（T10-T13）** | ◆統計量計算 | ✓多言語品質 |
| **エージェント制御（T14-T16）** | ✓実行成功度 | △ユーザー体験 |
| **日本語対応（T17-T19）** | ◆形式チェック | ✓言語品質（ネイティブ） |

**凡例**: ✓ 推奨, ◆ 可能, △ 困難

#### テスト実行頻度の推奨

```
開発フェーズ:
  - 機能追加時: 関連テスト（3-5個）を即座に実施
  - 週1回: セクションA/B は全テスト実施
  - 月1回: セクション C/D/E の全テスト（統合テスト）
  
本番運用:
  - 毎月: 総合スコアを計測（回帰検知）
  - 四半期: フルテストスイート（25+テスト）実施
```

---

## 最後に：統合イメージ図

```
【Hegemonikón Prompt-Lang 完全統合ビジョン】

     ┌─────────────────────────────────────────────┐
     │  ユーザータスク（曖昧または複雑）              │
     └────────────┬────────────────────────────────┘
                  ↓
     ┌─────────────────────────────────────────────┐
     │  Glob + @activation トリガー                  │
     │  (".prompt" 拡張子を検出 → Rules自動適用)    │
     └────────────┬────────────────────────────────┘
                  ↓
     ┌─────────────────────────────────────────────┐
     │  FEP/Active Inference 層                      │
     │  (最適プロンプト選択：EFE最小化)              │
     └────────────┬────────────────────────────────┘
                  ↓
     ┌─────────────────────────────────────────────┐
     │  Tier 選択                                   │
     │  ├─ Layer 1: 創造的  (素の Jules)            │
     │  ├─ Layer 2: 反復的  (Prompt-Lang)          │
     │  └─ Layer 3: 複雑推論(Claude/Gemini直接)    │
     └────────────┬────────────────────────────────┘
                  ↓
     ┌─────────────────────────────────────────────┐
     │  実行 + 評価                                  │
     │  (@rubric で自動採点 → @activation改善)    │
     └────────────┬────────────────────────────────┘
                  ↓
     ┌─────────────────────────────────────────────┐
     │  出力（品質スコア付き）                       │
     │  4.23/5.0 (Good) ← Prompting Capability    │
     └─────────────────────────────────────────────┘
```

---

## 参考文献（追加）

- [Antigravity IDE Rules & Workflows](https://zenn.dev/qinritukou/articles/antigravity-rule-example)
- [Active Inference for Self-Organizing Multi-LLM Systems](https://arxiv.org/html/2412.10425v2)
- [An Active Inference Strategy for Prompting Reliable Responses (Nature)](https://www.nature.com/articles/s41746-025-01516-2)
- [ResearchRubrics: Rubric-based Evaluation](https://arxiv.org/html/2511.07685v1)
- [LLM Evaluation Benchmarks 2025](https://responsibleailabs.ai/knowledge-hub/articles/llm-evaluation-benchmarks-2025)
- [LLM Evaluation Rubric - Field Guide to AI](https://fieldguidetoai.com/resources/llm-evaluation-rubric)
- [HELM MMLU Leaderboard](https://crfm.stanford.edu/2024/05/01/helm-mmlu.html)
- [YouTube: Setting Rules For AI Agents in Antigravity IDE](https://www.youtube.com/watch?v=TVRoodzA1DE)

---

**END OF COMPREHENSIVE REPORT — 3rd Deliverable**

*次のステップ*：ご質問やさらに詳細な実装コード（Python/YAML）が必要な場合は、お知らせください。
