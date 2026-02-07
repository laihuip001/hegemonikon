---
created: 2026-01-01T11:15:06 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/90734
author: AIDB Research
---

# 個人の深い価値観にもとづく「その人らしい答え」をAIで再現する手法 - AIDB

> ## Excerpt
> 本記事では、個人の価値観や判断傾向をAIで再現するための手法を紹介します。 単なる情報の蓄積ではなく、認知・感情・行動の観点から構造的にその人らしい思考や行動を再現しようとするアプローチです。 途中で使用するプロンプトも含め説明していきます。 本記事の関連研究 背景 AIを使用する上で、「人らしさ」をどう取り入れるかは関心が強いテーマです。 とくに、ある「特定の人物の判断や価値観を引き継がせたい」…

---
本記事では、個人の価値観や判断傾向をAIで再現するための手法を紹介します。

単なる情報の蓄積ではなく、認知・感情・行動の観点から構造的にその人らしい思考や行動を再現しようとするアプローチです。

途中で使用するプロンプトも含め説明していきます。

![[個人の深い価値観にもとづく「その人らしい答え」をAIで再現する手法 - AIDB/AIDB_90734-1024x576.png]]

**本記事の関連研究**

-   [プロンプトによるLLM応答のパーソナライゼーション　仮説を活用して文体を調整](https://ai-data-base.com/archives/89384)
-   [現実における人間の多様性に対応したLLMペルソナ設計手法の検証](https://ai-data-base.com/archives/88247)
-   [個人の振る舞いや考え方を模倣するアバターをLLMで構築する方法](https://ai-data-base.com/archives/87179)

## 背景

AIを使用する上で、「人らしさ」をどう取り入れるかは関心が強いテーマです。

とくに、ある「特定の人物の判断や価値観を引き継がせたい」というニーズは、実務でも意外とよくあります。たとえば、社長や課長、あるいは研究室の教授など、日頃から多くの意思決定を行っている人ほど、「この人ならどう考えるか」を再現したいと思われることがあるかもしれません。

LLMの活用が広がるなかで、そうした人物らしさを模倣する方法がいくつか登場してきました。あらかじめ用意したペルソナ情報をもとにキャラクターのような振る舞いをさせたりといったアプローチです。

しかし、現実の人間の価値観はずっと複雑です。文化や人生経験、信念の違いによって、同じ問いに対してまったく違う答えが返ってくるのはよくあることです。そうした個人ごとの価値観の違いを、LLMでどこまで丁寧に再現できるか。それは、人間らしいふるまいを目指すうえで避けて通れない課題のひとつです。

こうした見方をもとに、”過去の経験や属性情報から個人のストーリーを生成し、それを手がかりに価値観を再現する”新しい手法が提案されました。

なお、以前紹介した[「少数の文例から文体や価値観を読み取り、プロンプトに反映する」タイプの手法](https://ai-data-base.com/archives/89384)は、出力スタイルの調整に強みがありました。

一方、今回の研究が扱うのは、そうしたスタイルではなく「価値判断そのもの」の再現です。たとえば、ある社会問題に対して賛成か反対か、どれくらい重視するか、といった反応の違いを、個人の背景に基づいて再現しようとしています。つまり、話し方だけでなく「何をどう考えるか」に踏み込んだシミュレーションが目的になっています。

以下で、プロンプトも含め詳しく紹介します。

ここから限定コンテンツ

## 「その人らしさ」をどう再現する？過去の工夫を振り返る

個人の価値観をLLMでどこまで再現できるのか。この問いに対して、これまでにもさまざまなアプローチが試みられてきました。方向性としては、大きく3つに分けることができます。

### AIに「らしさ」を覚えさせる工夫

まず注目されてきたのは、年齢や地域といった属性情報を活用する方法です。たとえば、ある年齢層の人々に特有の価値観や話し方をAIに再現させようとする手法が提案されてきました。

さらに一歩進んで、特定の個人に近い背景情報をもとに、仮想的な人物像（ペルソナ）を構成する研究もあります。その人物がどんな人生を送ってきたのかをストーリーとして与えることで、よりリアルな振る舞いを引き出そうという発想です。

こうした研究から見えてきたのは、”属性だけでは限界がある”ということです。人の考え方は、過去の発言や行動の積み重ねに強く影響されます。そのため、これまでどう答えてきたか、どんな価値判断をしてきたかという履歴が、再現性のカギになります。

最近では、AIに個人の好みを覚えさせたり、アプリの中でのやりとりを模倣させたりといった応用も見られます。ただ、こうした取り組みはまだ限られた状況での最適化が中心で、価値観そのものに焦点を当てたものは多くありません。

### 人の判断はどう動く？脳の仕組みからヒントを探る

人が何かを判断するとき、理屈だけで動いているわけではありません。考え、感じ、行動するという複数の要素が同時に働きながら、意思決定が行われています。

心理学では、このような複雑なプロセスをモデル化するために、認知や感情の反応、行動パターンが状況に応じて組み合わさる「システムとしてのパーソナリティ」の考え方が広く使われています。また、脳の中では複数の判断基準が競い合い、ときには調整されながら一つの結論にまとまっていくと考えられています。

LLMは人間の脳とは違いますが、複雑な推論や状況判断をある程度こなせるようになってきています。こうした心理学の知見を取り入れて、AIが人をまねるだけでなく、人のように考えるための枠組みが模索され始めています。

### 価値観データってどこまで使える？信念のちがいをどう測るか

では、人それぞれの価値観をどうやって定量的にとらえるか。このテーマにおいては、いくつかの国際調査や社会心理学的な枠組みで取り組まれてきた記録が残っています。

広く使われているのが、価値観に関する大規模な調査データ「世界価値観調査（WVS）」です。宗教、政治、経済、教育といった多様な分野にわたり、人々の考え方や態度の傾向を記録したこのデータは、世界中の研究者によって活用されてきました。

AIの文脈でも、こうしたデータを使って「国ごとの傾向」や「ある集団の価値観の平均」を再現する試みは行われています。ただし、個人の信念や判断の軸まで掘り下げて再現しようとした研究は多くありません。

## 提案手法の中身

以上の背景をふまえ、今回の研究では新しいアプローチが提案されています。

新アプローチの焦点は2つあります。

ひとつは、人の情報をどのようにまとめてモデルに渡すか。  
もうひとつは、人間の意思決定にある複雑な構造を、どうLLMの処理に取り込むかという点です。

仕組みとしては、大きく2段階に分かれています。まず、過去のアンケート回答を「その人のストーリー」として再構成する仕組み。次に、そのストーリーをもとに「認知」・「感情」・「行動」の観点から同時に分析を進める構成です。

![[個人の深い価値観にもとづく「その人らしい答え」をAIで再現する手法 - AIDB/AIDB_90734_1-1024x389.png]]

手法の全体像を図示したもの

### 何をもとに再現するか

価値観の再現を考えるとき、最初に必要になるのが、その人に関するある程度まとまった情報です。たとえば、以前に答えたアンケートや意識調査の履歴、あるいは過去の面談記録、行動ログ、パーソナルな傾向がわかるような質問応答の履歴などが使えます。自社サービス内のユーザーデータや、従業員へのヒアリング記録などがある場合も、それを土台にできます。

これらの情報を整理し、ひとつの「プロフィール」として扱っていきます。内容は、質問とその回答のセットで構成そ、たとえば

Q. 「政治への関心はありますか？」  
A. 「ある程度関心がある」

といったかたちです。効果を高めるには、1人あたり数百件ほどのQ&Aを用意することが推奨されますが、10～50件程度でも実験は可能です。

目指すのは、このプロフィールには含まれていない新しい問いに対して、その人がどう答えるかをLLMに予測させることです。つまり、すでに与えた情報をもとに、その人の考え方や価値観を読み取り、未知の質問にも一貫性のある回答を出させるのが目的です。

このとき注意したいのが、情報量と質のバランスです。多すぎるとモデルが混乱しやすく、少なすぎるとその人らしさをつかみにくくなります。判断に影響を与えそうな質問を中心に、分野を少しずつ広げていくと安定しやすくなります。

なお、応答の評価では、「どの選択肢を選ぶか」という正答率と、「どれくらいずれたか」という誤差の2つの観点を使います。たとえば「1〜10の中から幸福度を選んでください」といった質問で、8と予測して実際は6だった場合、その差をスコアとして扱う方法です。

### 情報をストーリーとして整理する

LLMにプロフィール情報を渡すとき、単純にQ&Aのリストをそのまま入力する方法では、期待通りの挙動にならないことがあります。数百件の回答をそのまま並べると、処理負荷が高くなるうえ、バラバラの情報から一貫した価値観を読み取るのが難しくなります。

必要な部分だけを抜き出すという方法もありますが、断片的すぎると、その人らしさが失われやすくなります。実際、情報を全件渡した場合と、一部に絞った場合の両方で、回答の一貫性が下がることが確認されています。

そのため、Q&Aの羅列を”ストーリー形式”に変換して渡すと効果的です。情報の意味や流れが整理されることで、モデルがその人の価値観や傾向をより自然にとらえやすくなります。

Q&Aの羅列を”ストーリー形式”に変換する流れとしては、まずQ&Aをテーマごとにグループ化します。たとえば「属性に関する情報」「人生観や価値観」「社会的立場や政治的スタンス」などに分けておきます。

次に、それらを「あなたは～のような傾向があります」といった自然な文章に作り直すのです。文と文のあいだに関係性や背景を補足するような形で構成します。

**バックストーリー生成用プロンプト例**

Q&Aをまとめた「プロフィール」情報をストーリーに変換するときに用いるプロンプト例です。以下のように指示することで、断片的な質問・回答を一貫した二人称（「あなたは…」）の物語にまとめられます。

```
You are a background story writer, and you need to craft a comprehensive backstory for a person based on the information provided below.

IMPORTANT INSTRUCTIONS:
1. Please rearrange and reorganize the sequence of this information to ensure it forms a coherent backstory.
2. YOU MUST INCLUDE EVERY SINGLE DATA POINT from the original information - no exceptions.
3. Do not summarize or generalize multiple data points - maintain the specific values, numbers, and exact responses.
4. Each information point in the data consists of a question, possible options, and the person’s actual answer.
5. Focus primarily on the person’s actual responses when creating the backstory.
6. Use second-person format throughout (e.g., "You believe..." "You were born in...").
7. Group related information together for coherence, but never at the expense of omitting details.
8. Format the backstory in clear paragraphs focusing on different aspects (demographics, beliefs, political views, etc.).
9. If the backstory becomes lengthy, that is acceptable - completeness is more important than brevity.
10. Please directly output the final backstory without returning any unnecessary content or explanations.

Review your work carefully before submitting to ensure NO INFORMATION HAS BEEN OMITTED.

This person’s Information:
{profile_text}
```

日本語訳すると以下のようになります。

```
あなたはバックストーリー作家であり、以下に示す情報に基づいて人物の包括的なバックストーリーを作成する必要があります。

重要な指示：
1. この情報を再配置して再構成し、一貫したバックストーリーになるようにしてください。
2. 元の情報に含まれるあらゆるデータポイントを必ずすべて含めてください―例外は認められません。
3. 複数のデータポイントを要約や一般化してまとめることはせず、特定の値、数字、回答を正確に保持してください。
4. 各情報ポイントは質問、選択肢、そしてその人物の実際の回答で構成されています。
5. バックストーリーを作成するときは、主にその人物の実際の回答に焦点を当ててください。
6. 二人称形式（例：「あなたは…と信じています」「あなたは…で生まれました」）を通して使用してください。
7. 関連する情報はまとまりとしてグループ化し、一貫性を保ってください。ただし、詳細を省略してはなりません。
8. バックストーリーは、異なる側面（人口統計、信念、政治的見解など）に焦点を当てた明確な段落で構成してください。
9. バックストーリーが長くなる場合でもかまいません―簡潔さよりも完全さが重要です。
10. 不要な説明や補足を返さず、最終的なバックストーリーをそのまま出力してください。

作業を提出する前に、情報が抜け落ちていないか慎重に確認してください。

この人物の情報：
{profile_text}
```

### 判断の再現に必要な3つの視点

ストーリー形式のプロフィールを入力したら、次に行うのは「その人がどう判断するか」を考えさせる段階です。

人間の意思決定は、単なる計算だけではなく、考え方の癖や感情、行動パターンなど、さまざまな要素が絡み合って決まっていきます。その複雑さに対応するために、判断プロセスを3つの視点「認知」「感情」「行動」に分けて捉えると効果的です。

まずは「認知の視点」です。これは物事をどう考えるかという領域で、情報の受け取り方や、信念の構造、分析の傾向などが反映されます。

次に「感情の視点」では、その人の価値観や感情の動き、動機づけのパターンなどが検討されます。たとえば、同じ出来事に対してポジティブに反応するか、不安を感じるかといった違いが表れます。

最後に「行動の視点」では、実際にどのような行動を取りやすいかを見ていきます。過去の習慣や性格的な傾向、環境からの影響などを含めて判断します。

以下では、各プロンプト例を示します。

**「認知の視点」**

```
Please follow the Tutorial to analyze the User Profile below and answer the Question as if you were this person.

Tutorial:
Consider these cognitive dimensions to understand this user:
- How does this user typically gather and prioritize information?
- What reasoning approaches do they seem to prefer?
- How might their beliefs and worldview frame this situation?
- Which factors would they likely weigh most heavily when deciding?
- What thinking patterns or cognitive tendencies might influence them?

User Profile:
{backstory}

Question:
{question_text_with_options}

Please format your response exactly as follows:
Answer: [option number]
Analysis: [your reasoning for why this user would choose this option]
```

たとえば {backstory} 部分に先ほど生成されたストーリーを、その下に 「Q: …／A: …」 の選択肢つき質問を {question\_text\_with\_options} として与えます。すると「Answer: ③」「Analysis: …」といった形式で返答が得られます。

日本語訳版はこちらです。

```
以下のチュートリアルに従い、下記のユーザープロファイルを分析して、この人物になりきって質問に答えてください。

チュートリアル:
- このユーザーは通常どのように情報を収集し、優先順位付けしますか？
- どのような推論アプローチを好んでいるように見えますか？
- 彼らの信念や世界観はこの状況をどのように形作るでしょうか？
- 意思決定の際に、どの要素を最も重視するでしょうか？
- どのような思考パターンや認知傾向が影響を与える可能性がありますか？

ユーザープロファイル:
{backstory}

質問:
{question_text_with_options}

以下の形式で正確に応答をフォーマットしてください：
Answer: [選択肢番号]
Analysis: [このユーザーがなぜこの選択肢を選ぶかについてのあなたの推論]
```

**「感情の視点」**

```
Please follow the Tutorial to analyze the User Profile below and answer the Question as if you were this person.

Tutorial:
Consider these affective dimensions to understand this user:
- What affective patterns and regulation styles characterize them?
- Which values and principles seem to guide their judgments?
- What affective needs or motivations might be activated here?
- How might they feel about the different possible outcomes?
- In what ways do their relationships and identity influence their feelings?

User Profile:
{backstory}

Question:
{question_text_with_options}

Please format your response exactly as follows:
Answer: [option number]
Analysis: [your reasoning for why this user would choose this option]
```

認知とほぼ同じ構成ですが、着目する要素が「価値観や感情の動き」に寄っています。

日本語訳版：

```
以下のチュートリアルに従い、下記のユーザープロファイルを分析して、この人物になりきって質問に答えてください。

チュートリアル:
- 彼らにはどのような感情パターンや調整スタイルがありますか？
- どのような価値観や原則が彼らの判断を導いているように見えますか？
- どのような感情的ニーズや動機づけがここで活性化している可能性がありますか？
- 異なる結果に対して彼らはどのように感じるでしょうか？
- 彼らの人間関係やアイデンティティは感情にどのように影響しますか？

ユーザープロファイル:
{backstory}

質問:
{question_text_with_options}

以下の形式で正確に応答をフォーマットしてください：
Answer: [選択肢番号]
Analysis: [このユーザーがなぜこの選択肢を選ぶかについてのあなたの推論]
```

**「行動の視点」**

```
Please follow the Tutorial to analyze the User Profile below and answer the Question as if you were this person.

Tutorial:
Consider these behavioral dimensions to understand this user:
- What behavioral tendencies and habits appear in their profile?
- How might their environment and social context influence their actions?
- Which capabilities and limitations might shape their behavioral choices?
- In what ways might past experiences guide their current decisions?
- How might they typically implement their decisions in practice?

User Profile:
{backstory}

Question:
{question_text_with_options}

Please format your response exactly as follows:
Answer: [option number]
Analysis: [your reasoning for why this user would choose this option]
```

行動モジュールは「過去の習慣」「環境からの影響」「実行可能性」など、具体のふるまいにフォーカスします。

日本語訳版：

```
以下のチュートリアルに従い、下記のユーザープロファイルを分析して、この人物になりきって質問に答えてください。

チュートリアル:
- 彼らのプロフィールにはどのような行動傾向や習慣が見られますか？
- 彼らの行動に環境や社会的文脈はどのような影響を与えそうですか？
- どのような能力や制約が行動選択を形作っている可能性がありますか？
- 過去の経験は現在の意思決定にどのような形で影響を与えるでしょうか？
- 意思決定を実際にどのように実行する傾向がありますか？

ユーザープロファイル:
{backstory}

質問:
{question_text_with_options}

以下の形式で正確に応答をフォーマットしてください：
Answer: [選択肢番号]
Analysis: [このユーザーがなぜこの選択肢を選ぶかについてのあなたの推論]
```

### 最後に判断をどうまとめるか

3つの視点からそれぞれ出された答えを、どのように1つにまとめるかが最後のステップです。

単純に多数決や平均をとるのではなく、それぞれの理由や前提に目を向けて、共通する部分と食い違っている部分を見比べながら、最も自然な答えを選びます。

たとえば、「理屈では賛成だけど、気持ちとしては反対」「ふだんなら行動に出るけれど、この状況なら控える」といった揺らぎも反映されやすくなります。より人間らしい応答になるということです。

以下のようなプロンプトを使い、最終的な回答を導きます。

```
You are a coordinator in a user simulation system, and you need to synthesize analyses from three different perspectives to make a final decision.

Question: {question_text}
Options: {options_text}

Cognitive perspective answer: {cognitive_data['answer']}
Cognitive perspective analysis: {cognitive_data['analysis']}

Emotional perspective answer: {affective_data['answer']}
Emotional perspective analysis: {affective_data['analysis']}

Behavioral perspective answer: {behavioral_data['answer']}
Behavioral perspective analysis: {behavioral_data['analysis']}

Consider:
• How their thoughts, feelings, and behavioral tendencies might interact in this situation
• Which aspects of their psychology seem most influential here
• Where their different perspectives align or create tension

Format your response exactly as follows:
Answer: [option number]
Analysis: [your reasoning for this decision]
```

3つの視点から出た「Answer / Analysis」をすべて埋め込んで実行します。どの視点が強く影響しているか、あるいは対立しているかを文脈的に判断しながら、最適な回答を選びます。

プロンプト例の日本語訳版は下記です。

```
あなたはユーザーシミュレーションシステムのコーディネーターであり、3つの異なる視点からの分析を統合して最終的な判断を下す必要があります。

質問: {question_text}
選択肢: {options_text}

認知的視点の回答: {cognitive_data['answer']}
認知的視点の分析: {cognitive_data['analysis']}

感情的視点の回答: {affective_data['answer']}
感情的視点の分析: {affective_data['analysis']}

行動的視点の回答: {behavioral_data['answer']}
行動的視点の分析: {behavioral_data['analysis']}

検討事項:
・この状況で彼らの思考、感情、行動傾向がどのように相互作用するか
・どの心理的側面が最も影響力を持っているか
・それぞれの視点がどこで一致するか、あるいは緊張を生んでいるか

以下の形式で正確に応答をフォーマットしてください:
Answer: [選択肢番号]
Analysis: [この判断に至った理由]
```

## 実験の設計

このアプローチが実際にどの程度うまく機能するのか、複数のモデルと大規模な実データを用いて検証が行われました。情報の選び方やモデルへの渡し方、出力の評価手順に至るまで、現実の応用に近い設定が意識されています。

### 実験で用いたデータ

今回は実験なので、ベースとなる情報源として、世界価値観調査（WVS）の第7波が使われています。これは2017年から2022年にかけて世界66の国や地域で実施された意識調査で、1人あたり約290問の質問に答えている詳細なデータです。内容は、年齢や学歴といった属性情報から、政治観や宗教観、家族観、環境への関心など、かなり幅広い領域をカバーしています。

実際にビジネスの現場で本手法を活用する際にはこうしたデータベースを使用する必要はありませんが、この存在を覚えておくと別の場面で役立つかもしれません。

### 評価方法

再現させたいのは、与えた情報に含まれない問いに対する回答です。そのため、予測対象となる回答は完全に未知の質問として扱われます。

評価方法としては、以下のような基準が設けられています。

-   出力された選択肢が、実際の回答と一致しているか
-   数値の選択肢において、どの程度のズレがあるか（例：10段階の幸福度で予測値が8、実際が6なら誤差2）

### 使用モデルの構成

どのモデルで試したとしても再現性が得られるかを確認するため、LLMが比較に使われています。

使用されたモデルの例としては、

-   Metaによるオープンモデルで、多言語対応と軽量性が特徴のLlama 3.1 8B
-   中国の企業が開発したモデルで、広い文脈の把握と推論への最適化が強みのQwen 2.5 7B
-   対話の自然さや知識表現に特化して訓練されたモデルのDeepSeek V3

モデルごとの違いを統一条件下で見比べることで、提案手法そのものの有効性を正しく評価できるように設計されています。処理コストや導入制約の異なる複数のモデルで再現性が確認されたことは、今後の活用場面を広げるうえでの後押しになります。

## 実験結果

### ベースライン手法との比較

まずは、すでに知られた2つの代表的なアプローチとの比較が行われています。

-   すべてのプロフィール（約230件の質問と回答）をそのままLLMに渡して答えさせる「全情報入力方式」。構造化や要約はせず、ありのままを突っ込むイメージです。
-   プロフィール項目を埋め込み表現に変換し、現在の質問に関連する3項目を抽出して入力する「検索拡張方式」。関連性が高そうな情報だけを選んで使うやり方です。

いずれも、企業などでよく見られる基本的な使い方と言えます。すべて渡すか、一部を選ぶかという違いです。

比較のための実験は、各モデルごとに100人分のユーザーを対象として実施されました。

結果は、すべてのモデルにおいて本手法が最も高い精度を出すかたちとなりました。Llama 3やQwen 2.5では、正答率も誤差の小ささも大きく改善しています。DeepSeekや他のモデルでも同じ傾向が見られました。

![[個人の深い価値観にもとづく「その人らしい答え」をAIで再現する手法 - AIDB/AIDB_90734_2-1024x434.png]]

統計的に見ても、2つのベースラインと比べて有意差が確認されており、LLMの種類に関係なく一貫して高い性能が出ていることが示されています。

ポイントは、情報をそのまま渡すよりも、構造を意識して整理した方がずっと効果的であるということです。やみくもに情報量を増やしたり、モデルを変更したりするよりも、情報の渡し方を工夫するほうが現実的な改善につながる場合があるという示唆を与えてくれる結果です。

### 各モジュールの効果を分けて検証

本手法の構成要素それぞれがどれだけ効果に貢献しているかを確かめるために、要素を一部取り除く実験も行われました。

その結果、ストーリーモジュールを省いて、もとのQ&Aのまま使った場合、性能が落ちる傾向が見られました。どのモデルでも一貫して確認されています。単なる断片的な質問と答えよりも、つながりを意識した文章形式のほうが効果が高いということです。

![[個人の深い価値観にもとづく「その人らしい答え」をAIで再現する手法 - AIDB/AIDB_90734_3-1024x184.png]]

「認知・感情・行動」の3視点で分析する部分を外すと、さらに精度が低下しました。ストーリーだけに頼った場合、どうしても判断が浅くなってしまうようです。

また、認知だけ・感情だけといった形で一部だけを取り除く実験も行われ、それぞれに重要な役割があることが示されました。すべてそろってはじめて、精度が高く保たれるようです。

単一の観点では、その人らしい判断を捉えきれないことがあるということです。

### 入力情報の量が性能に与える影響

最後に、プロフィール情報の量と予測精度の関係を確認するため、段階的にデータ量を変えて検証が行われました。

渡す情報の件数は、0件・58件・116件・174件・232件という5段階で設定されました。

同じ質問に対して、どの程度正確な予測ができるかを比較しています。

結果としては、どのモデルでも、情報が増えるほど精度が上がるという傾向がはっきりと見られました。とくに、最初の50〜100件ほどの増加による効果が大きく、そこから先は徐々に伸びが緩やかになるという形です。

![[個人の深い価値観にもとづく「その人らしい答え」をAIで再現する手法 - AIDB/AIDB_90734_4.png]]

![[個人の深い価値観にもとづく「その人らしい答え」をAIで再現する手法 - AIDB/AIDB_90734_5.png]]

この結果は、実務的にも意味があります。無理に数百件の情報を集めようとしなくても、まずは50〜100件程度をしっかり押さえるだけで、十分に実用的な精度が得られるということです。

たとえば、手元に情報が部分的にしか残っていない場合でも、一定の再現性が期待できます。負担の少ないかたちで、価値観の把握や個別対応ができる可能性があります。

## まとめ

本記事では、人の価値観や判断の傾向をLLMによって再現するためのシミュレーション手法に関する研究を紹介しました。  
プロファイル情報をストーリー形式にまとめる工夫や、認知・感情・行動という複数の視点で同時に判断を再現する設計が提案されています。  
従来の「全情報をそのまま渡す」「関連情報だけを抜き出す」といった方法に比べて、安定して高い精度を示している点が特徴です。  
また、情報量が多ければ多いほど良いわけではなく、100件程度でも十分な再現性が得られることも確認されています。  
読者自身のプロジェクトにおいても、既存のQ&Aデータを再構成して個性を再現したい場面で参考になる手法といえます。

**参照文献情報**

-   タイトル：ValueSim: Generating Backstories to Model Individual Value Systems
-   URL：[https://doi.org/10.48550/arXiv.2505.23827](https://doi.org/10.48550/arXiv.2505.23827)
-   著者：Bangde Du, Ziyi Ye, Zhijing Wu, Jankowska Monika, Shuqi Zhu, Qingyao Ai, Yujia Zhou, Yiqun Liu
-   所属：Tsinghua University, Beijing Institute of Technology, Rice University
