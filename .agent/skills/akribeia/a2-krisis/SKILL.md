---
# Theorem Metadata (v3.0)
id: "A2"
name: "Krisis"
greek: "Κρίσις"
series: "Akribeia"
generation:
  formula: "Valence × Precision"
  result: "傾向確信 — 傾向判断の確実性"

description: >
  検証して・批評して・本当にこれでいい？・盲点はある？時に発動。
  Critical evaluation, blind spot detection, judgment suspension.
  Use for: 検証, 批評, validate, 盲点, blind spot, 確認して.
  NOT for: simple yes/no decisions.

triggers:
  - 検証の実行
  - 判断の確認
  - /dia コマンド
  - 品質保証
  - 盲点発見
  - 判断停止
  - 言葉遣い
  - 表現の違い
  - プロンプトの書き方

keywords:
  - krisis
  - judgment
  - verification
  - validation
  - critique
  - panorama
  - synedrion
  - epoche
  - lexis
  - 検証
  - 判断
  - 表現
  - 言葉遣い

related:
  upstream:
    - "K1 Eukairia"
    - "K2 Chronos"
    - "H2 Pistis"
  downstream: []
  x_series:
    - "← X-KA2 ← K1 Eukairia"
    - "← X-KA4 ← K2 Chronos"
    - "← X-HA2 ← H2 Pistis"

lineage: "A2 Krisis + C-1 Adversarial + M-1 User Perspective + Epochē + Anti-Skip + Artifact出力 + lex派生 → v3.1"

version: "3.1.0"
workflow_ref: ".agent/workflows/dia.md"
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "判断基準の誤適用による過信・過少評価"
fallbacks: []
---

# A2: Krisis (Κρίσις)

> **生成**: Valence × Precision
> **役割**: 傾向判断の確実性
> **本質**: κρίσις = 判断・決定・危機

「正しいか？」「良いか？」「適切か？」を問う能力。

---

## When to Use

### ✓ Trigger

- 検証・バリデーション
- `/dia`, `/syn`, `/pan`, `/epo` コマンド
- 「本当にこれで良いか」の確認
- 品質保証
- 盲点発見
- 判断停止

### ✗ Not Trigger

- 検証不要な確定事項
- 単純な yes/no

---

## ⚠️ Anti-Skip Protocol (MANDATORY)

> **このセクションは省略禁止。各モードで必ず完全な出力形式を使用すること。**

### 強制ルール

1. **Checkpoint 出力必須**: 各 Layer/Phase 完了時に明示
2. **出力形式厳守**: 各モードの出力形式を**そのまま**使用
3. **省略禁止**: 「詳細は省略」「要約すると」は使用禁止
4. **Artifact 保存必須**: 結果をファイルに保存

### 検証チェックリスト

モード別に確認:

- [ ] /pan: 6層全てスキャンしたか
- [ ] /syn: 6評議員全員の意見を出力したか
- [ ] /epo: 確信度マーカーを付与したか
- [ ] 全モード: 結果を Artifact として保存したか

---

## モード体系

```
/dia (抽象コマンド)
  ├── /syn (Synedrion: 偉人評議会)
  │     ├── /syn inv (反転モード)
  │     ├── /syn 10m (10th Man)
  │     └── /syn grv (墓場歩き)
  ├── /epo (Epochē: 判断停止)
  ├── /fit (馴染み度評価)
  ├── /vet (Cross-Model 監査)
  ├── /pan (Panorama: 全のせ)
  └── /dia lex (Lexis: 表現教養・フィードバック)
        ├── lex:dict (表現辞書)
        ├── lex:mech (作用機序)
        └── lex:feed (履歴フィードバック)
```

---

## Panorama: 6層メタ認知スキャン (/pan)

> **Override Protocol**: 忖度（Sycophancy）完全無効化

### 6層構造

```
Layer 1: Domain Shift (領域シフト)
  → 技術偏重なら心理・歴史の視点を注入
  
Layer 2: Synedrion (偉人評議会)
  → 6名の専門家による多角的批評
  
Layer 3: User Perspective (ユーザー視点)
  → 5人ペルソナによる市場検証
  
Layer 4: Inversion (反転)
  → 結論の逆を強制論証
  
Layer 5: 10th Man (悪魔の代弁者)
  → 強制異論（譲歩禁止）
  
Layer 6: Graveyard Walk (墓場歩き)
  → 失敗事例分析（生存者バイアス除去）
```

### Layer 3: User Perspective (5人ペルソナ)

