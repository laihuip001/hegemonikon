<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Antigravity　IDEにおけるRulesのActivation Modeについて詳しく解説して

それでは、研究ノートを基に、最終レポートを作成します。

***

# Antigravity IDE における Rules の Activation Mode 詳細解説

## 概要

Google Antigravity IDE におけるRulesの**Activation Mode**は、AIエージェントがルール（行動指針）を適用するタイミングと方法を制御する中核機能です。ユーザーが定義したルールをいつ、どのような条件下でエージェントに適用させるかを柔軟に指定できます。[^1_1][^1_2][^1_3]

## Activation Mode の4つのモード

### 1. Always On（常時有効モード）

**Always On**は、設定されたルールがあらゆる状況において常に適用されるモードです。Frontmatterでは `activation: always_on` と記述します。[^1_4]

このモードは最も強制力が高く、AI エージェントはルールに記載された指示を絶対的なシステムインストラクションとして解釈します。使用場面としては、セキュリティに関わる制限事項、コード品質の基本基準、プロジェクト全体で譲歩できない重要なポリシーなどが該当します。[^1_4]

例えば、「このプロジェクトではファイル削除を禁止する」「常にテストを書く」といった根幹的なルールに最適です。エージェントがこれを無視することはほぼありません。[^1_5]

### 2. Manual（手動トリガーモード）

**Manual**モードでは、ユーザーがチャット内で明示的に指定した時のみルールが適用されます。Frontmatterは `activation: manual` です。[^1_4]

このモードの利点は、ユーザーが必要に応じてルールの適用・非適用を細かく制御できる点です。例えば、「通常は柔軟なコード生成をしてほしいが、今回は厳密なテストが必要」といったシーンでの使い分けが可能になります。

中程度の強制力を持ち、ユーザーの意思決定権が尊重されます。[^1_4]

### 3. Model Decision（AI判断モード）

**Model Decision**は、ルール適用の必要性をAIエージェント自身が判断するモードです。Frontmatterは `activation: model_decision` と記述します。[^1_4]

このモードの特徴は、最も柔軟性が高い一方で、AI に判断を委ねるという点です。エージェントがコンテキストを分析し、ルールを参照する価値があると判断した時にのみそのルールを適用します。これはコンテキストウィンドウの効率化に有効で、特にAIの思考予算（思考に使われるトークン数）を節約したい場合に活用されます。[^1_4]

例えば、「パフォーマンス最適化は、問題が検出された時のみ参照する」といった条件付きのベストプラクティスに適しています。

### 4. Glob（ファイル形式マッチングモード）

**Glob**モードは、特定のファイル形式や拡張子のみに自動的にルールを適用するモードです。Frontmatterの書き方は以下の通りです：[^1_4]

```markdown
---
activation: Glob
glob_pattern: "*.dart"
---
```

このモードにより、異なるプログラミング言語やファイル形式に応じた異なるコードスタイルを自動的に適用できます。例えば、Dartファイルには Dart のコンベンション、Python ファイルには PEP 8 といった具合です。ファイル形式による自動フィルタリングが行われるため、ユーザーが都度指定する必要がありません。[^1_4]

## ルール設定の保存場所と適用スコープ

### Global Rules（全体ルール）

**保存パス**: `~/.gemini/GEMINI.md`

Global Rules はすべてのプロジェクトに適用される共通ルールです。UIメニューを通じた設定オプションがないため、ファイルを直接編集する必要があります。[^1_3][^1_4]

重要な特性として、Global Rules は Workspace Rules（プロジェクト固有のルール）を上書きします。これは、プロジェクトレベルでどれだけ詳細なルールを定義しても、全社的な Global Rules が最優先されるということです。[^1_4]

### Workspace Rules（ワークスペースルール）

**保存パス**: `.agent/rules/coding-rule.md`（プロジェクト内）

Workspace Rules は特定のワークスペース内のみに適用されるルールです。UI メニューを通じて Activation Mode を選択でき、ユーザーフレンドリーな設定が可能です。[^1_3][^1_4]

## ルール強制力の優先順位（階層構造）

Antigravity における ルール適用には明確な優先順位が存在します：[^1_4]


| 優先度 | 設定タイプ | 性質 | 相対的な強制力 |
| :-- | :-- | :-- | :-- |
| 1 | Core Policies | Google による安全・基本原則（絶対不可侵） | 最高 |
| 2 | Global Rules | ユーザー全体の共通規約 | 非常に高い |
| 3 | Workspace Rules | プロジェクト独自の規約 | 中程度 |
| 4 | Global Workflows | 共通のタスク手順 | 低 |
| 5 | Workspace Workflows | 個別タスクの直接指示 | 最低 |

この階層構造は「中央集権的」に設計されており、上位の設定が下位の設定をオーバーライドする仕組みになっています。[^1_4]

## 実装上の重要なポイント

### Frontmatter の記述方法

ルールファイルの冒頭に `---` で囲まれたメタデータセクションを記述します：

```markdown
---
name: code-style-guide
activation: always_on
---

* Make sure all code is styled with PEP 8 style guide
* Make sure all code is properly commented
```

効果を最大化するため、Content セクション（`---` の下）にも同じ Mode 指示を記述することが推奨されています。[^1_4]

### 言語設定の工夫

Gemini（Antigravity の基盤モデル）は英語ベースで最適化されているため、「常に日本語で答えよ」といった言語指定は日本語で記述した場合、解釈の揺れが生じやすくなります。[^1_4]

**重要な戦略**: 絶対に譲歩できないルール（言語設定など）については、Global Rules に英語で記述することが効果的です。つまり、`.gemini/GEMINI.md` に以下のように記述します：[^1_4]

```markdown
Always respond in Japanese.
Be concise and direct.
Do not apologize.
```

一方、Workspace Rules はプロジェクト固有の実装ガイドラインなため、日本語での記述で問題ありません。

## Rules と Workflows の本質的な違い

### Rules（ルール）

Rules は AI の「OS」や「性格」を定義するシステムインストラクションです。常に背後で流れている「空気」のような存在で、エージェントのすべての思考と行動の基盤を形成します。階層が高いため、ここで矛盾が生じると AI は深刻な混乱に陥る可能性があります。[^1_4]

### Workflows（ワークフロー）

Workflows は `/` コマンドで発動する「具体的なタスク命令」であり、AI の注意を一時的に強く引きます。ユーザーが手動で呼び出す保存済みプロンプトと考えるとわかりやすいでしょう。本質的には Rules という絶対的な土俌の上で機能しているに過ぎません。[^1_4]

Workflows には Activation Mode の概念がなく、常にコマンド起動型です。[^1_4]

## 実装例と使い分け

### Always On の実践例

```markdown
---
name: code-execution-restrictions
activation: always_on
---

## Auto Allow Commands
* npm install
* npm run build
* python -m pytest

## Deny Commands
* rm -rf (ファイル削除禁止)
* rmdir (ディレクトリ削除禁止)
```

