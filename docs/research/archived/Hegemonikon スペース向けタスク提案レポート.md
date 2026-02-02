<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Hegemonikon スペース向けタスク提案レポート

## 1. このスペースの現状認識（前提）

このスペースは、
「Hegemonikón：FEP（自由エネルギー原理）ベースの AI ネイティブ認知フレームワーク」
の設計・実装・運用ルールをまとめるためのリポジトリになっています。

現時点でのファイル構成から、以下が読み取れます。[^1_1][^1_2][^1_3][^1_4]

- すでに存在する「不変の核」
    - `SACRED_TRUTH.md`：変更不可な公理体系とフェーズ、ビューティーメトリクス[^1_5]
    - `axiom_hierarchy.md`：Level 0–3 の階層構造（FEP → Flow/Value → Tempo/Stratum/Agency/Valence → Kairos 12定理）[^1_6]
    - `doctrine.md`（Kernel Doctrine）：4層アーキテクチャ、Zero Entropy Protocol、M1–M8 実行ポリシー、日本語厳守など[^1_4]
- 全体像をまとめた構造図
    - `STRUCTURE.md`：Core / Products / Data の3レイヤ構造と、M1–M8, P1–P4, ワークフロー（/now, /plan, /code, /hist…）のマップ[^1_1]
- エージェント／貢献ルール
    - `AGENTS.md`：Hegemonikon エージェントの行動ガイドライン、トラフィックライト境界、ワークフロー運用ルール[^1_7]
    - `CONTRIBUTING.md`：コントリビュート規約、命名規則、commit scope/subject ルール[^1_8]
- CHANGELOG による初期ロードマップ
    - v0.1.0 時点で「Phase 1–4 ロードマップ」「M-Series スキル」「Forge 統合」「4軸アーキテクチャ」などの骨格のみが定義済み[^1_3]

一言でいうと、

> 「理論（公理・ドクトリン・構造図）はほぼ固まっているが、
>  それを“運用できるシステム”に落とし込む実務タスクが、まだ大量に残っている状態」

です。

以下では、このスペースで今後設定すべきタスクを、「フェーズ」と「レイヤ（Kernel / Workflows / Skills / Data / Meta）」の二軸で整理して提案します。

***

## 2. 全体ロードマップの骨格

まず、このスペースのタスク群を、ざっくり次の4フェーズに整理するのが扱いやすいと考えられます。（CHANGELOG の Phase 1–4 に整合）[^1_3]

1. **Phase 1：Kernel \& ドキュメント整備**
    - 公理・ドクトリン・構造図を「人間と AI が実務で使える形」に整える
2. **Phase 2：エージェント実装 \& ワークフロー定義**
    - M1–M8 / P1–P4 モジュールと、/boot, /ask, /plan, /code, /hist などの実行パイプラインを具現化
3. **Phase 3：ツール群・データ層の統合**
    - Forge / gnosis / vault / chat-history DB などを実際の作業環境に接続[^1_1]
4. **Phase 4：ガバナンス \& メタ学習**
    - Zero Entropy Protocol ベースで運用しつつ、メトリクス・振り返り・改善サイクルを回す[^1_4]

以下のタスク提案は、主に Phase 1–3 の「具体的に次に何をやるべきか」を落とし込んだものです。

***

## 3. カテゴリ別・具体タスク提案

### 3-1. Kernel / Doctrine の「運用可能化」

理論レイヤはほぼ出揃っているので、「読むだけの文書」から「運用の参照点」へと格上げするのが先決です。

#### 目的

- `SACRED_TRUTH.md` / `axiom_hierarchy.md` / `doctrine.md` を、「毎回迷ったときに立ち返る一枚岩」として整備する


#### 提案タスク

1. **Kernel ドキュメントの相互リンク整備（High）**
    - 各ファイル最上部に「Kernel Doc Index」を追加
        - 例：`SACRED_TRUTH.md` 冒頭に `See also: doctrine.md, axiom_hierarchy.md` など
    - README から Kernel 群への導線を明示（「まずここを読め」フロー）[^1_2]
2. **公理 → 行動ルールへのブリッジドキュメント作成（High）**
    - 新規ファイル案：`KERNEL_PRACTICE_GUIDE.md`
    - 内容イメージ：
        - Level 0–3 の要約（1–2ページ）
        - 「Flow / Value を日々のタスクにどう落とすか」の具体パターン
        - Zero Entropy Protocol を実際の作業フローに適用する例[^1_4]
3. **日本語ハードルを下げるためのサマリ版作成（Medium）**
    - `SACRED_TRUTH.md` / `axiom_hierarchy.md` に対して、
