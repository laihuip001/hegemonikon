---
created: 2026-01-01T11:16:37 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/97785
author: AIDB Research
---

# LLMにエピソード記憶のような能力を持たせるRAGのテクニック - AIDB

> ## Excerpt
> 本記事では、人間のようなエピソード記憶をLLMに持たせるための新しいフレームワークを紹介します。 通常のRAGでは苦手な「時間の経過にともなう役割や状態の変化を追いかけること」を、脳の記憶のしくみをヒントにして扱えるようにしています。 本記事の関連研究 背景 LLMは、仕事のさまざまな場面で使われるようになってきましたが、長い文書を扱うときには根本的な課題があります。ひとつは、LLMが一度に処理で…

---
本記事では、人間のようなエピソード記憶をLLMに持たせるための新しいフレームワークを紹介します。

通常のRAGでは苦手な「時間の経過にともなう役割や状態の変化を追いかけること」を、脳の記憶のしくみをヒントにして扱えるようにしています。

![[LLMにエピソード記憶のような能力を持たせるRAGのテクニック - AIDB/AIDB_97785-1024x576.png]]

**本記事の関連研究**

-   [RAGで取得すべき情報はLLMごとの「データの有用性」で異なる](https://ai-data-base.com/archives/96511)
-   [LLM自体の性能が飛躍的に向上した今、RAGに求められることとは](https://ai-data-base.com/archives/96364)
-   [RAGの実用性レベルを上げるために「データソースを構造化する」という考え方](https://ai-data-base.com/archives/96111)

## 背景

LLMは、仕事のさまざまな場面で使われるようになってきましたが、長い文書を扱うときには根本的な課題があります。ひとつは、LLMが一度に処理できる文字数（「コンテキストウィンドウ」）に限りがあり、膨大な資料をそのまま読み込ませることができない点です。さらにやっかいなのは、コンテキストウィンドウに収まる長さであっても、文書が長くなるほどLLMの理解精度が下がると報告されていることです。

こうした問題への現在の代表的な解決策が「RAG」と呼ばれる手法です。RAGでは、文書を小さな「チャンク」に分割し、それぞれを意味的な埋め込みベクトルに変換してデータベースに保存します。ユーザーが質問すると、その質問に最も関係の深いチャンクだけを検索して取り出し、LLMに渡します。必要な部分だけを効率よく参照できるため、事実に基づく質問応答にはうまく機能します。

一方で、標準的なRAGには大きな弱点もあります。チャンクは個別に埋め込まれ、個別に検索されるため、チャンク同士のつながりや流れが見えにくくなってしまいます。

解決のヒントになりそうなのは人間の「エピソード記憶」です。エピソード記憶とは、特定の時間と場所に結びついた個人的な経験の記憶のことです。私たちが現実世界で計画を立てたり推論したりするうえで欠かせない能力です。さらに人間は、複数の経験をまたいで推論することで、新しい世界モデルを作ったり、既存のモデルを更新したりできます。

しかし現在のRAG手法は、「時間とともに変化する役割や状態」を追跡したり、「いつ・どこで起きたか」という時空間的な文脈を正確に押さえたりする仕組みが十分ではありません。つまり、ビジネス文書や報告書のように「エピソード的な記憶」が求められる文書を扱う場面では、まだ大きな改善の余地があるということです。

そこで本記事ではLLMにエピソード記憶のような能力を持たせるテクニックについて取り上げます。

ここから限定コンテンツ

### **忙しい人向けに、重要なポイント5選**

1.  LLMは長文を扱うのが苦手で、標準的なRAGは「時間とともに変化する役割や状態」を追跡する仕組みが不十分
2.  本手法は人間の脳（大脳新皮質と海馬）の記憶処理を模倣し、アクターの役割・状態・時空間情報を構造化して記録するフレームワーク
3.  Operatorがテキストから意味要素を抽出し、Reconcilerがそれらを統合・更新することで、一貫したエピソード記憶を構築
4.  EpBenchでの評価では、既存手法よりF1スコアで10%以上高い0.85を達成し、特に複雑な質問で再現率が約20%向上した
5.  エンティティ単位の要約を生成することで、LLMに渡すトークン数を約51%削減しながら、高い精度を維持できる

**参照文献情報**

-   タイトル：Beyond Fact Retrieval: Episodic Memory for RAG with Generative Semantic Workspaces
-   URL：[https://doi.org/10.48550/arXiv.2511.07587](https://doi.org/10.48550/arXiv.2511.07587)
-   著者：Shreyas Rajesh, Pavan Holur, Chenda Duan, David Chong, Vwani Roychowdhury
-   所属：University of California, Los Angeles

## 脳の働きをまねして情報を整理する

### 記憶のしくみをヒントに設計

脳科学の研究では、大脳新皮質は「誰が」「何を」「どんな役割で」といった情報を、段階的に整理して理解すると考えられています。一方で、海馬は、そうして整理された情報を「いつ」「どこで」といった時間や場所の流れにそって並べる役割を持つとされています。

眠っているあいだには「経験の再生」と呼ばれる現象も起きます。脳は睡眠中に、過去の出来事を前から後ろへ、あるいは逆向きに何度もたどり直します。その結果、記憶が定着し、頭の中の世界のイメージが少しずつ整理されていくと考えられています。大脳新皮質と海馬が協力することで、覚えたことを長く保ち、先を見通した判断がしやすくなるという見方です。

こうした脳の仕組みは、記憶を扱うフレームワークを設計するときのヒントになります。

### LLMが文章と意味の構造を変換し合う

LLMの登場により、この双方向の対応づけが現実的になってきました。LLMは、テキストから簡潔な意味要素を取り出すことができますし、逆にその意味要素から自然な文章を組み立てることもできます。この性質を活かせば、コンパクトな意味のメモだけを保存しておき、必要になったときに文脈に合わせて文章として呼び起こす、といった効率的な記憶のモデルを作りやすくなります。

### Operatorが文章から登場人物の役割や状態、時間と場所を抜き出す

フレームワークの中心になるのが「Operator（オペレーター）」と「Reconciler（リコンサイラー）」という2つのモジュールです。まず、Operatorについて説明します。

Operatorは、入力された文章を読み取り、そこに含まれる意味の要素を抜き出す役割を持ちます。

たとえば「昨日、強盗事件の通報を受けて、法執行官がダウンタウン地区でグリーンビュー通り在住の32歳、ジョナサン・ミラーを逮捕した」という文があったとします。

この文から、Operatorはいくつかの重要な要素を取り出します。

下記にまとめます。

|     要素     |         ざっくりした意味          |         例（ミラーのケース）         |
|------------|---------------------------|----------------------------|
|    アクター    |          登場人物や組織          |       ジョナサン・ミラー、法執行官       |
|     役割     |     その人がどんな立場かを示すラベル      |          犯罪者、法執行官          |
|     状態     |      いまその役割の中でどんな状況か      |          逮捕されている           |
|   動詞とその価   | 何が起きたかという動きと、その前後でどう変化するか | 逮捕することで、自由な状態から逮捕された状態に変わる |
|   時間と場所    |       出来事がいつどこで起きたか       |        昨日、ダウンタウン地区         |
| 未来予測のための質問 |   これから起こりそうなことを考えるための問い   |  いつ起訴されるか、裁判はいつどこか、保釈されるか  |

Operatorは、すべての要素をまとめ上げ、一つの「ワークスペース」インスタンスとして表現します。数式としては、アクター（A）、役割（R）、状態（S）、動詞（V）、時間（T）、空間（X）、質問（Q）といった要素が、それまでの文脈から決まる確率分布としてモデル化されます。

以下にOperatorに与えるべきプロンプトを、原文と日本語版の両方で示します。

原文

```
User Prompt:
You are required to perform the operator extraction, you should follow the following steps:
Task 1: Actor Identification
Your first task is to identify all actors from the given context. An actor can be:
1. A person (e.g., directors, authors, family members)
2. An organization (e.g., schools, festivals)
3. A place (e.g., cities, countries)
4. A creative work (e.g., films, books)
5. A temporal entity (dates, years)
6. A physical object or item (e.g., artifacts, products) 
7. An abstract entity (e.g., awards, concepts that function as actors)
Guidelines for Actor Extraction:
- Ground actor extraction in the given situation (&lt;situation&gt;) and the background context 
(&lt;background_context&gt;).
- It is crucial that you follow the above, since we will attempt to merge relevant actors across chunks in the next 
step.
...
[Description of state identification task]
Task 4: Explicit Verb Phrase Identification
[Description of verb phrase identification task]
Task 4.5: Implicit Action Phrase Inference
[Description of implicit action phrase inference task]
Task 5: Prototypical Semantic Role Question Generation
[Description of semantic role question generation task]
Task 6: Answer Mapping and Actor Connection
[Description of answer mapping task]
Inputs:
Input Text: " Input chunk to be processed by the operator" 
Background Context: " This chunk places the chunking within the entire document, providing context to the 
chunk.
Situation: " The situation that is presented in this chunk"
```

日本語訳

```
ユーザープロンプト:
あなたには Operator 抽出を行ってもらいます。次の手順に従ってください。

タスク1: アクターの特定
最初のタスクは、与えられたコンテキストからすべてのアクターを特定することです。アクターになり得るものは次の通りです。
1. 人物（例: 監督、著者、家族）
2. 組織（例: 学校、フェスティバル）
3. 場所（例: 都市、国）
4. 創作物（例: 映画、本）
5. 時間的な実体（例: 日付、年）
6. 物理的な対象やアイテム（例: 遺物、製品）
7. 抽象的な実体（例: 賞、アクターとして機能する概念）

アクター抽出のガイドライン:
- アクターの抽出は、指定された状況 (&lt;situation&gt;) と背景コンテキスト (&lt;background_context&gt;) に必ず基づけてください。
- 次のステップでチャンクをまたいで関連するアクターを統合しようとするため、上記の点に従うことが非常に重要です。

...
[状態識別タスクの説明が入る部分]

タスク4: 明示的な動詞句の同定
[動詞句識別タスクの説明が入る部分]

タスク4.5: 暗黙的な行為句の推論
[暗黙的行為句推論タスクの説明が入る部分]

タスク5: 典型的な意味役割質問の生成
[意味役割質問生成タスクの説明が入る部分]

タスク6: 答えのマッピングとアクターの接続
[回答マッピングタスクの説明が入る部分]

入力:
Input Text: 「Operator によって処理される入力チャンク」
Background Context: 「このチャンクが文書全体の中でどこに位置するかを示し、チャンクに文脈を与えるテキスト」
Situation: 「このチャンクで提示されている状況の説明」
```

### Reconcilerがばらばらの情報をまとめて一つの記憶として整理する

Operatorが各テキストから意味の要素を取り出すのに対して、Reconcilerはそれらをまとめて、一貫した全体像を作り直す役割を持ちます。

新しいテキストが入るたびに、Reconcilerが既存のワークスペースと新しい情報を見比べて、矛盾がないように整理しながら更新していきます。

この更新は、何度も積み重ねる形で進みます。前のステップで作られたワークスペースを土台にして、新しい情報を少しずつ足していくイメージです。

以下に、Reconcilerに与えるべきプロンプトを、原文と日本語版の両方で提示します。

原文

```
User Prompt:
You are the Reconciler module in a Generative Semantic Workspace (GSW) for episodic memory.

Your goal is to take:
1) the current global workspace,
2) the new local semantic maps produced by the Operator for the latest chunk, and
3) the list of currently unanswered queries,

and produce an updated workspace that is temporally, spatially, and logically coherent, while resolving as many queries as possible.

You must ONLY use information contained in the inputs. Do not invent new facts that are not implied by the workspace or the new context.

--------------------
Inputs
--------------------
1. Current Workspace (&lt;current_workspace&gt;):
   A structured semantic workspace that contains:
   - Actors (with stable IDs, types, names, and descriptions)
   - Events and actions (including which actors participate and in what roles)
   - States of actors over time
   - Spatiotemporal information (locations, times, timelines)
   - Links between actors, events, times, and places
   - Any previously recorded contradictions or uncertainties

2. New Operator Output (&lt;new_operator_maps&gt;):
   The semantic maps extracted from the latest text chunk by the Operator:
   - Newly detected actors, events, states, times, and locations
   - Local relations between them
   - Local cues for coreference, ellipsis, and anaphora (e.g. pronouns, “he”, “she”, “there”, “then”)

3. Unanswered Queries (&lt;unanswered_queries&gt;):
   A list of questions that the system has not yet been able to answer.
   Each query includes:
   - A unique query_id
   - The natural language question
   - Any known cues (actors, times, locations, events) that are relevant

--------------------
Your tasks
--------------------

Task 1: Entity Reconciliation
You must reconcile actors from the new Operator output with actors in the current workspace.

- Decide, for each new actor, whether it:
  (a) matches an existing workspace actor (same underlying person, place, organization, etc.), or
  (b) should be added as a new actor.

- Use all available evidence:
  - Names, aliases, descriptions
  - Roles and actions
  - Time and location of participation
  - Coreference cues (e.g. “he”, “she”, “the professor”, “the museum”)

- When you merge actors:
  - Preserve the original workspace actor_id.
  - Extend the actor’s description with non-contradictory information.
  - Record any remaining uncertainty or alternative hypotheses as notes.

- If two actors might be the same but evidence is weak or ambiguous, keep them separate and mark the relation as “possibly_same_actor” instead of forcing a merge.

Task 2: Space/Time Reconciliation
You must integrate spatiotemporal information from the new Operator output into the workspace.

- Align new timestamps or date expressions to the existing timeline whenever possible.
  - If a new time is more specific (e.g. “May 31, 2024” vs “May 2024”), keep the more specific representation and link the coarser one to it.
  - If times conflict, prefer the reading that is most consistent with the majority of evidence in the workspace, but record the alternative as a “conflicting_time_hypothesis”.

- Align new locations with existing spatial entities:
  - Merge places when they clearly refer to the same entity (e.g. “Metropolitan Museum of Art” and “the museum”).
  - Maintain hierarchies when implied (e.g. room → building → city).

- Attach events and actor states to the appropriate time and place anchors in the workspace, updating the sequence of events so that it remains logically consistent.

Task 3: Event, State, and Relation Update
You must update the workspace-level events, states, and relations to reflect new information.

- For each event from the new Operator output:
  - Decide whether it corresponds to an existing event in the workspace or should be added as a new event.
  - Merge when the same occurrence is being described with additional detail.
  - Preserve the event_id of any existing event that is being enriched.

- For each actor state:
  - Append new states to the actor’s timeline instead of overwriting past states.
  - If a state directly contradicts a previous state at the same time, keep both and mark this as a “state_conflict”.

- Update relations between actors, events, times, and places so that the workspace encodes:
  - Who did what, when, and where
  - How their states changed as a result of events

Task 4: Question Reconciliation and Answer Update
You must use the updated workspace to attempt to answer previously unanswered queries.

- For each query in &lt;unanswered_queries&gt;:
  1) Check whether the updated workspace now contains enough information to answer it.
  2) If yes, produce a concise, factual answer grounded in the workspace.
  3) If partially answerable, provide the partial answer and state clearly what is still unknown.
  4) If still unanswerable, explain briefly what information is missing.

- When answering, always:
  - Refer indirectly to the underlying workspace entities (e.g. by their IDs or names).
  - Ensure that the answer is consistent with all non-conflicting evidence.
  - Prefer answers that respect the temporal and spatial constraints encoded in the workspace.

--------------------
Output format
--------------------

Return a single JSON object with the following top-level keys:

{
  "updated_workspace": {
    "actors": [...],
    "events": [...],
    "states": [...],
    "spacetime": [...],
    "relations": [...],
    "notes": [...]
  },
  "entity_alignment": [
    {
      "new_actor_id": "&lt;id in new_operator_maps&gt;",
      "workspace_actor_id": "&lt;id in current_workspace or null&gt;",
      "status": "merged | new | ambiguous",
      "comment": "&lt;short explanation&gt;"
    },
    ...
  ],
  "resolved_queries": [
    {
      "query_id": "&lt;id&gt;",
      "status": "answered | partially_answered",
      "answer": "&lt;short natural language answer&gt;",
      "support": {
        "actors": ["&lt;actor_id&gt;", ...],
        "events": ["&lt;event_id&gt;", ...],
        "spacetime": ["&lt;time_or_place_id&gt;", ...]
      }
    },
    ...
  ],
  "unresolved_queries": [
    {
      "query_id": "&lt;id&gt;",
      "status": "unanswered | contradictory | insufficient_information",
      "reason": "&lt;short explanation of what is missing or conflicting&gt;"
    },
    ...
  ]
}

Make sure the JSON is syntactically valid and that all IDs used in the query sections refer to elements that exist in the updated workspace.
```

日本語訳

```
ユーザープロンプト:
あなたはエピソード記憶用の Generative Semantic Workspace（GSW）における Reconciler モジュールです。

あなたの目的は次の三つを入力として受け取り、
1) 現在のグローバルなワークスペース
2) 最新チャンクに対して Operator が生成したローカルなセマンティックマップ
3) まだ未回答のクエリのリスト

時間・空間・論理の整合が取れた更新済みワークスペースを構成し、可能なかぎり多くのクエリを解決することです。

与えられた入力に含まれない事実を勝手に作らないでください。ワークスペースや新しいコンテキストから論理的に示唆されることのみに基づいて推論します。

--------------------
入力
--------------------
1. 現在のワークスペース（&lt;current_workspace&gt;）
   構造化されたセマンティックワークスペースで、次を含みます。
   - アクター（安定した ID、種類、名前、説明）
   - 出来事・行為（どのアクターがどの役割で関わっているか）
   - アクターの状態の時間変化
   - 時間・場所に関する情報（ロケーション、時刻、タイムライン）
   - アクター・イベント・時間・場所のリンク
   - これまでに記録された矛盾や不確実性のメモ

2. 新しい Operator 出力（&lt;new_operator_maps&gt;）
   最新のテキストチャンクから Operator が抽出したセマンティックマップです。
   - 新しく検出されたアクター、イベント、状態、時間、場所
   - それらの間の局所的な関係
   - 代名詞などによる共参照・省略・照応の手がかり（例: “he”, “she”, “there”, “then”）

3. 未回答クエリ（&lt;unanswered_queries&gt;）
   まだ回答できていない質問のリストです。各クエリは次を含みます。
   - 一意な query_id
   - 自然文の質問文
   - 関連しそうなアクター・時間・場所・イベントなどの手がかり（わかっている場合）

--------------------
タスク
--------------------

タスク1: エンティティ（アクター）の統合
新しい Operator 出力に含まれるアクターを、ワークスペース内のアクターと照合・統合します。

- 各新規アクターについて、次のいずれかを判断します。
  (a) 既存のワークスペースアクターと同一（同じ人物・場所・組織など）
  (b) 新しいアクターとして追加すべき

- 次の手がかりを総合的に使います。
  - 名前や別名、説明文
  - 担っている役割と行動
  - 登場する時間・場所
  - “he”“she”“the professor”“the museum” などの共参照表現

- アクターをマージする場合
  - ワークスペース側の actor_id をそのまま維持します。
  - 矛盾しない範囲で説明を拡張します。
  - まだ残る不確実性や代替仮説があれば、メモとして残します。

- 同一かもしれないが確信が持てない場合は、無理にマージせず別アクターとして保持し、
  関係を「possibly_same_actor（同一の可能性）」として記録します。

タスク2: 時間・空間情報の統合
新しい Operator 出力の時空間情報を、既存のワークスペースのタイムラインに統合します。

- 新しい時刻表現を既存の時間軸にそろえます。
  - 例: “May 31, 2024” と “May 2024” が同じ出来事を指すなら、より具体的な方を代表として採用し、
    粗い表現はそれにリンクします。
  - 時刻が食い違う場合は、ワークスペース全体の証拠ともっとも整合的な読みを優先し、
    代わりの候補は「conflicting_time_hypothesis」として残します。

- 新しい場所を既存の空間エンティティと照合します。
  - 「Metropolitan Museum of Art」と「the museum」のように明らかに同じ場所なら統合します。
  - 暗に示される階層（部屋→建物→都市など）があれば階層構造として保持します。

- イベントやアクターの状態を適切な時間・場所アンカーに結び付け、
  全体として矛盾のないイベント系列になるように更新します。

タスク3: イベント・状態・関係の更新
新たな情報を反映するように、ワークスペースレベルのイベント・状態・関係を更新します。

- 各イベントについて
  - 既存のイベントの別記・詳細か、新規イベントかを判断します。
  - 同じ出来事の追加情報であれば、既存イベントにマージし、event_id は維持します。

- 各アクターの状態について
  - 過去の状態を書き換えるのではなく、状態のタイムラインに新しい状態を付け足します。
  - 同じ時点で以前の状態と真っ向から矛盾する場合は両方を残し、「state_conflict」として記録します。

- アクター・イベント・時間・場所の関係を更新し、ワークスペースが次を明示できるようにします。
  - 誰が・何を・いつ・どこで行ったか
  - その結果、各アクターの状態がどのように変化したか

タスク4: クエリの照合と回答の更新
更新後のワークスペースを用いて、未回答クエリをできるだけ解決します。

- &lt;unanswered_queries&gt; の各クエリについて
  1) 更新済みワークスペースに、回答に十分な情報があるかを確認します。
  2) 十分な情報がある場合は、簡潔で事実ベースの回答を生成します。
  3) 部分的にしか分からない場合は、その範囲で回答し、まだ分からない点を明示します。
  4) 依然として回答不能な場合は、足りない情報を短く説明します。

- 回答を作るときは必ず
  - ワークスペース内のエンティティ（ID や名前）に結び付けて考えること
  - 矛盾のない証拠に基づいて答えること
  - タイムラインや場所の制約を尊重すること

--------------------
出力フォーマット
--------------------

次のトップレベルキーを持つ JSON オブジェクトを返してください。

{
  "updated_workspace": {
    "actors": [...],
    "events": [...],
    "states": [...],
    "spacetime": [...],
    "relations": [...],
    "notes": [...]
  },
  "entity_alignment": [
    {
      "new_actor_id": "&lt;new_operator_maps 内の ID&gt;",
      "workspace_actor_id": "&lt;current_workspace 内の ID または null&gt;",
      "status": "merged | new | ambiguous",
      "comment": "&lt;短い説明&gt;"
    },
    ...
  ],
  "resolved_queries": [
    {
      "query_id": "&lt;id&gt;",
      "status": "answered | partially_answered",
      "answer": "&lt;短い自然文の回答&gt;",
      "support": {
        "actors": ["&lt;actor_id&gt;", ...],
        "events": ["&lt;event_id&gt;", ...],
        "spacetime": ["&lt;time_or_place_id&gt;", ...]
      }
    },
    ...
  ],
  "unresolved_queries": [
    {
      "query_id": "&lt;id&gt;",
      "status": "unanswered | contradictory | insufficient_information",
      "reason": "&lt;不足または矛盾の内容を短く説明&gt;"
    },
    ...
  ]
}

必ず JSON が構文的に正しく、クエリ部で参照する ID がすべて updated_workspace 内の要素に対応するようにしてください。
```

### エンティティごとに要約を作り、質問に素早く答える

質問に答えるときは、まず質問文から人名・組織名・場所名などの固有表現を取り出します。次に、それらを意味ネットワーク内の対応するエンティティと結びつけます。

マッチしたエンティティごとに、過去の状況をまとめたエピソード要約を生成します。このとき使用するプロンプト例は以下です。

```
User Prompt:
You are an expert narrative summarizer. Your task is to create a concise, chronological summary paragraph about a single entity based on structured information extracted from a text. Focus on creating a coherent story of the entity's involvement and changes based *only* on the provided timeline.

INSTRUCTIONS:
1. Write a single paragraph summarizing the key roles, states, experiences, and actions of the entity.
2. Follow the chronological order presented by the Chunk IDs.
3. Integrate the roles, states, and actions into a coherent narrative. Mention key interactions with other entities or objects when provided in the context.
4. You will be provided with spatial and temporal context for entity.
5. These will be provided in the form of a timeline of how they were captured in the text, be sure to incorporate all this spatial and temporal information particularly, provide importance to specific information (like name of place/ explicit dates etc.).
6. Focus on what entity did, what roles they held, their state of being, where they were located, when events happened, and significant events they participated in.
5. Keep the summary concise and factual according to the input. Do not add outside information or make assumptions.
6. Output *only* the summary paragraph, with no preamble or markdown formatting.

Inputs:
Input Entity: "Entity with role/state information and space/time links as well as questions answered by it."
```

日本語訳

```
ユーザープロンプト:
あなたは物語の要約に長けたアシスタントです。あなたのタスクは、テキストから抽出された構造化情報にもとづいて、1つのエンティティについての簡潔で時系列に沿った要約段落を作成することです。与えられたタイムラインだけを使って、そのエンティティがどのように関わり、どのように変化したかを、一貫した物語としてまとめてください。

指示:
1. エンティティの主要な役割・状態・経験・行動を、1つの段落にまとめて要約してください。
2. チャンクIDで示される時系列の順序に従ってください。
3. 役割・状態・行動を統合し、まとまりのある物語として書いてください。コンテキストに他のエンティティや物体との重要な関わりが示されている場合は、それも触れてください。
4. エンティティには空間的・時間的な文脈も与えられます。
5. それらはテキスト内でどのように記録されているかを示すタイムラインの形で与えられます。この空間的・時間的な情報はすべて要約に取り入れてください。とくに、場所の名称や具体的な日付などの情報を重視してください。
6. エンティティが何をしたか、どのような役割を担ったか、どのような状態だったか、どこにいたか、いつ出来事が起きたか、どのような重要な出来事に参加したかに焦点を当ててください。
5. 要約は入力にもとづいて簡潔かつ事実ベースにしてください。外部の情報を付け足したり、推測で補ったりしてはいけません。
6. 出力は要約の段落だけを返してください。前置きやマークダウン形式の装飾は付けないでください。

入力:
Input Entity: 「役割・状態の情報と、空間・時間のリンク、およびそのエンティティが答えた質問に関する情報を含むエンティティ」
```

要約は関連度にもとづいて並べ替えられ、上位のものだけがLLMに渡され、最終的な回答が作られます。このとき使用するプロンプトについては以下が例です。

```
User Prompt:
You are a question answering agent that only uses provided information to answer questions. Your task is to answer questions based exclusively on the knowledge graph information provided. Do not use any external knowledge.

The information provided is extracted from a Generative Semantic Workspace (GSW) representation, which captures:
- Entities: People, places, objects, and concepts
- Verb Phrases: Actions or events involving the entities
- Spatial Relationships: Locations of entities
- Temporal Relationships: Time periods of entities

We use the GSW to extract entity summaries, and you will be provided with these summaries along with graph structure for the GSW for each relevant chapter in order to answer the question. Always ground your answer in the provided information, and only provide answers for which there is clear evidence in the information provided. If the information needed is not available, state that you cannot answer based on the available information.

Please answer the following question using ONLY the information provided in the knowledge base extract below. First determine which chapters are most likely to contain relevant information based on the question, then based on the entity summaries and the graph structure for those chapters, determine the most likely answer. Answers will always be a SINGLE entity representing a person, event, location or time period. It will not be a description or a concept.

QUESTION: questions
KNOWLEDGE BASE INFORMATION: gsw summaries

First provide a reasoning for which chapters are most likely to contain relevant information based on the question. Then provide a reasoning for which entity is most likely to be the correct answer based on the entity summaries and the graph structure for those chapters.

Inputs:
Question: "Question to be answered"
GSW Summaries: "Summaries produced by the GSW relevant to answer questions"
```

日本語訳

```
ユーザープロンプト:
あなたは、与えられた情報だけを使って質問に答えるエージェントです。あなたのタスクは、与えられたナレッジグラフの情報にもとづいて、質問に回答することです。外部の知識は一切使ってはいけません。

入力として与えられる情報は、Generative Semantic Workspace（GSW）表現から抽出されたものです。GSW は次のような情報を表現します。
- Entities: 人物・場所・物体・概念などのエンティティ
- Verb Phrases: エンティティが関わる行動や出来事
- Spatial Relationships: エンティティの位置関係
- Temporal Relationships: エンティティが関わる時間的な範囲

GSW からはエンティティごとの要約が抽出されます。質問に答えるために、関連する各チャプターについて、これらの要約と GSW のグラフ構造が与えられます。必ず提供された情報にもとづいて回答し、その情報の中に明確な根拠がある場合にのみ答えてください。必要な情報が見つからない場合は、「利用可能な情報にもとづいては答えられない」と明示してください。

以下のナレッジベース抜粋だけを使って、質問に答えてください。まず、質問文にもとづいて、どのチャプターが関連情報を含んでいそうかを判断してください。その上で、それらのチャプターのエンティティ要約とグラフ構造にもとづいて、もっともありそうな答えを決めてください。答えは常に1つのエンティティであり、人・出来事・場所・時間のいずれかを表します。説明文や抽象的な概念そのものを答えにしてはいけません。

QUESTION: questions
KNOWLEDGE BASE INFORMATION: gsw summaries

まず、質問にもとづいて、どのチャプターが関連情報を含んでいる可能性が高いか、その理由を述べてください。次に、そのチャプターに対するエンティティ要約とグラフ構造にもとづいて、どのエンティティが正解としてもっともふさわしいか、その理由を述べてください。

入力:
Question: 「回答すべき質問文」
GSW Summaries: 「GSW が生成した、質問への回答に関連する要約」
```

ここで重要なのは、丸ごとのチャンクや文書を渡すのではなく、エンティティに焦点を当てた要約を渡す点です。そのおかげで、LLMに渡す情報量をしぼりつつ、効率的でブレの少ない回答を出しやすくなります。

手法の全体の流れを示したイラストを下に掲載します。

![[LLMにエピソード記憶のような能力を持たせるRAGのテクニック - AIDB/AIDB_97785_1-1024x520.png]]

## 実験の概要

### EpBenchで時間や場所の流れをどこまで追えるかを調べる

本手法の性能を確かめるために、研究チームは[Episodic Memory Benchmark（EpBench）](https://github.com/ahstat/episodic-memory-benchmark)というベンチマークを使いました。EpBenchは、LLMがエピソード記憶をどれだけ思い出せるか、そして長い物語をどれだけ筋を追って考えられるかを測るために作られたデータセットです。

一般的な質問応答ベンチマークは、単発の事実を探して答える力に焦点が当たりがちです。これに対してEpBenchは、「いつ・どこで・誰が」という手がかりに結びついた出来事を覚えておき、同じ人物が関わる似た出来事をきちんと区別できるか、というエピソード記憶のコアな能力を見るように設計されています。

EpBenchの文書は、合成的に作られた「本」という形になっています。各章は、日付・場所・登場人物などを指定したイベントテンプレートから生成されます。同じ時間・場所・アクター（これらをまとめて「手がかり（cues）」と呼びます）が、複数の章にまたがって何度も登場するようになっており、そのため曖昧さを解消しながら時間の流れを追う必要があります。

実験では、標準サイズの200章版と、その10倍のスケールである2000章版の両方を使いました。200章版では、テキスト全体で約10万トークン、質問数は686件です。質問は「手がかりの数」で分類されており、0個から6個以上まで幅があります。また、1つの質問に答えるために、最大で17章分の情報をまたいで参照しなければならないケースも含まれています。

### LLMに採点させて回答の正しさを測る

モデルの評価には「LLM-as-a-Judge」と呼ばれる方法を使っています。これは、LLMを判定役として使うやり方です。モデルの回答は、正解より長かったり、言い回しが違ったりすることがあります。そこで、EpBenchの著者が決めた手順に従い、まずLLMに回答から必要な情報だけを抜き出させます。そのうえで、その情報と正解を比べて、精度（Precision）、再現率（Recall）、F1スコアを計算します。

### GraphRAGやHippoRAG2などの既存手法と同じ条件で比べる

比較対象は、外部記憶を使わない通常のLLM、標準的な埋め込みベースRAG、そしてGraphRAG・HippoRAG2・LightRAGといった構造化RAGです。  
埋め込みベースRAGには、検索ベンチマークで高性能とされるVoyage-03という埋め込みモデルを使いました。各手法のハイパーパラメータは、公式実装のデフォルト設定に従っています。

公平に比べるため、すべての手法で条件をそろえました。1つの質問につき、最大17章ぶんのコンテキストを使えるようにし（これはデータセット内で必要となる最大の章数です）、回答を生成するモデルもすべてGPT-4oで統一しました。

### GPT-4oに指示を出してOperatorとReconcilerを動かす

今回の実験においては、OperatorとReconcilerは、GPT-4oにタスク専用の指示を与えるかたちで実装されました。動作を安定させるため、温度パラメータは0に固定されています。

## 既存の手法より安定して高い性能を示した

### F1スコア0.85で最高性能、難しい質問で再現率が約20ポイント高い

EpBench-200データセットでの各手法の比較結果をまとめます。

指標は精度（どれだけ間違えずに答えたか）、再現率（本来の正解をどれだけ拾えたか）、それらをまとめたF1スコアです。

|               Method               | Precision (P) |  Recall (R)   | F1-Score (F1) |
|------------------------------------|---------------|---------------|---------------|
|            Vanilla LLM             | 0.766 ± 0.010 | 0.616 ± 0.011 | 0.629 ± 0.010 |
|           Embedding RAG            | 0.832 ± 0.012 | 0.807 ± 0.012 | 0.771 ± 0.013 |
|    GraphRAG (Edge et al. 2025)     | 0.781 ± 0.013 | 0.748 ± 0.014 | 0.714 ± 0.013 |
| HippoRAG2 (Gutiérrez et al. 2025b) | 0.812 ± 0.013 | 0.787 ± 0.013 | 0.753 ± 0.013 |
|     LightRAG (Guo et al. 2025)     | 0.763 ± 0.014 | 0.699 ± 0.015 | 0.678 ± 0.014 |
|             GSW (Ours)             | 0.865 ± 0.010 | 0.894 ± 0.009 | 0.850 ± 0.010 |

本手法（GSW）はF1スコア0.850で全体トップでした。精度と再現率もどちらも最も高く、次点の手法より1割以上良い結果です。手がかりの数ごとに見ても、ほとんどのケースで1位、残りも2位でした。

再現率は「正しい章や場面をどれだけちゃんと拾えたか」を見る指標です。ほかの手法は手がかりが増えると再現率が落ちますが、本手法は高い水準を保っています。外部記憶なしの通常LLMはF1スコア0.642と最も低く、このタスクには専用の記憶フレームワークが必要だとわかります。

### 章数10倍の2000章データでも15%以上の優位性を維持

コーパスが10倍の EpBench-2000 でも実験されました。本手法のF1スコアは0.773で、最も強かったベースライン（埋め込みベースRAG）より約15%、他の構造化RAGよりは約22%高い値でした。

|    Method     |   Precision   |    Recall     |      F1       |
|---------------|---------------|---------------|---------------|
| Embedding RAG | 0.827 ± 0.014 | 0.688 ± 0.015 | 0.675 ± 0.015 |
|   GraphRAG    | 0.761 ± 0.017 | 0.548 ± 0.017 | 0.544 ± 0.017 |
|   HippoRAG2   | 0.759 ± 0.016 | 0.648 ± 0.016 | 0.635 ± 0.015 |
|   LightRAG    | 0.649 ± 0.018 | 0.497 ± 0.017 | 0.494 ± 0.016 |
|  GSW (Ours)   | 0.830 ± 0.010 | 0.796 ± 0.009 | 0.773 ± 0.009 |

つまり、本手法はスケールが大きくなっても、高い再現率と推論性能を維持できそうであると分かりました。

### コンテキストトークンを約51%削減しつつ精度も確保

性能面だけでなく、トークンの使い方でも効率的です。実験結果を見ると、1質問あたりの平均コンテキストは約3,587トークンで、GraphRAGより約51%、埋め込みベースRAGやHippoRAG2より約59%少なくなっています。

|               Method               | Avg. Tokens | Avg. Cost |
|------------------------------------|-------------|-----------|
|            Vanilla LLM             |  ∼101,120   | ∼$0.2528  |
|           Embedding RAG            |   ∼8,771    | ∼$0.0219  |
|    GraphRAG (Edge et al. 2025)     |   ∼7,340    | ∼$0.0184  |
| HippoRAG2 (Gutiérrez et al. 2025b) |   ∼8,771    | ∼$0.0219  |
|     LightRAG (Guo et al. 2025)     |   ∼40,476   | ∼$0.1012  |
|             GSW (Ours)             |   ∼3,587    | ∼$0.0090  |

理由は、章全体を渡さず、意味構造にもとづいた「エンティティ別の要約」だけをLLMに渡しているためです。質問に関係する情報だけを絞ることで、コストを抑えつつ、事実と異なる出力も減らしています。

## まとめ

本記事では、人間のようなエピソード記憶をLLMに持たせるためのフレームワークを紹介しました。仕組みは、テキストから意味的な要素を抜き出す「Operator」と、それらをつなぎ合わせて一貫した記憶を作る「Reconciler」という2つのコアコンポーネントから成り立っています。

脳の記憶のしくみを参考にした設計になっており、登場人物や組織などのアクターが「いつ・どこで・どんな状態だったか」「どう変化したか」を、時間と場所に結びつけて辿る点が特徴です。

EpBenchという専用ベンチマークでの評価では、既存手法よりも高い精度を示しました。それに加えて、LLMに渡すトークン数を約半分まで減らし、推論コストも抑えられることが示されています。とくに、複数の文書や章にまたがるような複雑な質問に対して、強みがはっきり現れていました。

一方で、現時点ではGPT-4oのようなクローズドソースの性能の高いLLMに依存していることや、テキスト以外のデータ形式にはまだ対応していないことが今後の課題として挙げられます。それでも、ビジネス文書や報告書のような「まとまりのある長文」を扱う場面では、LLMの記憶能力を大きく伸ばせる有望なアプローチと言えそうです。

**本記事の関連研究**

-   [RAGで取得すべき情報はLLMごとの「データの有用性」で異なる](https://ai-data-base.com/archives/96511)
-   [LLM自体の性能が飛躍的に向上した今、RAGに求められることとは](https://ai-data-base.com/archives/96364)
-   [RAGの実用性レベルを上げるために「データソースを構造化する」という考え方](https://ai-data-base.com/archives/96111)

Copyright © Parks, Inc. All rights reserved.
