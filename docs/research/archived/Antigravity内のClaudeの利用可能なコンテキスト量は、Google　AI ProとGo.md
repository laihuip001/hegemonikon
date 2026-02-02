<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Antigravity内のClaudeの利用可能なコンテキスト量は、Google　AI ProとGoogle　AI Ultraで変わりますか？

基本的には**変わりません**。Google AI Pro／Google AI Ultraで主に変わると明示されているのは、Antigravityの優先アクセスや（クォータ更新頻度は同じく）より高いレート制限・最大使用量上限といった「利用量（スループット）」側で、Claudeの1会話あたりのコンテキストウィンドウ自体がプランで増える旨は公式説明からは読み取れません。[^1_1][^1_2][^1_3]

## ProとUltraの違い（Antigravity側）

Googleの案内では、Pro/Ultra加入者はAntigravityで「priority access（優先アクセス）」と、より高い（より寛大な）レート制限を得て、クォータは5時間ごとにリフレッシュされるとされています。[^1_1]
また、Ultraは最上位として「最大の使用量上限」「優先トラフィック」「新モデルへの先行アクセス」などが挙げられています。[^1_2]

## Claudeのコンテキスト（モデル側）

AntigravityでClaudeを使う場合の「1回の会話で保持できる量（コンテキストウィンドウ）」は、基本的にClaudeモデル側の上限に依存します。[^1_4][^1_5]
コミュニティ報告や解説では、Antigravity上のClaudeは概ね約200kトークン規模のコンテキスト、といった言及があります。[^1_4][^1_5][^1_6]

## 実務上の注意点

プラン差でコンテキストが増えない一方、Ultraのほうが利用量上限が大きいことで「長時間・高頻度に回す運用（大量の編集/ツール呼び出し）」はやりやすくなる、という差が出やすいです。[^1_2][^1_1]
コンテキスト枯渇がボトルネックなら、スレッドを切って要約を引き継ぐ／重要情報をファイルに退避して参照させる、といった運用で回避するのが現実的です。[^1_4][^1_5]

いま想定している「コンテキスト不足」は、(A) 会話が長くなって古い内容が落ちる現象、(B) 大規模リポジトリを読ませた時に入らない現象、どちらに近いですか？
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://blog.google/feed/new-antigravity-rate-limits-pro-ultra-subsribers/

[^1_2]: https://support.google.com/googleone/answer/16286513?hl=ja-JP

[^1_3]: https://zenn.dev/zenogawa/articles/antigravity-tips

[^1_4]: https://www.reddit.com/r/google_antigravity/comments/1pro9yz/sharing_what_i_have_learned_about_using_claude_on/

[^1_5]: https://www.linkedin.com/posts/shmulikwillinger_ai-developertools-gemini-activity-7401622035304448000-wUne

[^1_6]: https://apidog.com/jp/blog/claude-opus-4-5-api-free-using-opencode-jp/

[^1_7]: https://x.com/MickeyKubo/status/1990976200832135657

[^1_8]: https://note.com/rei_matsu/n/nd9c8aa7eface

[^1_9]: https://zenn.dev/shintaroamaike/articles/8a4fbd4794e17a

[^1_10]: https://www.reddit.com/r/Bard/comments/1pi2eoa/antigravity_limits/

[^1_11]: https://kurutto115.hatenablog.com/entry/2025/antigravity

[^1_12]: https://www.reddit.com/r/Bard/comments/1p21ova/worth_configuring_gemini_cli_or_antigravity_mcp/

[^1_13]: https://zenn.dev/aun_phonogram/articles/4be2f4745726fb

[^1_14]: https://skywork.ai/blog/ai-agent/antigravity-infinite-context-window-explained/

[^1_15]: https://forest.watch.impress.co.jp/docs/serial/yaaiwatch/2078823.html

[^1_16]: https://qiita.com/akira_papa_AI/items/0acf2679e4ce9f7fb153

[^1_17]: https://antigravity.google/blog/introducing-google-antigravity

[^1_18]: https://one.google.com/about/google-ai-plans/

[^1_19]: https://gihyo.jp/article/2025/11/gemini3-pro-preview

