---
created: 2026-01-01T11:16:40 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/97730
author: AIDB Research
---

# LLMでユースケース図の作成時間を大幅に短縮 3つのプロンプト技術を組み合わせ - AIDB

> ## Excerpt
> 本記事では、LLMを使ってユースケース図の作成を効率化する方法を紹介します。 ユースケース図は、ソフトウェア開発の初期段階で役に立つ図ですが、時間や専門知識が必要です。そのため、現場では作成が後回しになったり、省略されたりすることもあります。そこで、LLMによる支援が注目されています。 本記事で取り上げる研究では、3つのプロンプト技術を組み合わせています。実験の結果、モデリング時間は平均で約60%…

---
本記事では、LLMを使ってユースケース図の作成を効率化する方法を紹介します。

ユースケース図は、ソフトウェア開発の初期段階で役に立つ図ですが、時間や専門知識が必要です。そのため、現場では作成が後回しになったり、省略されたりすることもあります。そこで、LLMによる支援が注目されています。

本記事で取り上げる研究では、3つのプロンプト技術を組み合わせています。実験の結果、モデリング時間は平均で約60%短くなり、モデルの品質は手動で作成した場合とほぼ同じ水準でした。

手法とその結果を順に紹介します。

![[LLMでユースケース図の作成時間を大幅に短縮 3つのプロンプト技術を組み合わせ - AIDB/AIDB_97730-1024x576.png]]

**本記事の関連研究**