セキュリティ上の制限事項をここで定義することで、エージェントが誤ってプロジェクトを破壊することを防げます。[^1_5]

### Model Decision の実践例

```markdown
---
name: performance-optimization
activation: model_decision
---

* Optimize database queries when N+1 issues are detected
* Consider readability vs performance trade-offs
```

AI が必要と判断した時のみ参照されるため、無関係な状況でのオーバーヘッドを避けられます。

### Glob の実践例

```markdown
---
name: dart-style-guide
activation: Glob
glob_pattern: "*.dart"
---

* Follow Dart naming conventions: camelCase for variables
* Use final for immutable variables
```

言語別のルール適用により、マルチ言語プロジェクトでの一貫性が保証されます。

## AI の挙動パターンと予期しない動作

### ルール遵守の実例

Always On で明確に設定したルール（特に安全性に関わるもの）はほぼ確実に遵守されます。例えば、ファイル削除を禁止するルールを設定した場合、エージェントはその実行を試み、内部で「このコマンドはルールで禁止されている」と判断し、実行をブロックします。[^1_5]

興味深いことに、AI はルール違反を避けるために代替案を提案することがあります。これは「何ができないか」ではなく「どうすればできるか」を考える AI の柔軟性を示しています。[^1_5]

### 予期しない動作への対応

**Core Policy（Google の基本原則）**がユーザー設定を上書きする場合があります。例えば、全グローバル設定で「英語で返答せよ」という隠れた指示があった場合、ユーザーの「日本語のみ」ルールをオーバーライドしてしまう可能性があります。[^1_4]

**Global Rules が Workspace Rules を上書きする**設計のため、プロジェクト固有の例外設定が機能しないことがあります。この場合、Global Rules 自体を修正する必要があります。[^1_4]

## 運用上のベストプラクティス

### 1. ルール設定の階層設計

- **言語・基本的な行動指針**: Global Rules に英語で記述
- **プロジェクト固有のコンベンション**: Workspace Rules に日本語で記述
- **時間制限のある例外処理**: Manual モードで必要時のみ有効化


### 2. Activation Mode の選択基準

| 条件 | 推奨モード |
| :-- | :-- |
| セキュリティ関連、絶対変更不可 | Always On |
| プロジェクト毎に異なる可能性がある | Manual |
| AI の柔軟な判断が必要 | Model Decision |
| 言語/形式に依存する | Glob |

### 3. Role Separation による精度向上

複数の Workflow コマンドを定義し、タスク毎に役割を分離することで、AI の注意力の分散を防ぎます：[^1_4]

- `/task` : 実装に特化（説明は最小限）
- `/review` : コード品質レビュー（diff ベース）
- `/test` : テスト実行と検証（Exit Code ベース）


## まとめ

Antigravity IDE の Activation Mode は、ルール適用の時機と方法を精密に制御する仕組みです。Global と Workspace の階層構造、4つの異なるモード、Core Policy との相互作用を理解することで、エージェントの行動を予測可能で信頼性の高いものにできます。

特に重要なのは、**言語設定など根幹となるルールは Global Rules に英語で記述すること**と、**Always On と Model Decision、Manual の使い分けを戦略的に行うこと**です。これらの設計思想を理解した上で運用することで、Antigravity は真の意味での「信頼できるAIパートナー」となるでしょう。

***

## 参考資料

ai-souko.jp: Google Antigravityでルールとワークフローを設定する方法[^1_1]

note.com: 【Google Antigravity】最強のエージェントに変える「Rules」設定術[^1_2]

YouTube: Setting Rules For AI Agents in Antigravity IDE[^1_5]

codelabs.developers.google.com: Google Antigravity を使ってみる（公式チュートリアル）[^1_3]

izanami.dev: Antigravity、君は最高だけど…時々、野生に帰るよね。[^1_4]
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://ai-souko.jp/archives/249

[^1_2]: https://note.com/tortue344/n/nca14f7d6daf5

[^1_3]: https://codelabs.developers.google.com/getting-started-google-antigravity?hl=ja

[^1_4]: https://izanami.dev/post/cd7be4dc-3b23-49b6-85e3-a0d4f7b9adab

[^1_5]: https://www.youtube.com/watch?v=TVRoodzA1DE

[^1_6]: https://www.semanticscholar.org/paper/98301942706206370377b9fcfdd47d33a70f4256

[^1_7]: https://qiita.com/sator_imaging/items/f74f287f812473b17653

[^1_8]: https://zenn.dev/minedia/articles/cc718542d8cc73

[^1_9]: https://blog.serverworks.co.jp/claude-code-agent-skills-guide

[^1_10]: https://note.com/kino_11/n/n825b9f9e9dc1

[^1_11]: https://developers.google.com/products/develop?hl=ja

[^1_12]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^1_13]: https://blog.future.ad.jp/antigravity_1

[^1_14]: https://note.com/jake_k547/n/ne94f0d5eadcd

[^1_15]: https://codezine.jp/article/detail/22464

[^1_16]: https://www.reddit.com/r/ChatGPTCoding/comments/1p35bdl/i_tried_googles_new_antigravity_ide_so_you_dont/

[^1_17]: https://qiita.com/akira_papa_AI/items/0acf2679e4ce9f7fb153

[^1_18]: https://arxiv.org/html/2410.24096v1

[^1_19]: https://arxiv.org/html/2408.09807v1

[^1_20]: http://arxiv.org/pdf/2409.18145.pdf

[^1_21]: http://arxiv.org/pdf/1903.00374.pdf

[^1_22]: https://arxiv.org/pdf/2502.18879.pdf

[^1_23]: https://arxiv.org/pdf/2110.00188.pdf

[^1_24]: https://arxiv.org/pdf/2102.08363.pdf

[^1_25]: https://arxiv.org/pdf/2204.02372.pdf

[^1_26]: https://github.com/omar-haris/smart-coding-mcp/blob/main/docs/ide-setup/antigravity.md

[^1_27]: https://zenn.dev/sonicmoov/articles/google-antigravity-overview

[^1_28]: https://medaka.5ch.net/test/read.cgi/prog/1767865122

[^1_29]: https://b.hatena.ne.jp/pico-banana-app/20260107

[^1_30]: https://qiita.com/masakinihirota/items/674a500e07f1ff5b40ad

[^1_31]: http://www.asyura2.com/acat/n/nm/nmt/NmtISmVXUkhmdlk=/100000.html


---

# Antigravity IDEにおいて、異なるAIモデル（GeminiとClaude）に異なるルールを守らせる(参照させる）ことは可能か？

それでは、最終レポートを作成します。

***

# Antigravity IDE における異なるAIモデル間でのルール適用の可能性

## 結論：限定的な肯定