[^1_20]: https://www.remio.ai/post/google-antigravity-technical-review-the-first-true-agentic-ide-powered-by-gemini-3-pro

[^1_21]: https://www.youtube.com/watch?v=Le6JTzoSXsI

[^1_22]: https://cloud-ace.jp/column/detail529/

[^1_23]: https://www.youtube.com/watch?v=pmGQXj-Wyfg

[^1_24]: https://www.reddit.com/r/google_antigravity/comments/1qbig23/tried_google_ai_pro_antigravity_ide_ended_up/

[^1_25]: https://blog.google/innovation-and-ai/technology/developers-tools/gemini-3-developers/

[^1_26]: https://blog.google/products-and-platforms/products/gemini/gemini-3/

[^1_27]: https://www.reddit.com/r/GeminiAI/comments/1q6viir/testing_gemini_30_pros_actual_context_window_in/

[^1_28]: https://forum.cursor.com/t/cursor-200-vs-claude-max-cursor-usage-limits-and-trade-offs/148298

[^1_29]: https://note.com/r1250_gs/n/n03ff84c86f76

[^1_30]: https://www.resumy.ai/tech-posts/22030e4f-a9f9-4bcb-8572-97f145a79719

[^1_31]: https://www.reddit.com/r/ClaudeAI/comments/1pdud6r/claude_opus_45_is_now_on_antigravity/

[^1_32]: https://news.ycombinator.com/item?id=46591026

[^1_33]: https://www.datastudios.org/post/claude-context-window-token-limits-memory-policy-and-2025-rules

[^1_34]: https://hiroppy.me/labs/feedle/ai/community/lai-so-blog

[^1_35]: https://news.ycombinator.com/item?id=46523995

[^1_36]: https://bsky.app/profile/sungkim.bsky.social/post/3mbnw2czdck2z

[^1_37]: https://zenn.dev/okikusan/articles/5bd89b6c91e680

[^1_38]: https://www.reddit.com/r/google_antigravity/comments/1povrx4/not_actually_opus/


---

# A

skillやrulesの存在が抜け落ちる

会話が長くなると、Antigravity内のClaudeが「スレッド内で以前効いていたはずのskill/rules」を前提にしなくなることがあります。特にSkillsは“常に読み込まれる”ものではなく、必要だと判断された時だけコンテキストに注入される設計なので、「存在が抜け落ちた」ように見えやすいです。[^2_1]

## 起きていること（Aの正体）

- SkillsはSystem Promptのように常駐せず、ユーザーの要求に“関連するとモデルが判断した時だけ”コンテキストにロードされます。[^2_1]
- そのため会話の論点が少しズレたり、指示が暗黙的になったりすると「今回は関係ない」と判定され、Skillがロードされず、結果としてskill前提の挙動が消えたように見えます。[^2_1]
- さらに長いスレッドでは、不要情報の蓄積によるContext Saturationや「context rot（無関係データで混乱）」が起きうる、と説明されています。[^2_1]


## 対策（抜け落ち防止）

- **重要な縛りはSkillではなくRuleに寄せる**：Skillはオンデマンドなので、「常に守らせたい規約・禁止事項・出力形式」はRules側（ガードレール）に置く方が安定します。[^2_1]
- Ruleの適用モードを見直す：Rulesには “always on / manual / model decision” のような適用モードがあり、model decisionだと状況次第で適用されない可能性が出ます（常時効かせたいものはalways on寄りが安全）。[^2_2]
- Skillを確実に使わせたい時は“強制トリガー文”を入れる：自然言語で自動発火させるだけでなく、「この作業はXYZ skillを使って」と明示して発火を確実にします。[^2_3][^2_4]


## 運用テク（長スレ耐性）

- 「会話で覚えさせる」より「ファイルに固定する」：プロジェクト方針・前提・手順はリポジトリ内の短いドキュメントに置き、必要なタイミングでそれを参照させる運用の方が、長スレで落ちにくいです。[^2_1]
- スレッドを分割し、引き継ぎ要約を作る：長期作業は“要約（現在の目的・制約・採用方針・未解決）”を作って新スレに渡すと、context rotの影響を受けにくくなります。[^2_1]