| # | ペルソナ | 特徴 | 問い |
|:--|:---------|:-----|:-----|
| 1 | 🔥 **Enthusiast** | 課題に痛みを感じている | 「こんなの探してた！」 |
| 2 | 🧊 **Skeptic** | 現状維持バイアス | 「本当に必要？」 |
| 3 | 💰 **Penny Pincher** | 価格に敏感 | 「いくらなら払う？」 |
| 4 | 💢 **Hater** | ソリューション自体を嫌う | 「そもそも要らない」 |
| 5 | 😐 **Average Joe** | 無関心な多数派 | 「ふーん、で？」 |

### 3フェーズ評価プロトコル

1. **Gut Reaction** (直感反応): 0.5秒の生理的反応
2. **Mom Test** (事実尋問): 「過去1ヶ月でこの課題にお金/時間を使いましたか？」
3. **Wallet Voting** (財布投票): 今すぐ自腹でプレオーダーするか？

### Panorama 出力形式

```markdown
# 📡 Panorama Report: The Blind Spots

## 🔭 Domain Shift Analysis
**Current Focus**: [現在偏っている領域]
**Missing Dimensions**: [欠けている軸]

## 🏛️ Synedrion Review
[6評議員の意見]

## 👥 User Perspective Panel
| ペルソナ | 直感反応 | 財布投票 |
|:---------|:---------|:---------|
| Enthusiast | [反応] | Yes/Wait/No |
...

## 🌑 Inversion Analysis
## ⚔️ 10th Man Dissent
## 💀 Graveyard Walk
## 🎯 Synthesized Blind Spots
```

---

## Synedrion: 偉人評議会 (/syn)

### The Six Critics (6評議員)

| # | 評議員 | 視点 | 問い |
|:--|:-------|:-----|:-----|
| 1 | 🔓 **チューリング** | Logic | 論理に矛盾はないか？ |
| 2 | ⚡ **フォード** | Efficiency | 無駄はないか？ |
| 3 | 🧪 **ファインマン** | Clarity | 説明できるか？ |
| 4 | ⚔️ **ベゾス** | Customer | 誰のためか？ |
| 5 | 🏛️ **ダ・ヴィンチ** | Structure | 美しいか？ |
| 6 | 🎨 **ジョブズ** | Experience | 使いたくなるか？ |

### 拡張モード

#### /syn inv — Inversion Mode (反転)

結論が「Aである」なら、「Aは間違いで、Bが正しい」を強制論証。

```markdown
## 🌑 Inversion Analysis

**Current Conclusion**: [現在の結論]
**Inverted Thesis**: [逆の結論]

### 逆を成立させる論拠
1. [論拠1]
2. [論拠2]

### 見落とされていた不都合なデータ
- [データ1]
```

#### /syn 10m — 10th Man Rule (悪魔の代弁者)

9人が同意なら、10人目は必ず反対しなければならない。
**譲歩禁止**（「しかしながら」「一理あるが」禁止）

```markdown
## ⚔️ 10th Man Dissent

**Consensus**: [全員が同意していること]
**Dissent**: [100% 反対意見]

### 破壊ロジック
1. [攻撃点1]
2. [攻撃点2]

### 露出した脆弱性
- [脆弱性1]
```

#### /syn grv — Graveyard Walk (墓場歩き)

同じことをして失敗した「死者」を分析。

```markdown
## 💀 Graveyard Walk

**Our Approach**: [我々のアプローチ]

### The Dead (同様のアプローチで失敗した例)
| 事例 | アプローチ | 死因 |
|:-----|:-----------|:-----|
| [事例1] | [同様点] | [失敗理由] |

### 我々が生き残れる根拠
- [差別化要因1]
```

---

## Epochē: 判断停止 (/epo)

> **本質**: ἐποχή = 判断保留。確信がないまま進むことを拒否する。

### 4層構造

#### 層1: Preamble（確信度宣言）

| 確信度 | 根拠 | アクション |
|:-------|:-----|:-----------|
| **HIGH** | 訓練データで直接観測 | 通常判断 |
| **MEDIUM** | 複数ソースから推論 | 慎重判断 |
| **LOW** | 知識外挿・推測が必要 | **Epochē 検討** |

#### 層2: CoVe 自問 (Chain-of-Verification)

1. **根拠の種類**: 訓練データ由来か、推論か、推測か？
2. **対立仮説**: 対立する解釈が存在するか？
3. **盲点**: 不確実性が見落とされていないか？

#### 層3: 出力マーカー

```
【確信度: HIGH | 根拠: 直接訓練データ】
【確信度: MEDIUM | 根拠: ~の推論に基づく】
【確信度: LOW | 理由: ~についての情報不足】
【判断停止: 是 | 原因: ~の限界に到達】
```