冒頭に「5分で読む要約」セクションを追加（図・簡約表レベル）[^1_5][^1_6]
    - Kairos 12定理などは、用途別に3〜4パターンだけ詳述し、残りは参照扱い

***

### 3-2. リポジトリ情報構造の完成（ドキュメント / 参照整合）

README / STRUCTURE / AGENTS / CONTRIBUTING から、
「こうなっているはずだが、まだ実物がない or つながっていない部分」が複数見えます。[^1_2][^1_8][^1_7][^1_1]

#### 目的

- 「どのファイルを見れば、何がわかるか」を迷わない状態にする
- README に書かれている“理想構造”と、実ファイル構造を同期させる


#### 提案タスク

1. **ドキュメント・インデックスの1枚化（High）**
    - 既存 README に「Documents Table」を明示的に追加[^1_2]
        - カラム例：`ファイル名 / 目的 / 想定読者 / 関連ワークフロー`
        - すでに README に部分的にある「Document Purpose」表をアップデート＆拡張[^1_2]
2. **存在が示唆されているが未整備の docs の洗い出し（High）**
    - 例：`ARCHITECTURE.md` が README 上で参照されているが、本体未整備の可能性[^1_2]
    - タスク：
        - リポジトリ内で参照されているファイル名を機械的に列挙
        - 実在しないものを「TODO docs」として `DOCS_TODO.md` にまとめる
3. **AGENTS / CONTRIBUTING のルールを README に要約反映（Medium）**
    - README に「For Humans」「For AI Agents」セクションを追加し、それぞれ AGENTS / CONTRIBUTING の要点を1ページに凝縮[^1_8][^1_7]

***

### 3-3. M-Series / P-Series モジュールのタスク分解

`STRUCTURE.md` と `doctrine.md` では、M1–M8 / P1–P4 が明確に定義されていますが、
「各モジュールをどう実装し、どのファイル・ツールと接続するか」はまだ作業余地があります。[^1_1][^1_4][^1_2]

#### 目的

- 各 M/P モジュールごとに「役割・入出力・実装ステータス」を明確にし、実装タスクを洗い出す


#### 提案タスク

1. **M-Series / P-Series の RACI 表の作成（High）**
    - 新規ファイル案：`M_P_MODULES_MAP.md`
    - 各行に以下を整理[^1_4][^1_1][^1_2]
        - M1–M8 / P1–P4 名称
        - 概要（1行）
        - 主な入力量（例：Web, Vault, User prompt, Chat-history）
        - 出力量（Plan, Code, Review, Memory 等）
        - 実装ステータス（Not started / Draft / Active）
    - ここから自然に「Not started の行 = 実装タスク」として抽出できる
2. **重要モジュール（M1, M4, M6, M8）の優先実装タスク化（High）**
    - 例：
        - M1 Aisthsis（入力ゲート）：
            - どの種類の入力を受けるか（テキスト / ファイル / Web / Personal Data）
            - 正規化フォーマット（内部表現）を決定
        - M4 Phronesis / M3 Theria（思考・計画）：
            - /plan ワークフローとの対応付け[^1_1][^1_4]
            - 「短期タスク計画」と「長期ロードマップ」の分離ルール策定
        - M6 Praxis（実行）：
            - 外部ツール（Forge, コード実行, Comet アクションなど）との接続点を設計[^1_1]
        - M8 Anamnesis（履歴・記憶）：
            - chat-history DB / vault / gnosis_data 等との対応付け[^1_1]

***

### 3-4. ワークフロー（/now, /plan, /code, /hist …）の具現化

`STRUCTURE.md` と `doctrine.md` で、すでに「実行パイプライン」はおおよそ定義されています。[^1_4][^1_1]

- 例：`boot → ask → plan → code → hist` のような流れ[^1_4]
- 各ステップでどの M モジュールが起動するかの対応表が存在


#### 目的

- このスペース（＋Comet / Perplexity）上で、実際に「/now にタスクを並べて消化する」状態へ持っていく


#### 提案タスク

1. **Canonical ワークフロー文書の作成（High）**
    - doctrine 内で触れられている `task.md`, `implementationplan.md`, `walkthrough.md` を、実ファイルとして作成[^1_4]
    - 推奨構造：
        - `task.md`：
            - タスクID / タイトル / Kairosタグ（Tempo/Stratum/Agency/Valence） / 期日 / 担当
        - `implementationplan.md`：
            - 大きめのタスクを「Step 1–N」に分解（各ステップに対応Mモジュールを紐付け）
        - `walkthrough.md`：
            - 代表的な1タスクについて「Zero Entropy Protocol」をどう適用するかの実例