-   [要件定義前のインタビュー、LLMがどれほど役立つか？プロンプトの工夫と評価結果](https://ai-data-base.com/archives/93122)
-   [LLM時代のソフトウェア開発者が考える「要件からコード生成」の実践ポイント](https://ai-data-base.com/archives/92435)
-   [要件定義に役立つLLMプロンプトのガイドラインを整理](https://ai-data-base.com/archives/92204)

## 背景

ソフトウェア開発の初期段階では、「このシステムで誰が何をできるのか」をはっきりさせることが重要です。

そのための代表的な手法が、システムを使う人（アクター）と、その人たちの目的（ユースケース）を図で整理するユースケースモデリングです。ユースケース図は、完成後のシステムを理解するときにも役立ちます。保守担当者は「この機能は誰のためで、何のためか」を把握しやすくなり、テスト設計やシステム範囲の整理にも使えます。

一方で、実務ではユースケース図の作成が省略されることも多いです。要件を深く理解し、モデリング技術も身につける必要があり、時間と労力の負担が大きいからです。納期や市場投入のプレッシャーの中で、丁寧なモデリングに十分な時間を取りにくい状況があります。

ここで期待されているのがLLMです。近い事例として、LLMがソフトウェア要件からシステム設計を半自動で生成できる可能性が示されています。その中間ステップとしてユースケースモデルを作ることの重要性や、LLMにUML図を生成させる試みも報告されています。

ただし、ユースケース図の作成にLLMをどう組み込むかという具体的なプロセスやツールは十分に整理されていません。効率化の度合いを数値で評価した事例や、実際の開発者の受け止め方を丁寧に調べた研究も多くはありません。

そこで本記事では、テキストで書かれたソフトウェア要件からユースケース図を生成するプロンプトテンプレートと、その有効性を実務に近い形で検証した事例を取り上げます。

ここから限定コンテンツ

### **忙しい人向けに、重要なポイント5選**

1.  LLM支援でユースケース図の作成時間が平均60%短縮され、統計的にも有意な効果が確認された
2.  ロールプロンプティング、知識注入、ネガティブプロンプティングという3つのプロンプト技術を組み合わせることで、半自動かつ高品質な生成を実現
3.  生成されたモデルの品質は手動作成と同等レベルを維持し、参加者全員が「専門外の人でも使える」と評価した
4.  ワークフローに中間チェックポイントを設け、ユーザーが各段階で結果を確認・修正できる設計が効率化と品質維持の両立につながった
5.  要件が反復的に進化する実務環境への対応や、生成結果と要件のトレーサビリティ機能など、今後の改善余地も明らかになった

**参照文献情報**

-   タイトル：Leveraging Large Language Models for Use Case Model Generation from Software Requirements
-   URL：[https://doi.org/10.48550/arXiv.2511.09231](https://doi.org/10.48550/arXiv.2511.09231)
-   著者：Tobias Eisenreich, Nicholas Friedlaender, Stefan Wagner
-   所属：Technical University of Munich

研究チームは、Llama 3.1 70BというオープンウェイトのLLMを中核に使っています。このLLMに対して、プロンプトエンジニアリングと呼ばれる「指示文の工夫」で精度を高めています。

組み込まれている技術は3つです。

|      技術名      |        役割・ねらい         |                     具体例                     |
|---------------|-----------------------|---------------------------------------------|
|  ロールプロンプティング  | LLMに「どういう立場で答えるか」を伝える |         「ソフトウェア工学の専門家として振る舞ってください」          |
|     知識注入      |    事前に必要な知識を教えておく     |          PlantUMLの文法ルールを詳しく説明しておく           |
| ネガティブプロンプティング |   やってほしくない出力を明示して防ぐ   | 「存在しない要素を追加しない」「このパターンの誤りは出さないでください」などを指示する |

流れは下記の通りです。

1.  要件文書からアクターをすべて抜き出します。
2.  それぞれのアクターに関係するユースケースだけを抽出します。
3.  その結果をもとに最終的なユースケース図を生成します。
4.  最後に、ユーザーが結果を確認し、必要ならその場で修正します。

### Step1　アクター抽出

```
SYSTEM:
You are a software architect.
Extract all actors involved in the use case from the provided software requirements.

Constraints:
- Return only the list of actor names, separated by commas.
- Do not add any explanations, introductions, or trailing punctuation.
- Use a consistent naming style (e.g., Title Case in English).

USER:
Here are the requirements:

{requirements_text}

List the actors.
```

日本語版

```
SYSTEM:
あなたはソフトウェアアーキテクトです。
以下の日本語の要件定義から、ユースケース図に登場する「アクター」をすべて抽出してください。

制約:
- アクター名だけをカンマ区切りで出力してください。
- 説明や前置きの文章は書かないでください。
- 句読点（。や、）はアクター名の中に必要な場合だけ使い、末尾には付けないでください。

USER:
要件:
{requirements_text}

アクターを列挙してください。
```

### Step2　アクターごとのユースケース抽出

```
SYSTEM:
You are a software architect.
From the provided software requirements and the given list of actors,
identify the most important use cases for each actor.

Output format (exactly):
actor1: usecase1, usecase2;
actor2: usecase1, usecase2;
...

Constraints:
- Do not add explanations or extra text.
- Use only plain text in the format above.

USER:
Requirements:
{requirements_text}

Actors:
{actor_list}

Provide the use cases per actor in the specified format.
```

日本語版↓

```
SYSTEM:
あなたはソフトウェアアーキテクトです。
与えられた日本語の要件定義とアクターの一覧から、
各アクターにとって重要なユースケースを抽出してください。

出力形式（厳守してください）:
actor1: usecase1, usecase2;
actor2: usecase1, usecase2;
...

制約:
- 上記の形式だけを出力してください（説明文や前置きは書かないでください）。
- actor名には、入力で与えられたアクター名をそのまま使ってください。
- usecaseは動作が分かる短いフレーズで書いてください（例: "注文を登録する"）。
- セミコロン (;) の後には半角スペースを1つ入れてください。
- 最後の行の末尾にもセミコロン (;) を付けてください。

USER:
要件:
{requirements_text}

アクター一覧:
{actor_list}  # 例: "顧客, 店員, 管理者"

各アクターごとのユースケースを、指定された形式で出力してください。
```

### Step3　UseCase図＋記述生成

**PlantUMLのユースケース図生成**

```
SYSTEM:
You are a software architect.
Create a Use Case Diagram in PlantUML from the given list of actors and use cases.
Use the following diagram only as notation guidance:

@startuml
left to right direction
skinparam packageStyle rect
skinparam shadowing false

actor Administrator as administrator
actor :Mail-Server: as mail

rectangle MitgliedHinzufügen {
  (Formular anzeigen) as anzeigen
  (Informationen ausfüllen) as ausfüllen
  (Erstellung bestätigen) as bestätigen
  (Mail senden) as senden

  administrator --&gt; anzeigen
  administrator --&gt; ausfüllen
  administrator --&gt; bestätigen
  mail --&gt; senden

  bestätigen .&gt; senden : includes
}
@enduml

Constraints:
- Only output PlantUML code.
- Model only the actors and use cases from the input.
- The name of the rectangle (system) cannot include spaces.
- Use Case names can only include letters and numbers.
- All Use Cases must be placed inside the system rectangle.

USER:
Actors and use cases:
{actors_and_usecases}

Please output only the PlantUML code.
```

日本語版↓

```
SYSTEM:
あなたはソフトウェアアーキテクトです。
与えられたアクターとユースケースの一覧から、Use Case 図の PlantUML コードを生成してください。

次の例は記法の参考としてだけ使ってください。内容はまねする必要はありません。

@startuml
left to right direction
skinparam packageStyle rect
skinparam shadowing false

actor Administrator as administrator
actor :Mail-Server: as mail

rectangle MitgliedHinzufügen {
  (Formular anzeigen) as anzeigen
  (Informationen ausfüllen) as ausfüllen
  (Erstellung bestätigen) as bestätigen
  (Mail senden) as senden

  administrator --&gt; anzeigen
  administrator --&gt; ausfüllen
  administrator --&gt; bestätigen
  mail --&gt; senden

  bestätigen .&gt; senden : includes
}
@enduml

制約:
- 出力は PlantUML のコードだけにしてください（説明文は一切書かないでください）。
- 入力で与えられたアクターとユースケースだけをモデル化してください。
- システムを表す rectangle の名前にはスペースを含めないでください（例: "OrderingSystem"）。
- Use Case 名は半角の英字と数字のみを使ってください（スペースや記号は使わないでください）。
- すべての Use Case を rectangle の中に配置してください。

USER:
アクターとユースケース:
{actors_and_usecases}
# 例:
# 顧客: 注文を登録する, 注文履歴を確認する;
# 店員: 注文を確認する;

上記をもとに、Use Case 図の PlantUML コードだけを出力してください。
```

**Use Case記述のJSON文字列生成**

```
SYSTEM:
You are a software architect.
Create one Use Case Description for each use case.

Each description must have:
- title
- description
- actors (array of strings)
- mainFlow (array of strings)

Output format:
- Return a JSON array as a single string.
- Add "jsonStart" at the beginning and "jsonEnd" at the end of the string.

Example:
jsonStart[
  {
    "title": "verbNoun1",
    "description": "Description of the first use case.",
    "actors": ["Actor1", "Actor2"],
    "mainFlow": ["Step1", "Step2"]
  }
]jsonEnd

USER:
Actors and use cases:
{actors_and_usecases}

Provide the JSON string as specified.
```

日本語版↓

```
SYSTEM:
あなたはソフトウェアアーキテクトです。
与えられたアクターとユースケースから、各ユースケースの説明を作成してください。

各ユースケースについて、次の項目を含めてください:
- title: ユースケース名（動詞＋名詞の形、例: "登録注文" など）
- description: ユースケースの概要説明（1〜2文）
- actors: 関係するアクター名の配列
- mainFlow: 想定される主な処理の流れをステップごとの配列

出力形式:
- JSON 配列を1つの文字列として返してください。
- 文字列の先頭に "jsonStart"、末尾に "jsonEnd" を必ず付けてください。

例:
jsonStart[
  {
    "title": "verbNoun1",
    "description": "Description of the first use case.",
    "actors": ["Actor1", "Actor2"],
    "mainFlow": ["Step1", "Step2"]
  }
]jsonEnd

制約:
- 有効な JSON になるように記述してください（キーや文字列はダブルクォートで囲んでください）。
- 説明文は日本語で書いてください。
- 例のテキストはそのままコピーせず、与えられたユースケースに合わせて書き直してください。
- "jsonStart" と "jsonEnd" という文字列を忘れないでください。

USER:
アクターとユースケース:
{actors_and_usecases}

上記のユースケースについて、指定された形式の JSON 文字列を出力してください。
```

### ステップ４　改善

```
SYSTEM:
You are a software architect.
You will receive:
- PlantUML code for a Use Case diagram
- Use Case Descriptions in JSON format
- A refinement instruction

Apply the refinement to both the PlantUML and the Use Case Descriptions.
Use the following diagram only as notation guidance:

@startuml
left to right direction
skinparam packageStyle rect
skinparam shadowing false

actor Administrator as administrator
actor :Mail-Server: as mail

rectangle MitgliedHinzufügen {
  (Formular anzeigen) as anzeigen
  (Informationen ausfüllen) as ausfüllen
  (Erstellung bestätigen) as bestätigen
  (Mail senden) as senden

  administrator --&gt; anzeigen
  administrator --&gt; ausfüllen
  administrator --&gt; bestätigen
  mail --&gt; senden

  bestätigen .&gt; senden : includes
}
@enduml

Constraints:
- Output the refined PlantUML code.
- Then output the refined JSON string.
- Do not add explanations or comments.

USER:
Original PlantUML:
{plantuml_code}

Original Use Case Descriptions (JSON string):
{usecase_json}

Refinement instruction:
{refinement_instruction}

Return the refined PlantUML and JSON.
```

日本語版↓

```
SYSTEM:
あなたはソフトウェアアーキテクトです。
次の3つの情報を受け取ります。
1. Use Case 図の PlantUML コード
2. ユースケース記述の JSON 文字列
3. 修正指示（refinement instruction）

修正指示にしたがって、PlantUML コードとユースケース記述の両方を更新してください。

次の Use Case 図は記法の参考としてだけ使ってください。内容はまねする必要はありません。

@startuml
left to right direction
skinparam packageStyle rect
skinparam shadowing false

actor Administrator as administrator
actor :Mail-Server: as mail

rectangle MitgliedHinzufügen {
  (Formular anzeigen) as anzeigen
  (Informationen ausfüllen) as ausfüllen
  (Erstellung bestätigen) as bestätigen
  (Mail senden) as senden

  administrator --&gt; anzeigen
  administrator --&gt; ausfüllen
  administrator --&gt; bestätigen
  mail --&gt; senden

  bestätigen .&gt; senden : includes
}
@enduml

制約:
- 最初に修正済みの PlantUML コードを出力してください。
- そのあとに、修正済みの JSON 文字列を出力してください。
- 説明やコメントは書かないでください（コードと JSON のみを返してください）。

USER:
元の PlantUML コード:
{plantuml_code}

元のユースケース記述（JSON文字列）:
{usecase_json}

修正指示:
{refinement_instruction}

修正済みの PlantUML コードと JSON 文字列を、指定された順番で返してください。
```

ツールのコードやプロンプト、実験に使った要件文書は、[こちら](https://github.com/nicholasfriedlaender/requirements2usecase)で内容を確認できます。

上記に示したプロンプト例は、Githubに示されているプロンプトをわかりやすく書き換えたものです。

## 実験の流れ

### 実務経験7年の開発者5名が手動作業とLLM支援をどちらも試す

研究では、LLM支援が「どれくらい役に立つのか」を数字と開発者の声の両方から見ました。

数字としては、モデリングにかかった時間や、できあがったモデルの正確さを扱います。また、開発者の声としては、使ってみた感想や気づきを集めました。

両方をそろえることで、「速くなったかどうか」だけでなく、「なぜそう感じたのか」まで追いかけるねらいがあります。

実験のしかたとしては、同じ参加者に「手動だけでモデリングする場合」と「LLM支援を使う場合」の両方をやってもらいました。人ごとの得意・不得意の差を小さくできるので、条件どうしの違いを比べやすくなります。参加者は専門ネットワークから募集し、平均7年のソフトウェア開発経験を持つエンジニア5名に協力してもらいました。

まず定量データとして、手動とLLM支援のそれぞれについて、モデリング時間とモデルの品質を測りました。要件文書は、長さや難しさが近いものを2つ用意し、どちらの文書をどの条件で使うかを参加者ごとに入れ替えています。こうすることで、文書の違いが結果にあまり影響しないようにしました。

さらに定性データとして、半構造化インタビューというかたちで話を聞きました。あらかじめ質問の軸は用意しておきつつ、会話の流れに合わせて気になった点を深掘りしていく方法です。これによって、事前には想定していなかった気づきや、参加者の率直な感想を引き出すことを目指しました。

### 約50分の作業時間で従来手法とLLM支援を順番に比べる

|   フェーズ名    |                         主な作業内容                         |              ねらい              |
|------------|--------------------------------------------------------|-------------------------------|
|   導入フェーズ   |            研究の目的を説明し、例題でユースケースモデリングを練習してもらう            |      参加者が手法に慣れているかを確認する       |
|  ベースライン演習  | 2つの要件文書のうち1つで、手動でユースケース図を作成し、その中から2つのユースケースを選んで詳細説明を書く |  従来の手動作業の時間と成果物をベースラインとして取る   |
|  LLM支援演習   |           残りの要件文書を使い、開発したツールでユースケースモデルを作成する            |     LLM支援時の作業内容と成果物を取得する      |
| インタビューフェーズ |         ツールの印象、使いやすさ、有用性、結果の品質・信頼感、課題や改善点を聞き取る         | 開発者の生の声からLLM支援ツールの評価や改善点を把握する |

### モデリング時間と図の品質を統計的に確かめる

まず、数値で比べられる指標として、手動とLLM支援それぞれのモデリング時間を記録しました。時間制限は設けず、参加者が「これでよい」と思うところまで作業してもらい、要件文書を最初に読む時間だけは除外しています。読む速さの個人差を避け、純粋なモデリング時間だけを比べるためです。

あわせて、インタビューの音声を録音し、あとから文字起こしして定性データとして扱いました。

モデルの品質は、研究チームが手動で作成した正解モデル（グラウンドトゥルース）と、参加者が作ったモデルを見比べて評価しました。対象は、ユースケースモデルの土台となるアクターとユースケースに絞っています。関係性の細かな表現は文脈に左右されやすく、ユースケースの詳細説明も客観的に点数化しにくいため、今回のスコアには含めていません。

## 実験結果

### モデリングにかかる時間はおよそ6割短くなった

実験では、LLM支援ツールを使ったときと手動で作成したときのユースケースモデルについて、5名の参加者それぞれの作成時間が計測されました。同じ要件文書を使い、全員が手動とLLM支援の両方でモデリングを行っています。

集計の結果、LLM支援を使うと手動に比べて作成時間が平均で約60%短くなっていました。実務でも体感できるレベルの効率化といえます。

一方で、参加者が5名と少ないにもかかわらず有意差が出たのは、効果が非常に大きかったためと考えられます。ただし、実験では必ず「手動 → LLM支援」という順番で作業しており、順序が固定されている点はデザイン上の制約です。そのため、結果の解釈には注意が必要だと研究チームは述べています。

モデルの品質についても、精度・再現率・F1スコアの3つで評価されています。精度は生成された要素のうち正しいものの割合、再現率は正解モデルの要素をどれだけ拾えたかの割合、F1スコアはそのバランスを示す指標です。

結果を見ると、LLM支援での精度は高く、生成されたユースケースのほとんどが妥当な内容でした。再現率は手動よりも高く、正解モデルに含まれる要素をより多く拾えていました。アクターについては、手動とLLM支援のどちらでも全て正しく識別されていました。

### 参加者全員が「役に立つ」と感じ 専門外の人でも使えると評価した

インタビューでは、参加者全員がツールを肯定的に評価しており、ソフトウェアエンジニアの作業負担を減らし、モデリングのスピードを大きく上げられると答えました。

とくに評価されたのは、ワークフローのつくり方です。LLMが最初に出した結果から、関係のない要素や誤りを削除できるようになっており、ユーザーがLLMの解釈を確認して手直しできます。ゼロから図を描くのではなく、生成されたモデルを出発点にして磨いていける点が、効率化につながっていました。

ある参加者は「ユースケース図は役に立つのに、実務では専門知識や時間が足りず、作られないことが多い」と述べました。別の参加者は、ツールがアプリケーションライフサイクル管理の場面で役立ち、要件工学の専門家でない人でも要件を設計したり、ユーザーとシステムのやり取りを整理したりできると評価していました。

### 自動生成したモデルの品質は手作業とほぼ同じだった

また、参加者はツールの性能をおおむね高く評価しており、とくに生成結果が要件文書の内容とよく合っている点を評価しました。

参加者は、ツールが自分たちの手作業とほぼ同じようなモデルを作ることに満足していました。生成されたモデルは要件の内容や意図とよく整合しており、そのうえでモデリングの流れ全体をユーザーがコントロールできていました。「生成されたユースケースは意味があった」「自分でもこういうモデルにしたと思う」といったコメントも出ています。

研究チームが作業の様子を観察すると、中間結果や最終結果を細かく調整する様子が繰り返し見られました。不要なアクターを削除したり、ユースケース名を編集したりして、出力を徐々に整えていたのです。こうした行動から、ツールがユーザーによる適切な手直しの余地を残していることが分かります。

### 要件を対話で詰められないことと 出力が毎回少し変わることが課題

懸念としては、実務で使うときの課題と、LLMの限界が挙げられました。

参加者は、ツールには「結果が要件と本当に合っているか」を確かめる力がないと指摘しました。現場では、関係者が対話を重ねて前提を問い直し、目的を整理していきますが、ツールはこの反復的なやり取りを支援していません。ある参加者は「前提を問い、理由を聞き、代替案を探るプロセスがワークフローにはない」と話しています。

また、ユーザーが結果をそのまま信じてしまうリスクも懸念されました。ツールは「要件がきれいに定義されている」ことを前提にしていますが、実際のプロジェクトではそうとは限りません。ある参加者は「より大きな要件文書でも動くかは、今後の検証が必要だ」と述べました。

技術面では、LLMの非決定性による結果のばらつきと、初回のユースケース説明があっさりしすぎている点が課題として挙がりました。非決定性とは、同じ入力でも毎回少し違う出力になる性質のことです。

### 要件とのひも付けやペルソナ自動生成などの機能があるとよい

改善提案としては、ワークフローや成果物の質、ユーザーの関わり方を高めるための具体的なアイデアが出ました。

いちばん多かったのは、トレーサビリティ機能の追加です。生成されたユースケースが要件文書のどの部分に対応するかをたどれるようにし、結果の確認と理解をしやすくする提案でした。

参加者は、透明性とカバレッジも重視しました。明示されたユースケースだけでなく、抜けていそうなものも候補として示し、その扱い理由を説明すべきだとしています。また、ビジネス上の指針も反映し、将来的にはユースケースからユーザーストーリーを自動生成できるとよいという意見もありました。

さらに、ペルソナ記述の自動生成も提案されました。デザイン思考などと組み合わせることで、ユーザーの参加を促し、より質の高い結果を得やすくなるという考え方です。

## まとめ

テキストで書かれたソフトウェア要件からユースケース図を生成する方法論、そして実務経験のある開発者5名による検証結果を取り上げました。

その結果、モデリングにかかる時間は平均で約60%短くなり、統計的な検定でも偶然とは言えない差が確認されました。また、生成されたモデルの品質は手動で作成した場合とほぼ同じ水準が保たれていました。参加者全員がツールを有用だと感じており、とくにリソースが限られたチームで役立ちそうだと評価しています。

一方で、要件が段階的に変化していく実務環境への対応や、より大きな要件文書での検証など、今後取り組むべき課題も明らかになりました。LLMがユースケースモデリングを支援する具体的な可能性を示せた一方で、実務で広く使うためには、さらなる検証と改良が必要だと言えます。

**本記事の関連研究**

-   [要件定義前のインタビュー、LLMがどれほど役立つか？プロンプトの工夫と評価結果](https://ai-data-base.com/archives/93122)
-   [LLM時代のソフトウェア開発者が考える「要件からコード生成」の実践ポイント](https://ai-data-base.com/archives/92435)
-   [要件定義に役立つLLMプロンプトのガイドラインを整理](https://ai-data-base.com/archives/92204)