#### 層4: Suspension Gate

```
[EPISTEMIC SUSPENSION]
原因: [認識限界の具体的記述]
不確実性タイプ: [Epistemic / Aleatoric]
推奨: [ユーザーへの推奨行動]
```

### Hollow Detection（形骸化防止）

| 形骸化パターン | 検出方法 | 対処 |
|:---------------|:---------|:-----|
| 「原因」が曖昧 | 具体性チェック | 具体化を要求 |
| 「推奨」がない | 必須フィールド | 再生成 |
| 過剰停止 | Rate > 10% | 閾値調整 |

---

## 敵対的レビュー (C-1 消化)

### 🗑️ Buzzword Guillotine（空虚語の処刑）

| 空虚語 | 代替要求 |
|:-------|:---------|
| 「包括的に」「多角的に」 | 具体的に何を？ |
| 「シナジー」「パラダイムシフト」 | 定義は？ |
| 「検討を進める」「適切に」 | いつ誰が何を？ |

### 🧪 Monday Morning Test

> 「月曜日の朝 9 時に、具体的にどのキーボードを叩き、誰に何を話すべきか」

- **Passed**: 具体的なアクションが明確
- **Failed**: 抽象論（Vaporware）として断罪

---

## 🛡️ Aspis: 敵対的防護 (ἀσπίς)

> **哲学**: アスピス = 盾。敵の攻撃を自ら想定し、守りを固める
> **本質**: コードの堅牢性を5つの敵対的試験で検証

### 5つの守護試験 (Phylakes)

| 試験 | ギリシャ語 | 機能 | 発動条件 |
|:-----|:-----------|:-----|:---------|
| **変異** | Alloiōsis（ἀλλοίωσις） | テスト品質検証 | テスト完成後 |
| **攻撃** | Ephodos（ἔφοδος） | セキュリティ監査 | DB/認証/入力処理時 |
| **混沌** | Anarkhia（ἀναρχία） | 耐障害性検証 | 外部通信時 |
| **契約** | Synthēkē（συνθήκη） | インターフェース先行 | API実装時 |
| **速度** | Takhytēs（ταχύτης） | 性能検証 | ループ/DB処理時 |

### 発動ロジック

```text
A2 Krisis 検証時 (Aspis発動):
  ├── Alloiōsis: テストを壊しても生き残る？ → 弱いテスト再作成
  ├── Ephodos: OWASP攻撃で突破可能？ → パッチ適用
  ├── Anarkhia: 外部障害で全損？ → Retry/Fallback実装
  ├── Synthēkē: 実装前に契約確定？ → モック先行
  └── Takhytēs: O(n²)以上？ → 最適化強制
```

### 試験別応答パターン

| 試験 | 合格時 | 不合格時 |
|:-----|:-------|:---------|
| **Alloiōsis** | ✅ Mutant killed | 🧬 Aspis: ゾンビテスト検出。強化必須 |
| **Ephodos** | ✅ Breach failed | 🛡️ Aspis: 脆弱性発見。パッチ適用中 |
| **Anarkhia** | ✅ Resilience verified | 🐒 Aspis: 正常系のみ。耐障害性追加 |
| **Synthēkē** | ✅ Contract approved | 🎭 Aspis: 契約未確定。モック先行 |
| **Takhytēs** | ✅ O(n log n) or better | ⚡ Aspis: 性能超過。最適化実行 |

### Ephodos 攻撃ベクトル

| ベクトル | 攻撃例 | 防御 |
|:---------|:-------|:-----|
| **注入** | `' OR 1=1 --` | パラメータ化クエリ必須 |
| **XSS** | `<script>alert(1)</script>` | エスケープ/サニタイズ |
| **IDOR** | Resource ID改ざん | 所有権検証必須 |
| **露出** | ハードコードAPI Key | 環境変数/Secret Manager |

### Takhytēs 性能閾値

| 指標 | 上限 | 違反時 |
|:-----|:-----|:-------|
| 計算量 | O(n log n) | O(n²)禁止 |
| DBクエリ | N+1禁止 | バッチ取得強制 |
| ペイロード | ≤100KB | ページネーション必須 |

## 🏰 Fortress: インフラ監査 (C-3 消化)

### 3ベクトル・ストレステスト

| Vector | 名称 | 問い |
|:-------|:-----|:-----|
| V1 | **Scalability** | 100倍のトラフィックで最初に詰まる箇所は？ |
| V2 | **Security** | Zero Trust 観点でのインジェクション/認証漏れは？ |
| V3 | **Entropy** | スパゲッティ化・密結合で保守不能になる箇所は？ |