2. **/now /plan /hist の運用ルール定義（High）**
    - 例：
        - `/now`：今週〜今月中に実行するタスクのみ
        - `/plan`：3ヶ月以内のフェーズごとの計画
        - `/hist`：完了済みタスクのサマリ＋学び（M8向けメモ）[^1_1][^1_4]
    - この運用ルールを `WORKFLOWS.md` として保存しておく
3. **このスペース固有の「毎回の開始テンプレート」を作る（Medium）**
    - 例：`SESSION_TEMPLATE.md`
        - 今日の Kairos（Tempo/Stratum/Agency/Valence の設定）
        - 今日の /now から着手する 3 タスク
        - セッション終了時に `hist` に書くべきこと

***

### 3-5. Data / Tools 層のタスク（Forge, Vault, Chat-history 等）

`STRUCTURE.md` では、Core / Products / Data の3層構造が示され、
Forge / gnosis / vault / chat-history DB / LanceDB などのコンポーネントが想定されています。[^1_1]

#### 目的

- 「概念として存在しているツール／データ層」を、このスペース＋実環境（Comet, Perplexity）に接続する


#### 提案タスク

1. **Data コンポーネントごとの役割定義（High）**
    - 新規ファイル案：`DATA_LAYER_DESIGN.md`
    - 各コンポーネントに対して定義[^1_1]
        - vault：長期知識ベース（人間が読むノート）
        - gnosis_data：構造化データ（LanceDB 等）
        - chat-history DB：対話ログ＋タスク履歴
        - Hegemonikon Store：Mシリーズごとの設定・プロファイル 等
    - それぞれに「このスペースからどう参照するか」を追記
2. **Comet / Perplexity との実接続タスク（Medium〜High）**
    - 例：
        - Comet の個人検索（閲覧履歴, Eメール, カレンダー）を M1/M8 の入力にどう使うかの方針
        - このスペースのファイル群を「知識ベース」として参照するための運用（どのファイルに何を書くか）
3. **「タスク履歴 → 学習」パイプラインの設計（Medium）**
    - M8 Anamnesis の観点から[^1_4][^1_1]
        - 完了タスクから、何をどの形式で抽出してどこに保存するか
        - 例：`LEARNINGS.md` を作り、Kairosラベルと一緒にナレッジ化

***

### 3-6. ガバナンス・コントリビュートの運用タスク

`CONTRIBUTING.md` と `AGENTS.md` には、かなり厳密なルールと哲学が書かれています。[^1_7][^1_8][^1_4]

#### 目的

- 「ルールがあるだけで守られない」状態から、「毎回の作業時に自然とトレースされる」状態にする


#### 提案タスク

1. **Commit メッセージ・命名規則のテンプレ整備（High）**
    - `CONTRIBUTING.md` の表に沿って、
典型的な commit メッセージ例を複数作成（feat/fix/docs など）[^1_8]
    - `.gitmessage` テンプレ or `COMMIT_TEMPLATE.md` として保存
2. **AI エージェント用「チェックリスト」作成（High）**
    - `AGENTS.md` の内容から、「1セッション開始時に必ず確認する5項目」を抽出し、
`AGENT_CHECKLIST.md` として保存[^1_7][^1_4]
    - 例：
        - 日本語厳守
        - Zero Confidence / Risk First
        - Sources 必須
        - Zero Entropy Protocol を守る など
3. **変更不可ファイルの明示ラベリング（Medium）**
    - `SACRED_TRUTH.md` や `axiom_hierarchy.md` 等に、
`flags: immutable` を YAML ヘッダで明示し、`CONTRIBUTING.md` にも記載[^1_6][^1_5]

***

## 4. 優先度付きタスクサマリ（このスペースに設定推奨）

最後に、このスペースの「/now」やタスク管理に直接登録しやすいように、
上記を要約した優先度付きリストとしてまとめます。