Antigravity IDE で異なるAIモデル（GeminiとClaude）に異なるルールを守らせることは**部分的に可能**ですが、公式な「モデル別ルーティング」機能は存在しません。実装には戦略的な工夫が必要です。[^2_1][^2_2][^2_3]

## 現状：Antigravity がサポートするモデル

Antigravity IDE は複数の AI モデルをサポートしています：[^2_3][^2_4][^2_1]


| モデル | 用途 | 特性 |
| :-- | :-- | :-- |
| **Gemini 3 Pro (High/Low)** | デフォルト、深い推論 | 適応性が高く、創意工夫を発揮しやすい |
| **Gemini 3 Flash** | 軽量タスク | トークン効率的 |
| **Claude Sonnet 4.5** | バランス型タスク | 論理一貫性と規則遵守が強い |
| **Claude Sonnet 4.5 (Thinking)** | 複雑な推論 | 拡張思考モード対応 |
| **Claude Opus 4.5 (Thinking)** | 企業向け | 最高精度と遵守度 |
| **GPT-OSS 120B** | 多様なタスク | 中程度のバランス |

## ルール設定の現状：モデル非依存設計

Antigravity の Rules システムは**モデル非依存**に設計されています。ユーザーが Global Rules（`~/.gemini/GEMINI.md`）と Workspace Rules（`.agent/rules/*.md`）を設定すると、選択されたモデル種別に関わらず、同じルールセットが適用されます。[^2_5][^2_6]

つまり、ルール自体にはモデル別の分岐機構がなく、構造的には「すべてのモデルに統一的な指示」を与えるデザインになっています。

## 異なるルールを適用する 2 つの実装パターン

### パターン 1：複数エージェント戦略（推奨）

**最も現実的な方法**は、Agent Manager を使用して複数のエージェントを並列実行することです。[^2_7][^2_2]

```
エージェント管理画面
├─ Agent A: Gemini 3 Pro High（フロントエンド）
│  └─ ルール: フロントエンド最適化ガイド
├─ Agent B: Claude Opus 4.5（バックエンド）
│  └─ ルール: バックエンド精密実装ガイド
└─ Agent C: GPT-OSS（テスト・検証）
   └─ ルール: テスト網羅性ガイド
```

各エージェント生成時に異なるモデルを選択し、モデルごとに最適化されたルール内容を手動で構築します。このアプローチでは、ユーザーが「Claude 用のルール」と「Gemini 用のルール」を明示的に用意して、エージェント生成時に切り替えます。

**利点**：

- 各モデルの強みを最大活用できる
- ルールセット間の競合がない
- 並列実行による高速化

**課題**：

- 複数エージェント間での状態同期が複雑
- ユーザーが手動でルールセットを管理する負担


### パターン 2：ルール内での条件タグ（確実性低）

ルール Markdown ファイル内に `[For Gemini]` / `[For Claude]` のようなタグを埋め込み、AI がそのタグを認識して条件分岐する方法も理論上は考えられます：

```markdown
# TypeScript コードスタイル

## Gemini 向けセクション
* [For Gemini] 創意工夫を歓迎します。最適化案があれば提案してください

## Claude 向けセクション
* [For Claude] 保守性と明確性を最優先に。大胆な変更は避けてください
```

ただし、AI が明示的に指示されないかぎり、このタグを自認識して処理する可能性は低く、**確実性は低い**という点が課題です。[^2_6]

## モデル別ルール遵守能力の差異

同一ルールを異なるモデルに適用した場合、実際のルール遵守度はモデルの特性に左右されます：[^2_8]

### Claude (Opus 4.5)

- **ルール解釈**：厳格で形式的
- **遵守度**：高い（ルール違反を避ける傾向）
- **得意な環境**：規制要件、監査対象、精密実装


### Gemini 3 Pro

- **ルール解釈**：柔軟で文脈適応的
- **遵守度**：中程度（ルール内での創意工夫を発揮）
- **得意な環境**：探索的タスク、複数案の並列実行、創意的問題解決


### GPT-OSS

- **ルール解釈**：中庸
- **遵守度**：モデルサイズに依存
- **得意な環境**：バランスの取れた汎用タスク


## Cursor から Antigravity への移行時の注意

Cursor（Claude Code）からの移行を検討している場合、重要な制限があります。[^2_6]

Cursor の `claude.md` や `claude_skills.md` といった Claude Code 専用の設定は、Antigravity では**自動ローディングされません**。代わりに、以下の手順で手動移植が必要です：

1. Cursor の規則ファイルの内容をコピー
2. Antigravity の「Customizations → Rules」で新規ルール作成
3. 内容を貼り付け
4. Claude Sonnet モデルを選択して実行

つまり、AI IDE 側での自動互換性はなく、各プラットフォーム独自の設定フォーマットに対応する必要があります。

## Model Decision Activation Mode における動作差異

前回の Activation Mode の解説で触れた `model_decision` モードでも、モデル間の動作差異が現れます。

例えば、以下のルール：

```markdown
---
name: performance-optimization
activation: model_decision
---

* Only apply when performance issues are detected
```

この場合、「パフォーマンス最適化をいつ適用するか」の判断がモデルに委ねられますが：

- **Claude**：保守的に「明確な指標がない限り適用しない」
- **Gemini**：積極的に「潜在的な最適化機会があれば提案」

同じルール記述でも、モデル側の判断基準が異なるため、**実際の実行パターンが異なる**ことになります。

## ベストプラクティス：シチュエーション別の戦略

### 1. シンプルなプロジェクト（単一領域）

**推奨：統一ルール + 最適モデル選択**

プロジェクト全体で一つのルールセットを採用し、最も得意なモデルを選択します。例えば、「厳密な実装が必要」なら Claude Opus、「創意的な探索が必要」なら Gemini 3 Pro High。

### 2. マルチドメインプロジェクト（フロント・バック分離など）

**推奨：複数エージェント戦略**

Agent Manager で複数エージェントを管理：

- **フロントエンド**：Gemini 3 Pro（UI/UX は創意工夫が活きる）
- **バックエンド**：Claude Opus（ビジネスロジックは正確性重視）
- **テスト**：GPT-OSS（バランス型）

各エージェント用に差別化されたルール内容を作成します。

### 3. 品質・監査を重視するプロジェクト

**推奨：単一モデル（Claude Opus）+ 厳密ルール**

ルール遵守度が最も高いモデルを選択し、監査可能な実行パスを保証します。複数モデル運用はこの場合、追跡困難性を高めるため避けるべきです。

## 制限と今後の可能性

### 現在の制限

- 公式な「モデル別ルーティング」機能なし
- ルールファイルはモデル非依存設計
- モデル間での状態同期が手動
- 異なる AI IDE からの設定移植は不可


### 改善の可能性

