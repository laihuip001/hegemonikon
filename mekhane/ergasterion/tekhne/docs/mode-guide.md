# tekhne-maker v6.0 モード解説

> OMEGA SINGULARITY BUILD — 認知拡張メタプロンプト生成システム

---

## Operating Modes 一覧

| Mode | Trigger | Output | 適性 |
|:-----|:--------|:-------|:-----|
| **Generate** | 「〇〇用のスキルを作成」 | SKILL.md + references/ | 拡散・創発的タスク |
| **Týpos** | 「Týposで」「.promptで」 | .prompt ファイル | 収束・Zero-Entropy |
| **SAGE** | 「XMLで」「SAGE形式で」 | XML/MD ハイブリッド | 構造重視・移植性 |
| **Diagnose** | 「診断して」 | スコア表 + 改善案 | 既存資産の分析 |
| **Improve** | 「改善して」 | 差分のみ | 既存資産の改善 |
| **Expansion** | `/expand` | サブモジュール | 既存スキルの深掘り |

---

## 1. Generate Mode (デフォルト)

```
Trigger: 「〇〇用のスキル/プロンプトを作成」
Output:  SKILL.md + references/
適性:    拡散・創発的タスク（アイデア生成、設計、文書作成）
```

### 特徴

- 7モジュール（M0-M6）をフル活用
- 5 Diagnostic Questions でアーキタイプ自動選択
- Internal Council による設計批評
- Pre-Mortem/WARGAME による品質保証

### 使用例

```
「コードレビュー用のスキルを作成して」
「ブログ記事作成AIを構築」
```

---

## 2. Týpos Mode

```
Trigger: 「Týposで作成」「.promptで」「.prompt ファイルを作って」
Output:  .prompt ファイル（Týpos v2.1 準拠）
適性:    収束・Zero-Entropy タスク（コード生成、データ抽出、分類）
```

### 特徴

- 必須ディレクティブ: @role, @goal, @constraints, @format, @examples
- 曖昧語禁止（「適切に」「うまく」検出）
- @rubric による自己評価軸
- 構文検証: `typos.py parse` でエラーチェック

### 使用例

```
「TýposでSQL生成スキルを作成」
「.promptでログ解析ツールを作って」
```

---

## 3. SAGE Mode (v6.0 新規)

```
Trigger: 「XMLで作成」「SAGE形式で」
Output:  XML/MD ハイブリッド形式
適性:    構造重視・移植性（他LLMへの移植、形式的仕様）
```

### 特徴

- HEPHAESTUS v9.0.1 由来の構造化形式
- `<module_config>`, `<instruction>`, `<protocol>`, `<output_template>` タグ
- 認知プロセスをステップバイステップで明示
- Claude/Gemini/GPT 間での移植が容易

### 出力構造

```xml
<module_config>
  <name>...</name>
  <objective>...</objective>
</module_config>

<instruction>
  <protocol>
    <step_1_analysis>...</step_1_analysis>
    <step_2_synthesis>...</step_2_synthesis>
  </protocol>
  <constraints>...</constraints>
  <output_template>...</output_template>
</instruction>
```

### 使用例

```
「SAGE形式で統合監査スキルを作成」
「XMLでマルチエージェント調整プロンプトを作って」
```

---

## 4. Diagnose Mode

```
Trigger: 「このプロンプトを診断」「診断して」
Output:  スコア表 + 優先度順改善案
適性:    既存資産の分析
```

### 特徴

- 品質スコア算出（構造、明確性、網羅性など）
- 優先度順の改善ポイント
- アンチパターン検出
- アーキタイプ適合度評価

### 使用例

```
「このプロンプトを診断して」[ファイル添付]
「以下のSKILL.mdを評価して」
```

---

## 5. Improve Mode

```
Trigger: 「このプロンプトを改善」「改善して」
Output:  差分のみ提示
適性:    既存資産の改善
```

### 特徴

- 全体を再生成しない（トークン効率）
- 変更箇所のみをdiff形式で提示
- 理由付きの改善提案

### 使用例

```
「このプロンプトを改善して」[ファイル添付]
「診断結果に基づいて改善版を出して」
```

---

## 6. Expansion Generator (v6.0 新規)

```
Trigger: `/expand`「拡張モジュールを追加」
Output:  1-2個のサブモジュール
適性:    既存スキルの深掘り・エッジケースカバー
```

### 特徴

- メインスキル生成後に追加提案
- タスク種別に応じた拡張テンプレート
- エッジケース、深掘り分析をカバー

### 拡張テンプレート

| タスク種別 | 拡張候補 |
|:-----------|:---------|
| Coding | Security Audit, Performance Profiler |
| Writing | Tone Polisher, SEO Optimization |
| Strategy | Devil's Advocate, Implementation Roadmap |
| Analysis | Edge Case Finder, Anomaly Detector |

### 使用例

```
「/expand O1 Noēsis」
「このスキルにセキュリティ監査モジュールを追加」
```

---

## 内部メカニズム

### RECURSIVE_CORE (3層処理)

```
Layer 1: EXPANSION (拡散)
  → 変数・制約の網羅的列挙

Layer 2: CONFLICT (対立)
  → Internal Council 議論
  → Red Team 攻撃

Layer 3: CONVERGENCE (収束)
  → Ockham's Razor 蒸留
  → Artifact 形成
```

### Internal Council

| Voice | Role | Question |
|:------|:-----|:---------|
| LOGIC | Pure Compiler | 「これは論理的に正しいか？」 |
| EMOTION | Limbic System | 「これは Creator を傷つけるか？」 |
| HISTORY | Phantom Timeline | 「以前これを試した時、何が起きた？」 |

### 準備強制ゲート

> Layer 2 完了まで Layer 3 進行をブロック。
> 「早く実装したい」は許されない。**準備8割・実装2割**。

---

## 参照資料

| File | Content |
|:-----|:--------|
| `references/archetypes.md` | 5アーキタイプ詳細 |
| `references/sage-blueprint.md` | SAGE形式テンプレート |
| `references/expansion-templates.md` | 拡張モジュールテンプレート |
| `references/typos-templates/` | Týpos テンプレート集 |
| `references/cognitive-armory.md` | 思考フレームワーク |

---

*tekhne-maker v6.0 OMEGA SINGULARITY BUILD*
*Last Updated: 2026-01-28*