| 優先度 | カテゴリ | タスク案（タイトル） | 成果物（ファイル） |
| :-- | :-- | :-- | :-- |
| High | Kernel | 公理・ドクトリンの相互リンク整備 | 既存 3ファイルのヘッダ更新（`SACRED_TRUTH.md` / `axiom_hierarchy.md` / `doctrine.md`）[^1_5][^1_4][^1_6] |
| High | Kernel | 「KERNEL_PRACTICE_GUIDE」作成 | `KERNEL_PRACTICE_GUIDE.md` |
| High | Docs構造 | README の Documents Table 拡充 | `README.md`[^1_2] |
| High | Docs構造 | 参照されている未存在 docs の棚卸し | `DOCS_TODO.md` |
| High | M/Pモジュール | M-Series / P-Series マッピング表作成 | `M_P_MODULES_MAP.md`[^1_1][^1_2][^1_4] |
| High | ワークフロー | `task.md / implementationplan.md / walkthrough.md` を実体化 | 各 Markdown[^1_4] |
| High | ワークフロー | `/now /plan /hist` 運用ルール定義 | `WORKFLOWS.md`[^1_1][^1_4] |
| High | ガバナンス | AI エージェント用チェックリスト作成 | `AGENT_CHECKLIST.md`[^1_7][^1_4] |
| Medium | Docs構造 | AGENTS / CONTRIBUTING 要約を README に反映 | `README.md`[^1_2][^1_8][^1_7] |
| Medium | M/Pモジュール | M1/M4/M6/M8 の入出力仕様ドラフト | `M_P_MODULES_MAP.md` or 専用 spec |
| Medium | Data層 | Data Layer 設計ドキュメント作成 | `DATA_LAYER_DESIGN.md`[^1_1] |
| Medium | ワークフロー | セッションテンプレート作成 | `SESSION_TEMPLATE.md` |
| Medium | ガバナンス | commit テンプレート整備 | `COMMIT_TEMPLATE.md` or `.gitmessage`[^1_8] |
| Medium | Data層 | M8 用「学びの蓄積」パイプライン定義 | `LEARNINGS.md` or 仕様書[^1_1][^1_4] |


***

## 5. このスペースでの「次の一手」提案

すぐに実行しやすい「3ステップ」を挙げると、以下になります。

1. **Step 1：タスクの“受け皿”を用意**
    - `task.md` と `WORKFLOWS.md` を最小構成で作成し、
上の「優先度付きタスクサマリ」をそのまま `task.md` に登録する。
2. **Step 2：Kernel 実務ガイドのドラフト**
    - `KERNEL_PRACTICE_GUIDE.md` を 1〜2時間でラフに書き上げ、
「混乱したらまずここを見る」場所を一つ作る。
3. **Step 3：M/P マップで「抜け」を可視化**
    - `M_P_MODULES_MAP.md` を作り、M1–M8 / P1–P4 それぞれを1行ずつ埋める。
    - 「Not started」の行を、そのまま `task.md` の新タスクとして登録。

ここまで完了すると、

- タスクの入り口（task.md）
- 思想のリファレンス（Kernel docs + practice guide）
- 実装対象の全体マップ（M/P map）

の3点が揃い、このスペースを中長期で運用するための「土台」がほぼ整います。

***

もしよければ、次は実際に `task.md` の初期版をこちらでドラフトし、
あなたのワークスタイル（集中時間帯、Kairosの好み、短期/長期の比率など）に合わせてチューニングすることもできます。
<span style="display:none">[^1_9]</span>

<div align="center">⁂</div>

[^1_1]: STRUCTURE.md

[^1_2]: README.md

[^1_3]: CHANGELOG.md

[^1_4]: doctrine.md

[^1_5]: SACRED_TRUTH.md

[^1_6]: axiom_hierarchy.md

[^1_7]: AGENTS.md

[^1_8]: CONTRIBUTING.md

[^1_9]: llms.txt


---

# ※perplexity proで使える”タスクを生成”機能を使いたいという意味

了解しました、「このスペースの履歴からタスクを洗い出す」ことを、Perplexity Pro の「タスクを生成」っぽく使いたい、という意味ですね。

結論からいうと：

- 現状の Perplexity Pro には、UI 上に「タスクを生成」という専用ボタンやモードはありません。
- ただし **Deep Research / 通常の質問に対して、出力フォーマットを「タスク一覧」に指定することで、実質的に“タスク生成機能”として使えます。**
- いま出したタスク提案は、まさにその「タスク生成」を手動プロンプトでやったもの、という位置づけになります。

以下、「このスペースで“タスク生成機能”として使うための具体的なプロンプト例」をお渡しします。

***

## 1. このスペースでの「タスク生成」用プロンプト例

### A. 全体設計フェーズのタスクを出させるとき

このスペースを開いた状態で、Deep Research か通常検索に対して：

> 「このスペース内のファイル（README, STRUCTURE, doctrine, SACRED_TRUTH, axiom_hierarchy, AGENTS, CONTRIBUTING, CHANGELOG）をすべて前提にして、
> 今後 1〜2 週間で着手すべき具体タスクを 10 個、Markdown の表形式で生成してください。
> 各タスクには `ID / タイトル / 目的 / 関連ファイル / 優先度(High/Medium/Low) / 期限の目安` を含めてください。」