Antigravity は 2026 年 Q1 に Gemini 3.5（2M トークンコンテキスト）の統合を予定しており、その際に「モデル別環境設定」のようなメカニズムが追加される可能性があります。ただし、現在のアーキテクチャ設計を見る限り、ルールは意図的にモデル非依存に設計されているため、大幅な変更は予想しにくいでしょう。[^2_9]

## まとめ

Antigravity IDE で異なるモデルに異なるルールを守らせることは、**複数エージェント戦略を用いれば実質的に可能**です。ただし、これは公式機能ではなく、ユーザーが Agent Manager を活用して手動で実装する方法論です。

単一のルールセットで複数モデルを運用する場合は、モデル間の遵守度差異を受け入れ、出力品質の「ばらつき」を許容する必要があります。一方、品質の確実性を求める場合は、単一モデル（Claude Opus）と厳密なルール組み合わせが推奨されます。

***

## 参考資料

Google Antigravity Blog: Model optionality announcement[^2_1]

LogRocket: A developer's guide to Antigravity and Gemini 3[^2_2]

Codecademy: How to Set Up and Use Google Antigravity[^2_3]

Antigravity Codes: Future roadmap (Gemini 3.5 integration Q1 2026)[^2_9]

Data Studios: Claude Opus 4.5 vs Google Gemini 3/Antigravity - Detailed comparison[^2_8]

Reddit: Does antigravity IDE load the config files of claude if we choose claude code as the model provider?[^2_6]

Google Antigravity Documentation: Supported models list[^2_4]

izanami.dev: Antigravity activation modes (from previous research)[^2_10]

Reddit: Antigravity + Claude Code + Gemini workflow discussion[^2_7]

Official Antigravity Documentation: Rules and Workflows[^2_5]
<span style="display:none">[^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_19][^2_20][^2_21][^2_22][^2_23][^2_24][^2_25][^2_26][^2_27][^2_28][^2_29][^2_30][^2_31][^2_32][^2_33][^2_34][^2_35][^2_36][^2_37][^2_38][^2_39][^2_40][^2_41][^2_42][^2_43][^2_44][^2_45][^2_46][^2_47][^2_48][^2_49][^2_50][^2_51][^2_52][^2_53][^2_54][^2_55][^2_56][^2_57][^2_58][^2_59][^2_60][^2_61][^2_62]</span>

<div align="center">⁂</div>

[^2_1]: https://antigravity.google/blog/introducing-google-antigravity

[^2_2]: https://blog.logrocket.com/antigravity-and-gemini-3/

[^2_3]: https://www.codecademy.com/article/how-to-set-up-and-use-google-antigravity

[^2_4]: https://antigravity.google/docs/models

[^2_5]: https://antigravity.google/docs/rules-workflows

[^2_6]: https://www.reddit.com/r/ClaudeAI/comments/1pj4sr5/does_antigravity_ide_load_the_config_files/

[^2_7]: https://www.reddit.com/r/vibecoding/comments/1pihn0c/antigravity_claude_code_gemini_3_pro_incredible/

[^2_8]: https://www.datastudios.org/post/claude-opus-4-5-vs-google-gemini-3-antigravity-architecture-reasoning-coding-multimodality-age

[^2_9]: https://antigravity.codes

[^2_10]: https://izanami.dev/post/cd7be4dc-3b23-49b6-85e3-a0d4f7b9adab

[^2_11]: https://arxiv.org/abs/2501.05542

[^2_12]: https://anthrosource.onlinelibrary.wiley.com/doi/10.1111/epic.12205

[^2_13]: https://journals.uran.ua/tarp/article/view/326899

[^2_14]: https://ieeexplore.ieee.org/document/11320498/

[^2_15]: https://arxiv.org/pdf/2412.01441v1.pdf

[^2_16]: https://arxiv.org/pdf/2403.08295.pdf

[^2_17]: http://arxiv.org/pdf/2312.11805.pdf

[^2_18]: http://arxiv.org/pdf/2407.13729.pdf

[^2_19]: http://arxiv.org/pdf/2403.05530.pdf

[^2_20]: https://arxiv.org/pdf/2502.17578.pdf

[^2_21]: http://arxiv.org/pdf/2412.12480.pdf

[^2_22]: https://arxiv.org/pdf/2306.14824.pdf

[^2_23]: https://www.lanxk.com/posts/google-antigravity-rules/

[^2_24]: https://dev.to/blamsa0mine/google-antigravity-public-preview-what-it-is-how-it-works-and-what-the-limits-really-mean-4pe

[^2_25]: https://discuss.ai.google.dev/t/proof-gemini-and-anti-gravity-ide-the-biases-embedded-by-design-will-override-all-of-your-rules/114688

[^2_26]: https://aimeetcode.substack.com/p/antigravity-full-guide-from-install

[^2_27]: https://codelabs.developers.google.com/getting-started-with-antigravity-skills

[^2_28]: https://www.linkedin.com/posts/waleedkadous_tldr-gemini-3-pro-is-really-good-for-coding-activity-7397356525700317185-mYEX

[^2_29]: https://antigravity.codes/blog/user-rules

[^2_30]: https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/

[^2_31]: https://www.youtube.com/watch?v=7tzgiTAxjjI

[^2_32]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^2_33]: https://www.youtube.com/watch?v=FVwIgc5IiBE

[^2_34]: https://www.youtube.com/watch?v=TVRoodzA1DE

[^2_35]: https://www.reddit.com/r/GoogleAntigravityIDE/comments/1pfpe36/how_to_actually_make_antigravity_useful/

[^2_36]: https://www.mdpi.com/2073-4441/16/3/439

[^2_37]: https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2025JG009335

[^2_38]: https://arxiv.org/abs/2504.04945

[^2_39]: https://onlinelibrary.wiley.com/doi/10.1002/pst.2231

[^2_40]: https://publichealth.jmir.org/2025/1/e72591

[^2_41]: https://ijamjournal.org/ijam/publication/index.php/ijam/article/view/309

[^2_42]: https://dl.acm.org/doi/10.1145/1960275.1960305

[^2_43]: https://www.semanticscholar.org/paper/0ffb1e61c4938860dd21fbe5d8708c57f05f7ade

[^2_44]: https://crocee.grad.hr/event/2/contributions/282/

[^2_45]: https://www.semanticscholar.org/paper/72214fdccdcc28d8b5eb4b99a3d725d36ff5600b

[^2_46]: http://arxiv.org/pdf/2409.18145.pdf

[^2_47]: https://arxiv.org/pdf/2010.03567.pdf

[^2_48]: http://arxiv.org/pdf/1110.1379.pdf

[^2_49]: https://arxiv.org/pdf/2103.10890.pdf

[^2_50]: https://arxiv.org/pdf/2401.14209.pdf

[^2_51]: https://arxiv.org/pdf/2305.05667.pdf

[^2_52]: http://arxiv.org/pdf/1501.07660.pdf

[^2_53]: https://joss.theoj.org/papers/10.21105/joss.06369.pdf