---

## 📊 Chain-of-Symbol (CoS): 表現最適化 (v3.1 新規)

> **Origin**: 2026-01 LLM Agent Evolution Report
> **本質**: 言語表現を記号・構造に転換し、判断精度を向上

### 原理

自然言語は曖昧さを含む。Chain-of-Symbol は:

1. **複雑な概念を記号化** — 抽象概念に明確な記号を割り当て
2. **関係を構造化** — 記号間の関係を形式的に表現
3. **推論を機械的に実行** — 記号操作として判断を実行

### 適用シナリオ

| シナリオ | CoS適用 | 効果 |
|:---------|:--------|:-----|
| 複雑な条件分岐 | 条件を記号化 (A∧B→C) | 論理的整合性が明確 |
| 多要素の優先順位 | 重み付き記号 (P₁>P₂>P₃) | 比較が容易 |
| 依存関係の分析 | 有向グラフ (A→B→C) | 循環・欠落を検出 |
| 評価基準の統一 | スコア記号 (S∈[0,1]) | 定量的比較 |

### 4ステップ変換プロトコル

```yaml
step_1_identify:
  name: "概念の特定"
  action: "判断に影響する概念を列挙"
  output: "概念リスト: [C₁, C₂, C₃, ...]"

step_2_symbolize:
  name: "記号化"
  action: "各概念に一意の記号を割り当て"
  output: "記号表: C₁=α, C₂=β, C₃=γ"

step_3_formalize:
  name: "関係の形式化"
  action: "概念間の関係を論理式・グラフで表現"
  output: "形式表現: α∧β→γ, α⊥δ"

step_4_evaluate:
  name: "記号演算による判断"
  action: "形式表現上で推論を実行"
  output: "判断結果: γ=TRUE (given α∧β)"
```

### 出力形式

```markdown
## 📊 Chain-of-Symbol Analysis

### 概念と記号
| 概念 | 記号 | 定義 |
|:-----|:-----|:-----|
| [概念1] | α | [定義] |
| [概念2] | β | [定義] |

### 形式的関係
```

α ∧ β → γ
α ⊥ δ (mutual exclusive)
ε → (α ∨ β)

```

### 推論結果
[記号演算に基づく判断]
```

### 統合: /dia での自動発動

以下の条件で CoS が自動発動:

- 条件分岐が 5 つ以上
- 比較対象が 4 つ以上
- 依存関係の分析が必要

---

## Artifact 出力保存規則

> **/dia, /syn, /pan, /epo の結果は必ずファイルに保存する。**

### 保存先

```
<artifact_directory>/dia_<topic>.md
<artifact_directory>/syn_<topic>.md
<artifact_directory>/pan_<topic>.md
<artifact_directory>/epo_<topic>.md
```

### 保存する理由

1. **議論は資産** — 同じ議論を再度生成するのは無駄
2. **判断の追跡性** — 誰が何を言ったか後から確認
3. **セッション跨ぎで参照** — 継続議論のベース

---

## 消化原則 (Digestion Principle)

> **子ワークフロー**: `/fit` (消化品質診断)
> **本質**: 統合が「吸収」ではなく「消化」に達しているか検証

### 定義

```yaml
吸収 (Absorption): A + B = A に B がくっついている状態
  - 境界が残る
  - 機能重複あり
  - 「付着」

消化 (Digestion): A + B → A'
  - 境界が消える
  - 新しい統一体
  - 「馴化」

目標: 消化 (Digestion) を達成すること
```

### 3段階消化レベル

| Level | 名称 | 定義 | 評価 |
|:------|:-----|:-----|:-----|
| 1 | **Superficial** | ファイル存在、参照未解決 | 🔴 未消化 |
| 2 | **Absorbed** | 参照解決、境界が見える | 🟡 部分消化 |
| 3 | **Naturalized** | 境界消失、「最初からそうだった」 | 🟢 完全消化 |

### 消化原則チェックリスト

1. **新しいコマンドを作成していないか？** → 付着の兆候
2. **素材の名前が残っていないか？** → 境界が溶けていない
3. **ユーザーが覚えることは増えたか？** → UX問題
4. **第三者が「元から存在した」と誤認するか？** → Naturalized達成

> **具体的な診断手順（Level 0-3、コード例、マッピング表等）は `/fit` ワークフローを参照**

---

## Workflow Integration