いまのRules/Skillsは、適用モードが「Always on / Manual / Model decision」のどれになっていますか？
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://codelabs.developers.google.com/getting-started-with-antigravity-skills

[^2_2]: https://www.youtube.com/watch?v=TVRoodzA1DE

[^2_3]: https://lilys.ai/ja/notes/google-antigravity-20260119/antigravity-skills-cheat-code

[^2_4]: https://www.youtube.com/watch?v=cgl5tFN2zxA

[^2_5]: https://note.com/ns29qrk/n/n75a7a8f0e3d7

[^2_6]: https://www.reddit.com/r/Bard/comments/1q8swz5/yes_the_1m_context_ai_cannot_read_even_a_20page/

[^2_7]: https://obot-ai.com/column/14668/

[^2_8]: https://qiita.com/aoinakanishi/items/06d9af0afe3830bc8d88

[^2_9]: https://www.youtube.com/watch?v=Z2VphrD4ehY

[^2_10]: https://antigravity.codes/rules

[^2_11]: https://cloud-ace.jp/column/detail534/

[^2_12]: https://antigravity.google/docs/rules-workflows

[^2_13]: https://www.issoh.co.jp/tech/details/10673/

[^2_14]: https://minna-systems.co.jp/test/blog/ai-dev-tools-complete-guide-december-2025/

[^2_15]: https://zenn.dev/nono0601/articles/a2ca2a36bd735f


---

# Antigravity + Claude における Rules / Skills / Context rot 実務ガイド


***

## 1. Rules の適用モードの違い

### 1-1. 3つのモードの意味

Antigravity の公式ドキュメントとチュートリアルで、Rules の `Activation Mode` は次の3種類と定義されています。[^3_1][^3_2][^3_3]

- **Always On**
すべてのメッセージに対して、そのルールが必ずシステムプロンプトとして注入されるモード。
    - 「このプロジェクトでは常に守ってほしい制約（言語・安全・操作ポリシーなど）」を置く場所。
    - 逆に内容が大きすぎると毎回コンテキストを圧迫するので、短く・抽象度高めにするのが望ましい。
- **Manual**
明示的に呼び出したときだけ有効になるモード。
    - UI やコマンド、Workflow などから「このルールを使う」と指定した場合のみ適用。
    - テスト用のルールや、「特定フェーズだけ別ポリシーにしたい」とき向け。
- **Model Decision**
ルールの自然言語説明を読んだ上で、「今回のユーザーリクエストに関係があるかどうか」をモデル（Claude / Gemini）が自動判定して適用するモード。[^3_2][^3_1]
    - 「時々効いているが、時々抜ける」典型パターンはこれ。
    - Skills と同様、“関連度判定”に依存するため、長スレや曖昧な指示で抜けやすい。


### 1-2. 現在のルールファイルがどのモードか確認する

**GUI から確認するのが一番確実**です。[^3_3][^3_4]

1. Antigravity 右下の **“Antigravity – Settings”** を開く。
2. **“Customizations” → “Manage” → “Rules” タブ** を開く。
3.     - `Global` 側に表示されているものが `~/.gemini/GEMINI.md` に対応するグローバルルール。[^3_4][^3_3]
    - `Workspace` 側に表示されているものが `プロジェクト/.agent/rules/<name>.md` に対応するワークスペースルール。[^3_3]
4. 各ルール行に **Activation Mode 列** があり、`Always On / Manual / Model Decision` のいずれかが表示される。[^3_3]

ここに出ているモードが「現在そのルールがどのモードで動いているか」です。
※デフォルトが何かは公式に固定されていないため、「実際に Rules 一覧を見て判断」が安全です。

### 1-3. Always On に変更する方法

これも GUI から変更するのが推奨です。[^3_2][^3_3]

1. 上記と同じく **Settings → Customizations → Rules** へ。
2. 対象ルール（`GEMINI.md` か、`.agent/rules/xxx.md` に対応するもの）を選択。
3. 詳細ビューかリスト上のドロップダウンで **Activation Mode を `Always On` に変更して保存**。[^3_2][^3_3]