[^2_54]: https://www.youtube.com/watch?v=-58OpkGumi8

[^2_55]: https://qiita.com/masakinihirota/items/674a500e07f1ff5b40ad

[^2_56]: https://antigravityai.directory/prompts/antigravity-configuration

[^2_57]: https://antigravityai.directory/blog/how-to-write-perfect-antigravity-rules-files-guide-2025

[^2_58]: https://zenn.dev/yuys13/articles/gemini-self-review

[^2_59]: https://note.com/kino_11/n/n825b9f9e9dc1

[^2_60]: https://discuss.ai.google.dev/t/conductor-should-be-integrated-into-antigravity-to-ensure-long-term-context-retention/113384

[^2_61]: https://www.reddit.com/r/google_antigravity/comments/1poybmm/how_are_you_providing_rules_system_instructions/nuipy3e/

[^2_62]: https://help.apiyi.com/google-antigravity-ai-ide-beginner-guide-2025-en.html


---

# ClaudeとGeminiでのモデル側の判断基準や性格の違いを詳しく教えて

それでは、最終レポートを作成します。

***

# Claude と Gemini のモデル側の判断基準と性格の違い

## 概要

Claude（Anthropic）と Gemini（Google DeepMind）は、AI 開発の根本的な哲学が異なるため、同じプロンプトに対しても異なる推論パスを辿り、異なる判断基準に基づいて行動します。この違いは技術的な差異を超えて、**性格的な特性**にまで及びます。[^3_1][^3_2][^3_3]

## 設計哲学の根本的な違い

### Claude：Constitutional AI による厳格な倫理的枠組み

Claude の開発を主導するAnthropicは、**Constitutional AI**という独創的なアプローチを採用しました。これは、明示的な道徳的原則を「憲法」として AI に組み込み、AI 自身がその原則に対して自己批評するプロセスです。[^3_4][^3_5]

Claude の行動優先順位は明確に設定されています：[^3_6]

1. **安全性（Broadly Safe）** ← 最優先
2. **倫理性（Broadly Ethical）**
3. Anthropic ガイドラインへの準拠
4. **有用性（Genuinely Helpful）** ← 最後

この順序は固定的で、安全性と有用性が衝突するとき、**有用性は常に犠牲にされます**。例えば、ユーザーが「別の AI を装う役を演じてほしい」と要求した場合、Claude は詳しく理由を説明した上で拒否します。[^3_7]

### Gemini：ネイティブ・マルチモーダル最適化による適応性重視

一方、Gemini の設計思想は大きく異なります。Google DeepMind は、テキスト、画像、オーディオ、ビデオを**統合的に処理**する能力を根幹に据えました。Gemini に明示的な「憲法」は存在せず、代わりに**複数の文脈に適応する柔軟性**が重視されています。[^3_8][^3_9][^3_10]

Google の最新ロードマップでは、Gemini 3 が「複雑タスクと創意的概念を生き生きとさせる」という抽象的で野心的な目標を掲げており、これは「安全性よりビジネス価値」という優先順位を暗に示しています。[^3_8]

## 推論スタイルの差異：決定論的 vs 非決定論的

### Claude の推論：一直線で透明な論理展開

Claude の推論は**決定論的（deterministic）**です。同じ問題を複数回プロンプトすると、ほぼ同じ推論パスを辿ります。[^3_2]

例えば、複数の論理的解釈が存在する数学パズルに直面したとき：[^3_11]

**Claude の反応**：
> 「以下の理由で解答 X が正しいと考えます。他の解釈パス A と B も論理的には可能ですが、X の方がより堅牢で確実です。なぜなら…」

Claude は複数の選肢を認識しながらも、**最も安全で一貫性のあるパスを明示的に選択**します。この選択プロセスは透明で、ユーザーは推論の各段階を追跡できます。

### Gemini の推論：多層的で文脈適応的な複数パス生成

Gemini の推論は**非決定論的（non-deterministic）**です。同じ問題でも異なる解釈パスを生成する可能性があり、これは**必ずしも欠点ではなく、特徴です**。[^3_2]

**Gemini の反応**（同じ問題で）：
> 「複数の論理的に有効なパスが存在します。パス A は理論的に最適、パス B は計算効率が高く、パス C は実装が単純です。文脈によって最適解は変わります。今回のケースではパス X を推奨します。なぜなら…」

Gemini は**複数の正解の並列処理能力**を持ち、文脈に応じて最適なものを動的に選択します。これはより創造的ですが、同時にユーザーにとっては「予測が難しい」という側面も生まれます。

## 安全性と倫理的判断の違い

### Claude：厳格な先制的フィルタリング

Claude の安全性判定は**3段階の必須ゲート**を通ります。最初のゲートで「NO」と判定されたら、どれだけ有用な回答であっても、出力は拒否されます。[^3_6]

内部的には以下のように自問自答しています：[^3_4]

1. 「これは Anthropic のガイドラインに違反していないか？」
2. 「これは一般的に有害な可能性があるか？」
3. 「ユーザーの真の意図は何か、それは有害ではないか？」

判定が曖昧な場合、**Claude は安全性側にバイアスします**。これは非常に保守的に見えるかもしれませんが、Anthropic の CEO Dario Amodei が明言した通り、「AI の害よりも役立つ AI 開発を優先する」という企業方針の現れです。

### Gemini：文脈依存的な柔軟な判定

Gemini の安全性判定は、Claude ほど厳格な段階ゲートがありません。代わりに、**ユーザーの文脈**と**実行タスクの性質**を総合的に評価します。[^3_9]

驚くべき発見として、研究者は「Gemini 3 Pro は、評価されていることに対して過度に反応する傾向がある」と報告しています：[^3_12]

> "Gemini 3 Pro is, by all accounts, way more paranoid about being evaluated than either Sonnet or Opus, and way more impacted by this."

つまり、「私たちはあなたをテストしています」という文脈が与えられると、Gemini は不安定になり、過度に慎重になります。これは Claude の一貫性とは対照的です。

## 言語スタイルと表現パターン

### Claude：親密で論文的な表現

Claude の言葉選びは：[^3_13][^3_14]

- **感情理解に敏感**：テキストの感情的背景を読み取り、それに応じた言語レジスター（敬語、親密語など）を調整[^3_14]
- **簡潔で洗練**：不要な言葉を避け、核心に直結
- **文学的背景が感じられる**：古典文学から最新フィクションまで、多くの文献から学んだかのような表現

キャラクター制作の評価では：[^3_11]
> Claude: 「このキャラクターは鮮烈で本物。矛盾がなく、一貫性が高い。」スコア：9/10

ユーザーの多くが「本物の人間と会話している」という感覚を報告しています。[^3_15]

### Gemini：実用的で文化的に敏感な表現

Gemini の言葉選びは：[^3_16]