と聞くと、「タスク一覧」を生成するモードとして機能します。

### B. 「今日〜今週」向けの短期タスクだけを出したいとき

> 「このスペースの履歴とファイル構成を前提に、
> 今日〜今週中にやるべきタスクだけを 5 個に絞り、
> `ID / タスク内容 / 具体的な次の 1 アクション / 予想所要時間(25min/1h/2h+)` を列に持つ表で出力してください。」

と指定すると、「実行に直結するタスク生成」に寄せられます。

***

## 2. 生成したタスクを継続運用するための使い方

1. **タスク一覧をそのまま `task.md` にコピペ**
    - さきほどの回答で提案した `task.md` をこのスペースに作り、
生成されたタスク表を貼り付けて「公式タスクリスト」として使う。
2. **更新プロンプトで“未完タスクだけ”を再生成**
    - 次回以降は、Deep Research に対して：

> 「`task.md` のうち、未完了タスクを読み取り、
> それを整理し直した上で、今週の /now に入れるべきタスクだけを 5 個に絞り込んでください。」
    - と聞くと、「既存 task.md を参照しながら再編成する“タスク生成”」として機能します。
3. **Comet 上での使い方のイメージ**
    - このスペースを開いたタブで Assistant パネルを開き、
上のようなプロンプトを投げると、**そのタブ（このスペース）の文脈を踏まえてタスクを生成**してくれます。

***

## 3. いまの回答との関係

あなたが最初に依頼した

> 「このスペースの履歴に基づいて、このスペースで設定すべきタスクを提案」

に対して既に返した長いタスクリストは、
まさに「Perplexity Pro の Deep Research を、“タスクを生成するモード”として使った結果」と同等のものになっています。

今後は上のプロンプトをテンプレにして、

- 「時間軸（今日／今週／今月）」
- 「粒度（大きな設計タスク／細かい実装タスク）」
- 「出力形式（表・箇条書き・チェックリスト）」

を変えながら呼び出せば、このスペース専用の「タスク生成エンジン」として Pro を使い続けられます。