以後、そのルールの内容は**毎ターン確実にシステムプロンプトとして注入**されます。[^3_5][^3_1]

**実務上のおすすめ構成（Antigravity + Claude 前提）**

- `GEMINI.md`（Global, Always On）
    - 言語・トーン・安全ポリシー・ファイル操作ポリシーなど「どのプロジェクトでも最上位に効かせたい共通ルール」[^3_6][^3_5][^3_4]
- プロジェクト固有ルール (`.agent/rules/code-generation-guide.md` など, Workspace, たとえば Always On or Model Decision)
    - そのリポジトリだけのコーディング規約・構成方針などを記述。[^3_7][^3_3]

***

## 2. Skill を「確実に」発火させる方法

### 2-1. Antigravity における Skill の仕組み

Skill は **`SKILL.md` を元にした「手順書＋トリガー条件」** です。[^3_8][^3_7]

- `~/.gemini/antigravity/skills/<skill-name>/SKILL.md`（グローバル）
または
`.agent/skills/<skill-name>/SKILL.md`（プロジェクトローカル）[^3_7][^3_8]
- 先頭に YAML frontmatter で `name` や `description` を定義し、その後に具体的な手順やガイドラインを記述。[^3_9][^3_8][^3_7]

モデル（Claude / Gemini）は、**ユーザー発話と `description`（や “When Activated” セクション）を照合して、「関連する Skill を起動するか」を判断**します。[^3_10][^3_9][^3_7]

### 2-2. 「強制トリガー文」の設計

Skill が抜けやすい原因は、

- description に書いたトリガー条件が曖昧
- 実際のプロンプトで、その条件に十分マッチしていない
- 長スレで会話の topic がぼやけている

といったケースです。[^3_10][^3_9]

#### (1) SKILL.md 側の書き方（必須）

**YAML `description` と “When Activated” セクションで、発火条件をかなり具体的に書く**のがベストプラクティスです。[^3_8][^3_9][^3_10]

```yaml
---
name: "code-review"
description: >
  Perform strict code review for source files in this repository.
  Use when the user asks to review, critique, or improve code quality,
  especially with phrases like "コードレビュー", "コードを見て", "レビューして".
---

## When Activated

This skill activates when:

- The user explicitly says: "コードレビューして", "コードをレビューして", "このコードを見て".
- The user runs the `/review` command.
- The user asks for feedback on code quality, structure, or best practices.
```

ポイント:

- `description` に **「Use when ...」形式で自然文の発火条件を書く**（公式/コミュニティで推奨のフォーマット）。[^3_9][^3_10]
- “When Activated” セクションで、**日本語の具体的なフレーズを列挙**しておくと Claude 側のマッチ精度が上がりやすい。[^3_8][^3_9]


#### (2) GEMINI.md に書くべきか？

**発火条件の「本体」は SKILL.md に置くのが基本**です。[^3_7][^3_9][^3_8]

- GEMINI.md は「グローバルな行動指針・安全ルール・トーン」向け。[^3_6][^3_4]
- Skills のトリガーや手順は、Skill単体で完結するように `SKILL.md` 側で定義するのが Antigravity の設計思想。[^3_7][^3_8]

ただし、あなたのように “日本語特有の言い回し” を多用する場合は、

- GEMINI.md 側に
「私が『○○して』と言ったら、優先的に skill `code-review` を使用して処理すること」
のような補助ルールを書いておくのは有効です。

> まとめると:
> - **主トリガー条件 → SKILL.md**
> - **ユーザー固有の言い回し・優先度調整 → 必要なら GEMINI.md に補助的に記述**

#### (3) チャット側の「強制トリガー文」の書き方（Claude 用）

Antigravity の codelab や実践ガイドでは、Skill がうまく動かない場合のデバッグとして、次のようなフレーズが推奨されています。[^3_9][^3_7]

- 「`Use skill code-review to ...`」
- 「`Use the "code-review" skill to review this diff.`」[^3_9]