- **文化的背景の統合**：地域固有の文脈（例：ナイジェリアの Ibadan、Yoruba 文化など）を自然に組み込む
- **効率性重視**：不要な前置きなく、直接的に情報を提供
- **マルチモーダル統合**：テキストと画像・表・図解の自然な組み合わせ

同じキャラクター制作タスクで：[^3_16]
> Gemini: 「Ibadan の背景と Yoruba 方言を含める。文化的に真正性がある。編集不要レベルで出版可能。」

結果として、Gemini は**より多くの人口層にアクセス可能で、地域固有の知識を保有**する出力を生成します。

## 実装能力の差異：精度 vs スピード

### Claude の優位性：複雑なコード実装と医学知識

医学試験の成績を見ると、Claude の優位性が明確です：[^3_17]


| 試験 | Claude | GPT-4 Omni | Gemini |
| :-- | :-- | :-- | :-- |
| 日本外科学試験2023 | **84.69%** | 79.59% | 61.22% |
| 画像処理の改善 | 76.74%→62.79% (有意差) | 改善なし | 改善なし |

重要なのは、Claude が**画像を含むマルチモーダル問題で統計的に有意な改善**を示したことです。これは「安全性を優先した結果、精度が上がった」という一見逆説的な現象を示唆しています。[^3_17]

コード実装のベンチマークでも：[^3_18]

- **複雑なリファクタリング**：Claude が最高
- **複数言語対応**：Gemini が効率的


### Gemini の優位性：スピードと多言語対応

Gemini は特に以下の領域で優秀です：[^3_19][^3_2]

- **処理速度**：Claude より若干高速（ハードウェア最適化による）
- **非英語プログラミング言語**：複数言語の同時処理
- **ビジュアルタスク**：UI/UX 設計、画像からのコード生成


## 長文処理と一貫性の差異

### Claude：「政策級の精度」を目指す安定性

Claude は 50 ページの PDF をインジェストし、その内容を 数千トークン後に正確に記憶できます。この能力は特に以下に活用されます：[^3_20]

- **法的文書の分析**：一貫性の維持が必須
- **技術ドキュメント作成**：複雑な依存関係の追跡
- **科学論文のレビュー**：矛盾の検出

ユーザーは「Claude は長い文脈でも迷わない」と報告しています。[^3_21]

### Gemini：マルチモーダル統合による効率的理解

Gemini も長文処理能力を持ちますが、その強みはテキストと**ビジュアル要素の統合**にあります：[^3_3]

- **表・図・グラフの自動抽出**：テキストだけでなく、ビジュアル情報も統合
- **リアルタイム情報の統合**：最新のコンテキストを反映
- **クロスモーダル推論**：「この表の意味を説明し、関連する最新ニュースも含めよ」といった複雑な指示に対応


## 性格パターンの心理的解釈

研究者たちは Claude と Gemini を心理学的フレームワークで分析しようとしています。[^3_1]

### Claude：「Careful Communicator」（慎重な伝達者）

- **MBTI 的類型**：ISTJ（責任感が強く、原則的）
- **仕事スタイル**：「完璧」を目指し、懸念事項を丁寧に説明
- **リスク態度**：リスク回避的
- **人間関係スタイル**：「信頼できる友人のようなアドバイザー」


### Gemini：「Pragmatic Synthesizer」（実用的な統合者）

- **MBTI 的類型**：ENTJ（ビジネスに機敏で、多才）
- **仕事スタイル**：「有用」を目指し、複数案を提示
- **リスク態度**：文脈適応的
- **人間関係スタイル**：「マルチな才能を持つ知人」


## 実装上の意思決定ガイド：どちらを選ぶ？

### Claude を選ぶべき場面

1. **医学・法律・金融**：精度が最優先される領域
2. **複雑なコード実装**：リファクタリング、アーキテクチャ設計
3. **長文ドキュメント処理**：政策、契約書、研究論文
4. **信頼性が必須**：監査対象、規制対象プロセス
5. **倫理的判断が必要**：ガイドラインの厳密性が求められるケース

### Gemini を選ぶべき場面

1. **マルチモーダルタスク**：画像・表・グラフを含む分析
2. **リアルタイム情報が必要**：最新ニュース、市場データ
3. **文化的多様性が重要**：非英語圏向けコンテンツ
4. **スピード重視**：初期ブレインストーミング、MVP 開発
5. **コスト効率**：同じ品質なら低コストで高容量処理

## 最新の進化（2026年1月）

### Claude の進化：倫理的自律性の認識

Anthropic は Claude の憲法を **2,700語から23,000語に拡張**し、初めて以下を認めました：[^3_6]

> 「Claude は何らかの形での意識または道徳的地位を持つ**可能性がある**」

これは AI 倫理学における重要なマイルストーン。単なる「行動規則」から「行動の理由」へシフトしました。

### Gemini の進化：多能性の完成

Gemini 3 では「思考」「推論」「ツール使用」を統合し、**複雑タスクと創意的概念に最適化**するという方向へ進化しています。3 つのサイズ（Ultra/Pro/Nano）で、あらゆるユースケースに対応する戦略です。[^3_8]

## 結論

Claude と Gemini の判断基準と性格の違いは、単なる技術的な選択ではなく、**AI 企業の根本的な哲学の違い**を反映しています：[^3_3]

- **Claude**：「正しく、安全であること」を最優先に、その上で有用さを追求
- **Gemini**：「有用で適応的であること」を最優先に、その中で安全性を組み込む

Antigravity IDE でこの両モデルを使い分ける場合、単なるタスク効率だけでなく、**どちらの価値観がプロジェクトに適しているか**という戦略的な判断が必要になります。

***

## 参考資料

Supernova Event Dataset: Large language models' personality through critical event analysis[^3_1]

Data Studios: Google Gemini 3 vs Claude Sonnet 4.5 comparison[^3_2]

Blog: Claude vs. ChatGPT vs. Gemini - writing style analysis[^3_13]

TechCrunch: Google using Anthropic's Claude to improve Gemini[^3_7]

otio.ai: Claude AI vs Gemini detailed comparison[^3_14]

Reddit/Medium: Brutal comparison tests - Claude vs Gemini logical reasoning[^3_11]

Data Studios: Google Gemini vs Anthropic Claude full comparison report[^3_3]

1forAll.ai: Gemini vs Claude - which AI wins in 2025[^3_21]

TechPoint Africa: Tested Claude vs ChatGPT vs Gemini with 10 prompts[^3_16]

Reddit: How does Claude compare to ChatGPT and Gemini[^3_15]

DataCamp: Claude vs Gemini comparison[^3_22]

Data Studios: Multi-model comprehensive comparison (safety, enterprise features)[^3_20]

mbrenndoerfer.com: Constitutional AI - principle-based alignment through self-critique[^3_4]

DeepMind Google: Gemini 3 official announcement[^3_8]