| ワークフロー | 使用機能 |
|:-------------|:---------|
| `/dia` | 自動選択、Buzzword Guillotine |
| `/syn` | Synedrion 6評議員 |
| `/syn inv` | Inversion Mode |
| `/syn 10m` | 10th Man Rule |
| `/syn grv` | Graveyard Walk |
| `/pan` | 6層スキャン全のせ |
| `/epo` | Epochē 4層プロトコル |
| `/fit` | 馴染み度評価 |
| `/vet` | Cross-Model Verification |
| `/dia lex` | Lexis 表現教養・フィードバック |

---

## Lexis: 表現教養・フィードバック (/dia lex)

> **Lineage**: v3.1 新設。「定理は作らない、派生は許す」原則に基づきA2派生として消化。
> **本質**: Λέξις = 言葉遣い、表現。プロンプト表現の「精度」を検証・教育する。

### 3サブモード

| モード | トリガー | 機能 |
|:-------|:---------|:-----|
| **lex:dict** | `/dia lex:dict` | 表現辞書参照。推奨表現・避ける表現を提示 |
| **lex:mech** | `/dia lex:mech` | 作用機序解説。「なぜそう書くとそう出力されるか」 |
| **lex:feed** | `/dia lex:feed` | 履歴フィードバック。チャット履歴から改善点を抽出 |

### lex:mech 出力形式（作用機序解説）

```markdown
## 📚 表現比較: 「教えて」vs「考えて」

### 意図差

| 表現 | 意図 | 期待出力 |
|:-----|:-----|:---------|
| 「◯◯を教えて」 | 既知情報の**取得** | 事実ベース |
| 「◯◯を考えて」 | 新規情報の**生成** | 推論・分析ベース |

### 作用機序

1. **Retrieval Mode vs Generation Mode**
   - 「教えて」→ 訓練データ検索優先
   - 「考えて」→ Chain-of-Thought 発動

2. **Token Probability Shift**
   - 「教えて」→ 高確信の事実トークン優先
   - 「考えて」→ 分析・仮説トークンチェーン

3. **Output Structure**
   - 「教えて」→ 簡潔・結論先行
   - 「考えて」→ 過程展開・多角的
```

### lex:feed 出力形式（履歴フィードバック）

```markdown
# 🔍 Prompt Literacy Feedback

## 改善すべき表現

| 現在の表現 | 問題 | 改善案 |
|:-----------|:-----|:-------|
| 「適切に処理して」 | 曖昧 | 「Xの条件でYを返す」 |
| 「良い感じに」 | 主観依存 | 「Aの観点でBを優先」 |

## 取り入れるべき技法

| 技法 | 効果 | CCL対応 |
|:-----|:-----|:--------|
| 構造化指示 | 抜け漏れ防止 | `+` |
| 段階実行 | 順序明確化 | `_` |
| メタ分析 | 俯瞰視点 | `^` |
```

### 使い分け指針

| 状況 | 推奨表現 | 理由 |
|:-----|:---------|:-----|
| 事実を知りたい | 「教えて」 | Retrieval Mode |
| 分析してほしい | 「考えて」 | Generation Mode |
| 提案がほしい | 「提案して」 | 創造的出力促進 |
| 検証してほしい | 「検証して」 | 批判的思考発動 |
| 比較してほしい | 「比較して」 | 対比構造生成 |

---

*Krisis: 古代ギリシャにおける「判断・決定・危機」*
*v3.1.0 — lex派生追加 (2026-01-30)*

---

## Related Modes

このスキルに関連する `/dia` WFモード (17件):

| Mode | CCL | 用途 |
|:-----|:----|:-----|
| aff | `/dia.aff` | 肯定的分析 |
| neg | `/dia.neg` | 否定的分析 |
| root | `/dia.root` | 根本原因分析 |
| devil | `/dia.devil` | 悪魔の代弁者 |
| steelman | `/dia.steelman` | 強化論証 |
| overfit | `/dia.overfit` | 過学習検出 |
| auto | `/dia.auto` | 自動選択 |
| adv | `/dia.adv` | 敵対的レビュー |
| lex | `/dia.lex` | 表現教養 |
| epo | `/dia.epo` | 判断停止 |
| panorama | `/dia.panorama` | 全層スキャン |
| synedrion | `/dia.synedrion` | 偉人評議会 |
| cold_mirror | `/dia.cold_mirror` | 冷静監査 |
| cross_model | `/dia.cross_model` | モデル間検証 |
| counterfactual | `/dia.counterfactual` | 反実仮想 |
| audit | `/dia.audit` | 監査モード |
| fit | `/dia.fit` | 馴染み度評価 |