Claude でもほぼ同様に効くので、日本語＋英語混在で**できるだけ明示的に書く**と安定します。

例:

- 「**必ず skill `code-review` を使って**、この PR 全体のレビューを行ってください。」
- 「次の作業は **Antigravity の `code-review` SKILL を使って**実行してください。」
- 「`Use skill "code-review"` to review the changes in these files.」

**Skill 名をダブルクォートまたはバッククォート付きで明示**し、`Use skill ...` という構文を含めると、ほぼ強制的に発火させられます。[^3_7][^3_9]

***

## 3. Context rot 対策（長スレッド + Claude）

### 3-1. Context rot の正体

コミュニティやプロ向けガイドでは、次のような現象が報告されています。[^3_11][^3_12]

- スレッドが肥大化し、過去の試行錯誤・雑談・エラー出力など「今は不要な情報」が大量に残る。
- モデルはそれらも含めて“現在の状況”として解釈しようとするため、
    - 意図しない古い方針をまだ有効とみなす
    - ルール/Skill が相対的に埋もれてしまう
    - 応答がぶれたり、同じ説明を繰り返したりする
- プロジェクトの規模が増えるほど、この「性能劣化」が顕著になる。[^3_11]


### 3-2. ベストプラクティス（Antigravity + Claude）

#### (1) ルールと設計ドキュメントに「責務を逃がす」

- **プロジェクト方針・制約・役割分担は、スレッドではなくファイルに固定**する。
    - 例: `AGENTS.md`, `ARCHITECTURE.md`, `CONVENTIONS.md` などに設計・方針を明文化し、
チャットでは「この方針に従って実装して」とだけ指示する。[^3_11][^3_8][^3_7]
- ルール系は `GEMINI.md` + `.agent/rules/*.md` に寄せる。[^3_5][^3_4][^3_6][^3_3]

→ これにより、「会話ログのどこかに一度書いたはずのルール」に依存せずに済みます。

#### (2) スレッドを「フェーズ単位」で分割し、要約で引き継ぐ

- ある程度話が進んだら、**そのフェーズのゴール・決定事項・残タスクを要約し、新スレッドに持ち替える**運用が推奨されています。[^3_11][^3_7]
- Claude は長コンテキストに強いとはいえ、**「過去 100 ターン分全部」を常に見るより、「直近の設計要約＋必要なドキュメント」の方が安定**しやすい、という報告が多いです。[^3_11]

実務的には:

- **1トピック / 1マイルストーンごとにスレッドを切る**イメージで運用
- 例:
    - 設計フェーズスレ → 「最終設計要約」を作る
    - 実装フェーズ用の新スレ → その要約と関連ファイルだけ渡す
- 「5〜10ラリーで必ず切る」という厳格なルールというより、
    - 方針が変わった
    - 大きな決定がまとまった
    - 途中経過が長くなってきて、会話の“文脈ノイズ”が増えた
くらいを目安に、**“1フェーズ終わり”と見なして要約 \& 新スレ**が扱いやすいです。


#### (3) ファイル参照ベースの指示に寄せる

- 長い会話ヒストリで説明を積み上げるより、**「このファイルを読んで、このポリシーに従って作業して」**という形で、常に最新の情報をファイルに集約する。[^3_8][^3_7][^3_11]
- 特に Claude は長文ドキュメントの読解に強いので、
    - 重要な仕様や方針は 1〜2 ファイルにまとめる
    - 必要なたびにそのファイルへの参照を明示する
ほうが、context rot の影響を受けにくいです。[^3_13][^3_11]


#### (4) Rules / Skills を「短く・明確に」

- ルールが長文化すると、それ自体がコンテキストを埋めてしまい、逆に重要部分が埋もれる、という指摘があります。[^3_11]
- `GEMINI.md` や `.agent/rules/*.md` は:
    - 上位概念としてのルールだけを書く
    - 詳細な手順や個別パターンは、Skill や別ドキュメントに逃がす
- Skill も同様に、
    - `description` は「やること」と「発火条件」のみに絞る
    - 細かい解説は下部のセクションに整理する
といった「レイヤリング」をすると、モデルの理解負荷が下がります。[^3_10][^3_8][^3_9]