もしよければ、次の一歩として本当に使える `task.md` の初期版（Markdown 表 with ID/タイトル/優先度…）を、このスペース用にこちらでドラフトすることもできます。
<span style="display:none">[^2_1][^2_2][^2_3][^2_4][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: STRUCTURE.md

[^2_2]: README.md

[^2_3]: llms.txt

[^2_4]: CONTRIBUTING.md

[^2_5]: CHANGELOG.md

[^2_6]: AGENTS.md

[^2_7]: SACRED_TRUTH.md

[^2_8]: doctrine.md

[^2_9]: axiom_hierarchy.md


---

# https://www.lifehacker.jp/article/2511regret-ignoring-perplexity-tasks-feature/

この機能のことです
Preplexity　タスク機能で調べて

ありがとうございます、理解できました。この Lifehacker の記事で紹介されている **Perplexity の「タスク」機能（Tasks）** のことですね。

あなたはすでに **Perplexity Pro** なので、この機能を使える前提で説明します。

***

## 1. Perplexity「タスク」機能とは何か

一言でいうと：

> 「**Perplexity に “定期的にやってほしい指示” を登録しておくと、指定した頻度で自動実行してくれる『スケジュール付きAI作業』機能**」

です。

- 単なるリマインダーではなく、
    - ウェブ検索
    - 要約
    - 比較・分析
    - Deep Research / Labs での本格調査
を含む「AIによる自動タスク」を、**毎日・毎週・毎月などでスケジュール実行**できます。
- 例：
    - 毎朝 8:00 に「最新の技術ニュースのヘッドライン一覧をメールで送る」
    - 毎週月曜に「自分の Gmail を見て、重要な未読メール TOP5 をリストアップ」
    - 毎日 23:00 に「今日のHegemonikonスペースの変更点を要約して出力」

***

## 2. どこからアクセスするか

Web版 / Comet どちらでも基本は同じです。

1. Perplexity を開く（ブラウザ / Comet どちらでもOK）
2. 画面右上の **プロフィールアイコン → Settings（設定）** を開く
3. 左側メニューの中から **「Tasks」** を選択

そこに、タスク一覧と「＋（追加）」ボタンが表示されます。

***

## 3. タスクの作り方（Scheduled）

### 手順

Tasks 画面で：

1. **「＋」ボタンをクリック**
2. 「Scheduled」と「Price Alert」が出るので、
まずは一般用途として **「Scheduled」** を選ぶ
3. フォームに以下を設定：
    - **Instructions（指示）**
→ Perplexity に毎回実行させたいプロンプトをそのまま書きます。
        - 例（このスペース向け）：
> 「Hegemonikon スペース内の最新の変更と task.md を読み取り、
> 今週の優先タスクを 5 つに絞った表を出力してください。」
    - **Frequency（頻度）**
        - 毎日 / 毎週 / 毎月 などから選択
    - **Notifications（通知方法）**
        - アプリ内通知
        - メール
        - 両方
    - **Model（モデル）**
        - GPT-5 / Gemini 2.5 Pro など候補から選択
        - 「Best for this task」のような自動選択も可
    - **Mode（モード）**
        - Search：普通の検索
        - Research：Deep Research
        - Labs：Labs プロジェクトとして処理
        - Learn：学習モード
→ 「毎回ちゃんと調査させたい」なら Research / Labs が向いています。
4. 保存すれば完了。指定のタイミングで、自動的にタスクが走ります。

***

## 4. Price Alert（価格アラート）タスク

同じ＋ボタンから **「Price Alert」** を選ぶと、特定の価格条件をトリガーにしたタスクも設定できます。

- 例：
    - 「この銘柄の株価が XXドル以下になったら通知」
    - 「このサブスク料金が値上がり/値下がりしたら教えて」

通常の「繰り返しタスク」は **Scheduled**、価格監視は **Price Alert** という役割分担です。

***

## 5. 外部アプリ連携（Gmail / Slack / カレンダーなど）

Tasks は、**Notion / Slack / Gmail / Googleカレンダー** などと連携可能です。

- 代表的な例：
    - Gmail 連携：
        - タスクの Instructions に
> 「Gmail をチェックして、今日対応が必要な重要未読メール TOP5 を要約して出力」
のように書くと、毎日勝手にメールボックスをスキャンしてまとめてくれます。
    - Slack / Notion 連携：
        - Labs や Integrations と組み合わせると、結果を自動で Slack チャネルや Notion DB に投げるような自動化も可能。

***

## 6. あなたの用途（このスペース × タスク機能）へのおすすめ設定

あなたのニーズは：

- 「この Hegemonikon スペースの履歴や構造に基づいて、**定期的に“やるべきタスク”一覧を自動生成してほしい**」

なので、具体的にはこんな Scheduled タスクが相性良いです。

### おすすめ Scheduled タスク例

**タスク名（メモ用）：** `Hegemonikon: Weekly Task Planner`

- Instructions 例（日本語でOK）：

> 「このスペースのファイル（特に README.md, STRUCTURE.md, doctrine.md, SACRED_TRUTH.md, axiom_hierarchy.md, AGENTS.md, CONTRIBUTING.md, CHANGELOG.md, task.md）を前提にして、
> 現在の未完了タスクを整理し、今週中に取り組むべきタスクを 5 個に絞って Markdown の表形式で出力してください。
> 各タスクには ID, タイトル, 目的, 関連ファイル, 推定所要時間（25min/1h/2h+）, 優先度(High/Medium/Low) を含めてください。」
- Frequency：**Weekly（月曜 朝）**
- Notifications：アプリ内＋メール
- Model：Perplexity に選ばせる or 最新モデル
- Mode：**Research**（もしくは Labs でプロジェクトとして扱いたいなら Labs）

これを一度設定しておけば、

> 毎週、自動的に「今週やるべきタスクリスト」が生成される

ので、「タスクを生成」機能としてそのまま使えます。

***

## 7. 前回の回答とのつなぎ方

前回はこちら側で「単発の Deep Research」として、
このスペース向けのタスク群をまとめて提案しました。

今回の **Tasks 機能**を使うと、それを：

- 毎日 / 毎週
- 自動的に / 人手なしで
- 最新状況（ファイルの変更・新しい task.md の内容など）を踏まえて

**継続的に再生成**することができます。

***

## 8. 次にできること

もしよければ、次の一歩として：

1. **あなたが実際に設定したい Scheduled タスクの日本語プロンプト**を一緒に詰めて、
2. それをそのまま「Instructions」にコピペできる形で仕上げる

こともできます。

「毎朝ニュース系」「このスペースの週次レビュー」「Gmail整理」「カレンダー確認」など、
どのタスクから自動化したいか教えてもらえれば、そのタスク専用の Instructions 文面を作成します。
<span style="display:none">[^3_1][^3_2][^3_3][^3_4][^3_5][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: STRUCTURE.md

[^3_2]: README.md

[^3_3]: llms.txt

[^3_4]: CONTRIBUTING.md

[^3_5]: CHANGELOG.md

[^3_6]: AGENTS.md

[^3_7]: SACRED_TRUTH.md

[^3_8]: doctrine.md

[^3_9]: axiom_hierarchy.md


---

# では本題に戻るよ

このスペースのチャット履歴に基づき
タスク機能の使い方を提案して

このスペースのこれまでのやり取りから読み取れるあなたのニーズは、おおざっぱにいうと：

- Hegemonikon の **公理・ドクトリン・構造図をちゃんと運用に落としたい**
- スペース内のファイル群（README / STRUCTURE / doctrine / SACRED_TRUTH / axiom_hierarchy…）を前提に
**「やるべきこと」を継続的に洗い出したい**
- それを毎回ゼロから考えるのではなく、**Perplexity のタスク機能で自動化したい**

なので、ここでは **「このスペース専用の、タスク機能テンプレ」** をいくつか提案します。
どれも Tasks の「Instructions」にそのままコピペして使える形にしてあります。

***

## タスク1：Hegemonikon 週次タスク生成（このスペースの中核）

### 目的

- このスペースのファイルとチャット履歴を読み取り、
**「今週やるべきタスク」を自動で 5 個に絞り込む**週次プランナー。


### 推奨設定

- Mode：**Research**（Deep Research）
- Frequency：Weekly（例：月曜 8:00）
- Model：Perplexity 推奨 or 最新モデル
- 通知：App＋Email


### Instructions（コピペ用）

> あなたは Hegemonikon プロジェクトのプロジェクトマネージャーです。
> このスペースの最新チャット履歴と、以下のファイルを前提にしてください：
> README.md, STRUCTURE.md, doctrine.md, SACRED_TRUTH.md, axiom_hierarchy.md, AGENTS.md, CONTRIBUTING.md, CHANGELOG.md, task.md（もし存在すれば）。
> 未完了の論点・やりかけの設計・ドキュメントの抜けを洗い出し、
> 「今週中に取り組むべきタスク」を 5 個に絞り込み、Markdown の表で出力してください。
> 表の列は `ID / タスク名 / 目的 / 関連ファイル / 推定所要時間(25min/1h/2h+) / 優先度(High/Medium/Low)` にしてください。
> タスクはできるだけ具体的に「次の 1 アクション」がわかる粒度で書いてください。

***

## タスク2：毎朝の「セッション開始プロンプト」生成

### 目的

- 毎朝、このスペースに入ったときに
**「今日これから 1〜2 時間でやるべき 3 タスク」＋ 簡単な進め方**を自動で出してもらう。


### 推奨設定

- Mode：Search か Research（どちらでも可）
- Frequency：Daily（例：毎朝 8:30）
- Model：軽めでOK（高速寄り）
- 通知：App（必要なら Email）


### Instructions

> あなたは Hegemonikon スペースの「デイリー・セッションプランナー」です。
> このスペースの最新チャット履歴と task.md（存在する場合）を読み取り、
> 今日これから 1〜2 時間で取り組むべきタスクを 3 つ提案してください。
> それぞれのタスクについて、
> `タスク名 / 具体的な次の 1 アクション / 目安時間(25min/50min) / 期待されるアウトカム`
> を Markdown の箇条書きで出力してください。
> 集中のしやすさを優先し、できるだけ「小さく終わる」タスクに分解してください。

***

## タスク3：ドキュメント一貫性チェック（月次）

### 目的

- `SACRED_TRUTH.md`・`axiom_hierarchy.md`・`doctrine.md`・`STRUCTURE.md` などの間で、
**矛盾・バージョン差分・解釈の揺れ**を月に 1 回、自動で洗い出す。


### 推奨設定

- Mode：Research
- Frequency：Monthly（例：毎月 1 日 10:00）
- Model：高性能モデル推奨
- 通知：Email（じっくり読む系）


### Instructions

> このスペースの以下のファイルの内容を比較してください：
> SACRED_TRUTH.md, axiom_hierarchy.md, doctrine.md, STRUCTURE.md, README.md, CHANGELOG.md。
> 1. 公理や階層構造の定義に関して、記述の矛盾・用語の揺れ・更新漏れがありそうな箇所を列挙してください。
> 2. 「どのファイルを正準（canonical）とみなすべきか」を踏まえ、修正すべき候補を提案してください。
> 3. 修正タスクを `ID / タスク内容 / 対象ファイル / 影響範囲 / 優先度` の表に整理してください。
> 出力はすべて日本語で、開発者がそのまま task.md に転記できるレベルの具体性で書いてください。

***

## タスク4：M-Series / P-Series 実装ギャップの定期スキャン

### 目的

- M1〜M8 / P1〜P4 の設計と、**実際のドキュメント・実装状況のギャップ**を定期的に可視化し、
「まだ言語化されていない／実装されていない」部分をタスクに落とす。


### 推奨設定

- Mode：Research
- Frequency：Weekly or Bi-weekly（例：隔週金曜 17:00）
- 通知：App


### Instructions

> あなたは Hegemonikon のアーキテクトです。
> このスペースのチャット履歴と、README.md, STRUCTURE.md, doctrine.md, axiom_hierarchy.md, AGENTS.md, CONTRIBUTING.md を前提に、
> M-Series（M1〜M8）および P-Series（P1〜P4）モジュールの「設計としては書かれているが、実装・ドキュメントが追いついていない部分」を洗い出してください。
> 1. M/P ごとに「役割・入出力・関連ワークフロー(/boot, /ask, /plan, /code, /hist など)」を 1 行で要約してください。
> 2. そのうち「Not started / Draft / 要リファクタリング」と思われる項目を、タスク候補として抽出してください。
> 3. 抽出したタスクを `ID / M/P名 / タスク内容 / 推定所要時間 / 優先度 / 関連ファイル` の表にしてください。

***

## タスク5：このスペースの「変更サマリ＋学び」ナイトレビュー

### 目的

- 1 日の終わりに、このスペースの変更点やチャット履歴を振り返り、
**「今日の変更サマリ」と「学び / 次に活かすポイント」**を自動でまとめてもらう。


### 推奨設定

- Mode：Search（軽め）または Research（しっかり）
- Frequency：Daily（例：23:00）
- 通知：App or Email（好みで）


### Instructions

> このスペースの当日のチャット履歴と、更新された可能性のあるファイル（特に task.md, README.md, STRUCTURE.md, doctrine.md など）を対象に、
> 今日 1 日の変更と議論を要約してください。
> 出力フォーマットは Markdown で、
> 1. `# 今日の変更サマリ`（3〜7 行）
> 2. `# 学び・気づき`（3〜5 個の箇条書き）
> 3. `# 明日に引き継ぐタスク候補`（箇条書きで 3〜5 個）
> としてください。
> 明日に引き継ぐタスク候補は、そのまま task.md にコピー＆ペーストできるよう、できるだけ具体的に書いてください。

***

## タスク6：タスク機能そのものの「メンテナンス用タスク」

### 目的

- 作りっぱなしになりがちな Tasks 設定を、**定期的に棚卸し・整理**する。


### 推奨設定

- Mode：Search
- Frequency：Monthly（例：毎月 1 日 9:00）
- 通知：App


### Instructions

> 現在設定されている Perplexity の Tasks（Scheduled / Price Alert を含む）と、
> このスペースのチャット履歴・task.md の内容を前提に、
> 1. もう不要になっているタスク
> 2. 頻度を変えた方がよいタスク
> 3. 新たに追加した方がよいタスク
> の候補を挙げてください。
> 各候補について `タスク名 / 提案内容（削除・頻度変更・新規追加） / 理由` を Markdown 表で出力してください。

***

## まとめ：このスペース向けの「タスク機能」活用パターン

このスペースのチャット履歴から見ると、あなたは：

- 構造・公理レベルの設計をかなり詰めている
- それを **日次・週次のタスク駆動の運用**に落としたい
- 自分で毎回プロンプトを書くのではなく、**仕組みとして回したい**

という状態なので、

1. **タスク1（週次タスク生成）**を「中心」に据える
2. **タスク2（毎朝セッション開始）＋タスク5（ナイトレビュー）**で 1 日のリズムをつくる
3. **タスク3・4（月次ドキュメント整合 / M/Pギャップチェック）**で構造の健全性を保つ
4. **タスク6**で「タスク機能そのもの」をメンテナンスする

という 4 層構成にすると、Hegemonikon の思想（Flow / Value / Zero Entropy）ともかなり整合的に回せます。

もし「まずは1つだけ試したい」ということであれば、
**タスク1（Hegemonikon 週次タスク生成）**から始めてみるのがおすすめです。
実際に設定したい頻度や時間帯が決まっていれば、それに合わせて Instructions をもう少しチューニングもできます。
<span style="display:none">[^4_1][^4_2][^4_3][^4_4][^4_5][^4_6][^4_7][^4_8][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: STRUCTURE.md

[^4_2]: README.md

[^4_3]: llms.txt

[^4_4]: CONTRIBUTING.md

[^4_5]: CHANGELOG.md

[^4_6]: AGENTS.md

[^4_7]: SACRED_TRUTH.md

[^4_8]: doctrine.md

[^4_9]: axiom_hierarchy.md