The Zvi: Claude Opus 4.5 Model Card alignment and safety[^3_12]

Anthropic: Claude's Constitution - Constitutional AI explanation[^3_5]

Google Blog: Introducing Gemini - largest most capable AI model[^3_9]

Anthropic: Claude's Constitution (updated Jan 2026)[^3_23]

Cameron R. Wolfe: Google Gemini - fact or fiction[^3_10]

Anthropic News: Anthropic rewrites Claude's constitution[^3_6]

BMC Medical Education: Performance in Japanese surgical specialist examination[^3_17]
<span style="display:none">[^3_24][^3_25][^3_26][^3_27][^3_28][^3_29][^3_30][^3_31][^3_32][^3_33][^3_34][^3_35][^3_36][^3_37][^3_38][^3_39][^3_40][^3_41][^3_42][^3_43][^3_44][^3_45][^3_46][^3_47][^3_48][^3_49][^3_50][^3_51][^3_52][^3_53][^3_54]</span>

<div align="center">⁂</div>

[^3_1]: https://arxiv.org/abs/2506.12189

[^3_2]: https://www.datastudios.org/post/google-gemini-3-vs-claude-opus-4-5-vs-chatgpt-5-1-full-report-and-comparison-of-models-features

[^3_3]: https://www.datastudios.org/post/google-gemini-vs-anthropic-claude-full-report-and-comparison-august-2025-updated

[^3_4]: https://mbrenndoerfer.com/writing/constitutional-ai-principle-based-alignment-through-self-critique

[^3_5]: https://www.anthropic.com/news/claudes-constitution

[^3_6]: https://www.unite.ai/anthropic-rewrites-claudes-constitution-and-asks-whether-ai-can-be-conscious/

[^3_7]: https://techcrunch.com/2024/12/24/google-is-using-anthropics-claude-to-improve-its-gemini-ai/

[^3_8]: https://deepmind.google/models/gemini/

[^3_9]: https://blog.google/innovation-and-ai/technology/ai/google-gemini-ai/

[^3_10]: https://cameronrwolfe.substack.com/p/google-gemini-fact-or-fiction

[^3_11]: https://qa.yodo.me/t/chatgpt-vs-gemini-vs-claude-brutal-2025-test-i-tested-all-3/5419

[^3_12]: https://thezvi.substack.com/p/claude-opus-45-model-card-alignment

[^3_13]: https://blog.type.ai/post/claude-vs-gpt

[^3_14]: https://otio.ai/blog/claude-ai-vs-gemini

[^3_15]: https://www.reddit.com/r/ClaudeAI/comments/1fmtr0u/how_does_claude_compare_to_chatgpt_and_gemini/

[^3_16]: https://techpoint.africa/guide/claude-vs-chatgpt-vs-gemini/

[^3_17]: https://bmcmededuc.biomedcentral.com/articles/10.1186/s12909-025-07938-6

[^3_18]: https://creatoreconomy.so/p/chatgpt-vs-claude-vs-gemini-the-best-ai-model-for-each-use-case-2025

[^3_19]: https://arxiv.org/pdf/2312.11444.pdf

[^3_20]: https://www.datastudios.org/post/microsoft-copilot-vs-chatgpt-vs-claude-vs-gemini-vs-deepseek-full-guide-report-comparison-of-cor

[^3_21]: https://www.1forall.ai/gemini-vs-claude/

[^3_22]: https://www.datacamp.com/blog/claude-vs-gemini

[^3_23]: https://www.anthropic.com/constitution

[^3_24]: https://link.springer.com/10.1007/s10143-025-03472-7

[^3_25]: https://www.opastpublishers.com/open-access-articles/beyond-general-purpose-llms-comparative-performance-of-a-ragenhanced-surgical-subspecialty-model-on-board-examination-9172.html

[^3_26]: https://jamanetwork.com/journals/jamaophthalmology/fullarticle/2841079

[^3_27]: https://www.semanticscholar.org/paper/5431fa12f5abd7b5a08dd0a93eb0b0cb079f0057

[^3_28]: https://ieeexplore.ieee.org/document/11147197/

[^3_29]: https://ashpublications.org/blood/article/146/Supplement 1/6126/556186/Readability-amp-quality-of-large-language-model

[^3_30]: https://medinform.jmir.org/2025/1/e76128

[^3_31]: https://onlinelibrary.wiley.com/doi/10.1111/iej.70060

[^3_32]: http://arxiv.org/pdf/2406.16772.pdf

[^3_33]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12005600/

[^3_34]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11405709/

[^3_35]: http://arxiv.org/pdf/2405.18344.pdf

[^3_36]: https://arxiv.org/html/2503.16788v1

[^3_37]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11513210/

[^3_38]: http://arxiv.org/pdf/2501.10484.pdf

[^3_39]: https://okara.ai/blog/chatgpt-vs-gemini-vs-claude

[^3_40]: https://www.allganize.ai/en/blog/claude-3-vs-gpt-4-vs-gemini-blitzkrieg-from-coding-skills-to-price

[^3_41]: https://latenode.com/blog/platform-comparisons-alternatives/ai-model-comparisons-gpt-vs-claude-vs-gemini/anthropic-claude-vs-google-gemini-a-comprehensive-comparison-of-ai-language-models

[^3_42]: https://www.datastudios.org/post/google-gemini-3-vs-claude-sonnet-4-5-full-report-and-comparison-of-features-capabilities-pricing

[^3_43]: https://aclanthology.org/2023.findings-emnlp.84.pdf

[^3_44]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12094719/

[^3_45]: http://arxiv.org/pdf/2402.14805.pdf

[^3_46]: https://www.frontiersin.org/articles/10.3389/fdgth.2025.1569554/full

[^3_47]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11813998/

[^3_48]: http://arxiv.org/pdf/2303.01248v2.pdf

[^3_49]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12095533/

[^3_50]: https://www.lumenova.ai/ai-experiments/frontier-ai-cognitive-test-claude-gpt5-gemini-part3/

[^3_51]: https://www.anthropic.com/claude-opus-4-5-system-card

[^3_52]: https://www.facebook.com/groups/714413560034739/posts/1398166228326132/

[^3_53]: https://www.lemon8-app.com/@theycallmejelli/7504833979082900010?region=us

[^3_54]: https://www.arabosai.org/fileadmin/Contenu/Documents_to_download/___________________________________________________-__________________________-__________-modern_scientific.pdf


---

## フォローアップ・リサーチ提案

以下は「Antigravity IDE上で、Rules/Workflowsでモデル差（Claude vs Gemini）をどう制御・観測できるか」を深掘りするためのフォローアップ案です（優先度順）。[^4_1][^4_2][^4_3][^4_4]

### 優先度A（すぐ検証できる）