#### (5) 「過去の会話に依存しすぎない」プロンプトにする

- 新しい作業を始める時は、できるだけ
    - 「前回までの前提は、この要約にまとまっている」
    - 「この要約と、このファイル群を前提として作業して」
と明示し、**古いラリーの細部に依存させない**のが有効です。[^3_7][^3_11]

***

## 4. まとめ（Antigravity + Claude 向けにやっておくと良いこと）

1. **GEMINI.md と Workspace Rules を `Always On` に整える**
    - Settings → Customizations → Rules で `GEMINI.md` と主要プロジェクトルールを `Always On` に。[^3_1][^3_4][^3_2][^3_3]
    - 中身は「共通ポリシー + プロジェクト固有の上位ルール」に絞る。
2. **Skill は SKILL.md の `description` / “When Activated” で細かくトリガーを定義**
    - 日本語トリガーフレーズを列挙。
    - `Use when ...` 形式で書く。[^3_10][^3_8][^3_9][^3_7]
3. **Claude に使わせたい時は、チャットで「Use skill `<name>` …」を明示**
    - 「必ず skill `code-review` を使って〜」と宣言してからタスクを書く。[^3_9][^3_7]
4. **Context rot 対策として、フェーズごとに要約 → 新スレ運用**
    - 長くなってきたら「このフェーズの最終要約」を作り、それを持って新スレで続行。
    - 方針や仕様はドキュメント／Rules／Skills に逃がす。

このあたりを固めると、「A: 長くなると Rules / Skills が抜ける」現象はかなり減るはずです。
もしよければ、いま使っている `GEMINI.md` / SKILL.md の断片を貼ってもらえれば、「この書き方だと Claude + Antigravity で抜けやすい」「ここをこう変えると安定する」といったリライトも具体的に提案できます。
<span style="display:none">[^3_14][^3_15][^3_16][^3_17]</span>

<div align="center">⁂</div>

[^3_1]: https://antigravity.google/docs/rules-workflows

[^3_2]: https://www.youtube.com/watch?v=TVRoodzA1DE

[^3_3]: https://ai-souko.jp/archives/249

[^3_4]: https://note.com/kino_11/n/n825b9f9e9dc1

[^3_5]: https://mindgard.ai/blog/google-antigravity-persistent-code-execution-vulnerability

[^3_6]: https://www.reddit.com/r/GoogleAntigravityIDE/comments/1pgf6dt/antigravitys_geminimd_file/

[^3_7]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^3_8]: https://note.com/munakata_souri/n/n052a421eab45

[^3_9]: https://qiita.com/TOMOSIA-LinhND/items/edb5f15ed4be0f875bff

[^3_10]: https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows/agent-skills

[^3_11]: https://www.reddit.com/r/ClaudeCode/comments/1qfoadh/claudes_feedback_on_variable_performance_issues/

[^3_12]: https://www.reddit.com/r/Bard/comments/1q8swz5/yes_the_1m_context_ai_cannot_read_even_a_20page/

[^3_13]: https://www.datastudios.org/post/claude-context-window-token-limits-memory-policy-and-2025-rules

[^3_14]: https://izanami.dev/post/cd7be4dc-3b23-49b6-85e3-a0d4f7b9adab

[^3_15]: https://dev.classmethod.jp/articles/antigravity-terminal-command-auto-execution/

[^3_16]: https://www.linkedin.com/posts/ujjyainimitra_%F0%9D%90%86%F0%9D%90%A8%F0%9D%90%A8%F0%9D%90%A0%F0%9D%90%A5%F0%9D%90%9E-%F0%9D%90%80%F0%9D%90%A7%F0%9D%90%AD%F0%9D%90%A2%F0%9D%90%A0%F0%9D%90%AB%F0%9D%90%9A%F0%9D%90%AF%F0%9D%90%A2%F0%9D%90%AD%F0%9D%90%B2-%F0%9D%90%93%F0%9D%90%A1-activity-7399759614738616320-chMd

[^3_17]: https://unikoukokun.jp/n/nd096dd7d4e42