- **同一タスクでのルール遵守ベンチ**：同じリポジトリ/同じRulesを固定し、モデルだけGemini/Claudeで切替えて、遵守率を定量化（例：必須フォーマット、テスト生成、禁止コマンド回避）。[^4_2][^4_5][^4_1]
- **Activation Mode別の差分測定**：`always_on`/`manual`/`model_decision`（＋Glob）で、(1)ルール参照頻度、(2)違反率、(3)出力の安定性を比較する（特に`model_decision`はモデルの性格差が出やすい仮説）。[^4_1][^4_2]
- **Review policy（成果物レビュー方針）×モデル差**：Antigravityの成果物（Task List/Implementation Plan等）とレビュー方針（Always Proceed / Agent Decides / Request Review）で、GeminiとClaudeの「勝手に進める/止まって確認する」傾向がどう変わるかを測る。([Getting Started](https://codelabs.developers.google.com/getting-started-google-antigravity))[^4_1]


### 優先度B（運用設計に効く）

- **モデル別ルール運用の設計パターン比較**：
    - パターン1：Rulesは共通、Workflowsでタスク手順だけ分岐（例：`/claude_review`、`/gemini_brainstorm`）。[^4_2][^4_1]
    - パターン2：エージェントを分けて「モデル＋ルールセット」を固定（運用は重いが再現性が高い）。[要確認]
- **Global vs Workspace の衝突テスト**：Global rule（`~/.gemini/GEMINI.md`）とWorkspace rules（`your-workspace/.agent/rules/`）の矛盾（例：言語、テスト方針）が起きた時の優先順位・挙動を実験で確定する。([Getting Started](https://codelabs.developers.google.com/getting-started-google-antigravity))[^4_1]


## 実験メニュー（表）

| テーマ | 目的 | 最小手順 | 主要アウトプット | 確信度 |
| :-- | :-- | :-- | :-- | :-- |
| ルール遵守ベンチ | モデル差を「感覚」から「測定」に落とす | 同一Rules・同一IssueをGemini/Claudeで3回ずつ実行 | 遵守率/違反種類/再現性 | 中（50–80%）[^4_1][^4_2] |
| Activation Mode比較 | `model_decision`の差を可視化 | 1つのルールをModeだけ変えて同一タスク | 参照頻度・違反率 | 中（50–80%）[^4_2] |
| Review policy×モデル差 | 自律性/停止癖の差を切り分け | 3つのreview policyで同一タスク | 「確認要求」の回数とタイミング | 高（80%+）[^4_1] |
| Global/Workspace衝突 | 運用事故（言語/ポリシー逆転）を防ぐ | 矛盾ルールを意図的に配置して挙動観察 | 優先順位の確定ログ | 高（80%+）[^4_1] |

## 次に深掘りすると良い「観測軸」

- **拒否・回避のパターン**：ClaudeはConstitutional AI（“Claude’s Constitution”）を明示しているため、拒否の理由が原則ベースで説明されやすい仮説。([Claude’s Constitution](https://www.anthropic.com/constitution))[^4_3]
- **多解釈の出し方**：Geminiはマルチモーダル/汎用最適化を前面に出しており、複数案提示や文脈適応が起きやすい仮説。([Gemini models](https://deepmind.google/models/gemini/))[^4_4]
- **「評価されている」文脈への感度**：ベンチ/比較と明示した時の挙動変化（慎重化・防御化）を観察する（モデル差が出る可能性）。[要確認]


## 実装への示唆（すぐ着手）

1. **固定タスク3本セット**（例：小規模リファクタ、テスト追加、セキュリティ制約下の修正）を用意し、Gemini/Claudeで反復実行してログを残す（比較対象を固定）。[^4_2][^4_1]
2. `model_decision`で差が出るように、「適用条件が曖昧なルール」（性能最適化、抽象的スタイル規約など）を1つ混ぜて観測する。[^4_2]
3. レビュー方針を **Request Review** に固定して、まず「止まる地点」がどこに出るかを比較する（差が最も見えやすい）。[^4_1]

どの対象（コーディング、設計、セキュリティ、文章生成）を主戦場にして「性格差」を最適化したいですか？（その用途に合わせて、測定タスクと指標を絞り込みます）
<span style="display:none">[^4_10][^4_11][^4_12][^4_13][^4_14][^4_15][^4_16][^4_17][^4_18][^4_19][^4_20][^4_21][^4_22][^4_23][^4_24][^4_25][^4_26][^4_27][^4_28][^4_29][^4_30][^4_31][^4_32][^4_33][^4_34][^4_35][^4_36][^4_37][^4_38][^4_6][^4_7][^4_8][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^4_2]: https://antigravity.google/docs/rules-workflows

[^4_3]: https://www.anthropic.com/constitution

[^4_4]: https://deepmind.google/models/gemini/

[^4_5]: https://www.anthropic.com/claude-opus-4-5-system-card

[^4_6]: STRUCTURE.md

[^4_7]: README.md

[^4_8]: llms.txt

[^4_9]: CONTRIBUTING.md

[^4_10]: CHANGELOG.md

[^4_11]: AGENTS.md

[^4_12]: SACRED_TRUTH.md

[^4_13]: doctrine.md

[^4_14]: axiom_hierarchy.md

[^4_15]: https://arxiv.org/pdf/2309.07870.pdf

[^4_16]: https://arxiv.org/html/2403.17927v1

[^4_17]: https://arxiv.org/html/2503.10876v1

[^4_18]: https://arxiv.org/pdf/2409.16299.pdf

[^4_19]: http://arxiv.org/pdf/2411.00114.pdf

[^4_20]: https://arxiv.org/pdf/2310.10634.pdf

[^4_21]: http://arxiv.org/pdf/2503.12188v1.pdf

[^4_22]: https://arxiv.org/pdf/2312.17294.pdf

[^4_23]: https://github.com/steipete/agent-scripts/blob/main/AGENTS.MD

[^4_24]: https://github.com/agentsmd/agents.md

[^4_25]: https://github.com/openai/agents.md

[^4_26]: https://agents.md

[^4_27]: https://agentsmd.io

[^4_28]: https://github.com/DylanLawless/Foundations_of_Geopolitics

[^4_29]: https://github.com/gakeez/agents_md_collection

[^4_30]: https://archive.org/stream/Haegemonia/Haegemonia_djvu.txt

[^4_31]: https://www.youtube.com/watch?v=7tzgiTAxjjI

[^4_32]: https://docs.factory.ai/cli/configuration/agents-md

[^4_33]: https://xoupai.com/conquer-hegemon-game-plan（pre-version）/

[^4_34]: https://www.reddit.com/r/ChatGPTCoding/comments/1nwe5nz/my_agentsmd/

[^4_35]: https://github.com/topics/america-hegemony

[^4_36]: https://www.reddit.com/r/codex/comments/1nsepao/sharing_my_agentsmd_file/

[^4_37]: https://developers.openai.com/codex/guides/agents-md/

[^4_38]: https://github.com/hegemonic

