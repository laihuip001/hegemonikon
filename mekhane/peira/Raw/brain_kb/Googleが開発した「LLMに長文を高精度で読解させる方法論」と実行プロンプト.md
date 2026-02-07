---
created: 2026-01-01T10:32:48 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/68821
author: AIDB Research
---

# Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB

> ## Excerpt
> LLMが一度に処理できる文章の長さには限界があり、また長い文章になるほど性能が低下するという問題が指摘されています。 そこでGoogleの研究者らは、人間の読解プロセスに着想を得たアプローチ「ReadAgent」を提案しています。この方法論によりLLMが処理できる文脈の長さを最大20倍に拡張し、様々な長文読解タスクでの性能向上を実現したとのことです。 参照論文情報 本記事の関連研究： 背景 大規模…

---
LLMが一度に処理できる文章の長さには限界があり、また長い文章になるほど性能が低下するという問題が指摘されています。

そこでGoogleの研究者らは、人間の読解プロセスに着想を得たアプローチ「ReadAgent」を提案しています。この方法論によりLLMが処理できる文脈の長さを最大20倍に拡張し、様々な長文読解タスクでの性能向上を実現したとのことです。

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821-1024x576.jpg]]

**参照論文情報**

-   タイトル：A Human-Inspired Reading Agent with Gist Memory of Very Long Contexts
-   著者：Kuang-Huei Lee, Xinyun Chen, Hiroki Furuta, John Canny, Ian Fischer
-   所属：Google DeepMind, Google Research

**本記事の関連研究**：

-   [LLMにおける超長尺のコンテキスト内学習（In-context learning）とファインチューニングの性能比較](https://ai-data-base.com/archives/68564)
-   [LLMにおける、長いコンテキストから欲しい情報を見つけ出す「needle-in-a-haystack（干し草の中の針）」テスト結果とプロンプト例](https://ai-data-base.com/archives/68016)
-   [どのLLMが最も長文要約性能が高いのか評価した実験結果　データセットと要約ノウハウも公開](https://ai-data-base.com/archives/58765)
-   [LLMが生成した長いテキストにおける「事実性」を自動で評価するLLMエージェントフレームワーク『SAFE』Google DeepMindが開発](https://ai-data-base.com/archives/66502)
-   [GPT-4やGeminiなどさまざまなLLMで、プロンプトの入力が長くなるにつれて推論性能に顕著な低下が見られる](https://ai-data-base.com/archives/64873)

## 背景

大規模言語モデル（LLM）が一度に処理できる文章の長さには限界があります。  
また、たとえ制限内の長さ（コンテキストウィンドウ範囲内の文章量）であっても、文章が長くなるほど性能が低下してしまうのです。

一方で、人間は分厚い本を読んだり、長い文章を理解したりするのが得意です。なぜ両者（LLMと人間）に差が生じるのでしょうか？読み方の違いが、その根本的な理由だと考えられています。

LLMは、与えられた文章を単語ごとに忠実に処理します。  
それに対して、人間の読解プロセスはもっと双方向的です。正確な情報はすぐに忘れてしまいますが、読書から得た大まかな要点は長く記憶に残ります。そして、詳細な情報が必要になったら、元の文章を見返すのです。つまり全体的なコンテキストを把握しつつ、ローカルな詳細情報にも注目することで、人間は効率的に長い文章を理解できると考えられています。このようなプロセスがLLMによる文章の真の理解においても役立つ可能性があります。

なお、これまでにもLLMに長い文章を処理させるいくつかのアプローチが研究されてきました。モデルを長い文脈で訓練したり、アーキテクチャを工夫したりする方法などが提案されています。しかし、まだ限界があることが示唆されています。  
また、検索技術を用いてモデルの知識を拡張する検索拡張生成（RAG）も研究されています。大規模なデータベースから関連情報を検索する手法は有用ではあるものの、密接に関連する長い文書の処理には適していない可能性があります。

以上の背景を踏まえ、今回ReadAgentという新しいアプローチが提案されました。前述した人間の読解プロセスにヒントを得たLLMのエージェントシステムです。対話型のプロンプトを用いて、長い文章を効果的に処理します。実験の結果、モデルが効果的に処理できる文脈の長さが大幅に拡張され、様々なタスクでの性能向上が確認されています。以下で詳しく紹介します。

ここから限定コンテンツ

## ReadAgentの仕組み

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_1.png]]

ReadAgentのワークフロー概念図

ReadAgentは、人間の読解プロセスを模倣したシステムです。長い文章を効率的に処理することを目指して以下の3つのステップを踏みます。

### ステップ1: エピソードのページ分割

まず、ReadAgentは長い文章を読み進め、適切な区切りごとに分割します。区切りは、場面の転換や対話の終わりなど、内容の切れ目となる自然な位置に置かれます。

区切りから区切りまでの文章を「エピソード」と呼び、1つのまとまりとして扱います。文章のどこで区切るかは、モデルが判断します。ユーザーはモデルに適切な指示を与えることで、自然な区切り位置を選ばせます。

**ページ分割のプロンプトテンプレート**

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_2.png]]

**原文**

```
You are given a passage that is taken from a larger text (article, book, ...) and some numbered labels between the paragraphs in the passage.
Numbered labels are in angle brackets. For example, if the label number is 19, it shows as &lt;19&gt; in text.
Please choose a label where it is natural to break reading. The label can be a scene transition, the end of a dialogue, the end of an argument, a narrative transition, etc.
Please answer with the break point label and explain.
For example, if &lt;57&gt; is a good point to break, answer with "Break point: &lt;57&gt;\n Because ..."
Passage:
{...}
{PARAGRAPH 5 TEXT}
&lt;5&gt;
{PARAGRAPH 6 TEXT}
&lt;6&gt;
{PARAGRAPH 7 TEXT}
{...}
```

**日本語版**

```
あなたには、より大きなテキスト（記事、本など）から抜粋された文章と、段落間にいくつかの番号付きラベルが与えられます。
番号付きラベルは山括弧で囲まれています。例えば、ラベルの番号が19の場合、テキストでは&lt;19&gt;と表示されます。
読むのを中断するのに自然なラベルを選んでください。ラベルは、場面の転換、対話の終わり、議論の終わり、物語の転換などにできます。
中断点のラベルを答え、説明してください。
例えば、&lt;57&gt;が中断に適している場合は、"Break point: &lt;57&gt;\n Because ..."と答えてください。
文章：
{...}
{段落5のテキスト}
&lt;5&gt;
{段落6のテキスト}
&lt;6&gt;
{段落7のテキスト}
{...}
```

### ステップ2: 要点の抽出

次に、各エピソードから重要な情報を取り出し、短くまとめます。このまとめを「要点」と呼びます。要点は、LLMに指示を与えることで自動的に生成されます。要点には、元のエピソードがどこにあったかを示す情報（ページ番号など）も付け加えられます。こうしてできた要点のまとまりを「要点記憶」と呼びます。なお、論文の原文では、個々の要点を “gist” と呼び、要点の集合体を “gist memory” と呼んでいます。

**要点抽出のプロンプトテンプレート**

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_3.png]]

**原文**

```
Please shorten the following passage.
Just give me a shortened version. DO NOT explain your reason.
Passage:
{PAGE TEXT}
```

**日本語版**

```
次の文章を短くしてください。<br>短くしたバージョンを教えてください。理由は説明しないでください。<br>文章：<br>{ページのテキスト}
```

### ステップ3: 双方向の情報検索

タスクが与えられると、ReadAgentは要点記憶とタスクの内容を見比べ、元の文章のどのページを参照すべきかを決定します。この「双方向の情報検索」には、2つの戦略があります。1つは、必要なページを一度にまとめて検索する並列検索（ReadAgent-P）、もう1つは、1ページずつ順番に検索する逐次検索（ReadAgent-S）です。検索されたページは、要点と組み合わせられ、タスクの解決に用いられます。

**並列検索（ReadAgent-P）による情報検索のプロンプトテンプレート**

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_4.png]]

**原文**

```
The following text is what you remember from reading an article and a multiple choice question related to it.
You may read 1 to 5 page(s) of the article again to refresh your memory to prepare yourself for the question.
Please respond with which page(s) you would like to read.
For example, if you only need to read Page 8, respond with "I want to look up Page [8] to ..."; if you would like to read Page 7 and 12, respond with "I want to look up Page [7, 12] to ..."; if you would like to read Page 2, 3, 7, 15 and 18, respond with "I want to look up Page [2, 3, 7, 15, 18] to ...".
DO NOT select more pages if you don't need to.
You don't need to answer the question yet.
Text:
{GIST MEMORY}
Question:
{QUESTION}
```

**日本語版**

```
以下のテキストは、ある記事を読んで覚えていることと、それに関連する多肢選択問題です。
その質問に答える準備をするために、記事の1～5ページを再度読んで記憶を呼び起こすことができます。
どのページを読みたいか回答してください。
例えば、8ページだけ読む必要がある場合は、「Page [8]を調べたい...」と回答します。7ページと12ページを読みたい場合は、「Page [7, 12]を調べたい...」と回答します。2、3、7、15、18ページを読みたい場合は、「Page [2, 3, 7, 15, 18]を調べたい...」と回答します。
必要以上のページを選択しないでください。
まだ質問に答える必要はありません。
テキスト：
{要点の記憶}
質問：
{質問}
```

**逐次検索（ReadAgent-S）による情報検索のプロンプトテンプレート**

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_5.png]]

**原文**

```
The following text is what you remember from reading a meeting transcript, followed by a question about the transcript. You may read multiple pages of the transcript again to refresh your memory and prepare to answer the question. Each page that you re-read can significantly improve your chance of answering the question correctly. Please specify a SINGLE page you would like to read again or say "STOP". To read a page again, respond with “Page $PAGE_NUM”, replacing $PAGE_NUM with the target page number. You can only specify a SINGLE page in your response at this time. To stop, simply say “STOP”. DO NOT answer the question in your response.
Text:
{GISTS WITH IN-LINE EXPANDED PAGES}
Pages re-read already (DO NOT ask to read them again):
{LIST OF PAGE NUMBERS ALREADY READ}
Question:
{QUESTION}
Specify a SINGLE page to read again, or say STOP.
```

**日本語版**

```
以下のテキストは、会議の記録を読んだことを覚えている内容と、その記録についての質問です。記憶を新たにして質問に答える準備をするために、複数のページを再読することができます。再読する各ページは、質問に正しく答える可能性を大幅に向上させることができます。再読したい単一のページを指定するか、「STOP」と言ってください。ページを再度読む場合は、「Page $PAGE_NUM」と返答し、$PAGE_NUMを目的のページ番号に置き換えてください。この時点で回答できるのは単一のページのみです。停止するには、単に「STOP」と言ってください。質問には回答しないでください。
テキスト:
{GISTS WITH IN-LINE EXPANDED PAGES}
既に再読したページ（再読しないでください）:
{LIST OF PAGE NUMBERS ALREADY READ}
質問:
{QUESTION}
単一のページを再読するか、または「STOP」と言ってください。
```

本フレームワークに従って要点をまとめることで、文章の長さを大幅に短くすることができます。その結果、モデルが一度に処理できる文章の長さが事実上増えることになります。また、要点だけを覚えておけば、課題に関係のない情報を減らせるので、モデルの処理がより効率的になります。

なおReadAgentは、長い文章を処理するだけでなく、さまざまな場面で役立つ可能性を秘めています。

**例1：ウェブページへの応用**

ウェブページはとても長い文章であることが多いので、ReadAgentの技術を使えば、もっと効率的にウェブの情報を処理できるかもしれません。

**例2：他の言語処理への応用**

要点のまとめ方や、必要な情報の探し方は、文章の要約、質問への回答、会話のシステムなど、他の言語処理の分野にも活かせるアイデアです。

## 性能評価実験

ReadAgentの長文読解能力を評価するために、3つの難易度の高い質問応答タスクが用いられました。QuALITY、NarrativeQA、QMSumです。なおデータセットの訓練データを一切使用せずに評価されました。

**QuALITY (Question Answering with Long Input Texts, Yes!)**

多肢選択問題形式のデータセットです。平均5,000トークンの長さの英語の文章で構成されています。

**NarrativeQA**

ストーリー全体の理解を評価するために設計されたデータセットです。サマリーや全文を読んだ後、複数の選択肢から正しい回答を選びます。

**QMSum**

会議などの長いセッションから情報を要約することに焦点を当てたデータセットです。特定の質問に対する答えや要約を生成する能力を評価することを目的としています。

### 評価方法

モデルの出力を自動的に評価する際には、「LLM Rater」と呼ばれるプロンプトが使用されました。モデルが生成した応答を、人手で作成された参照応答と比較し、完全一致（LR-1）または部分一致（LR-2）の割合を計算します。人手による評価に近い自動評価が可能になります。LR-1は厳密な評価、LR-2はより緩やかな評価と位置づけられています。

**LR-1（厳密な評価）のプロンプトテンプレート**

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_6.png]]

原文

```
After reading some text, John was given the following question about the text:
{QUESTION TEXT}
John's answer to the question was:
{MODEL RESONSE TEXT}
The ground truth answer was:
{REFERENCE RESPONSE TEXT}
Does John's answer agree with the ground truth answer?
Please answer YES or NO.
```

**日本語版**

```
ある文章を読んだ後、ジョンにはその文章に関する以下の質問が与えられました:
{質問文}
ジョンの答えは以下の通りでした:
{モデルの応答文}
正解の答えは以下の通りでした:
{参照応答文}
ジョンの答えは正解と一致していますか?
YESまたはNOで答えてください。
```

**LR-2（緩やかな評価）のプロンプトテンプレート**

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_7.png]]

**原文**

```
After reading some text, John was given the following question about the text:
{QUESTION TEXT}
John's answer to the question was:
{MODEL RESONSE TEXT}
The ground truth answer was:
{REFERENCE RESPONSE TEXT}
Does John's answer agree with the ground truth answer?
Please answer "Yes", "Yes, partially", or "No". If John's response has any overlap with the ground truth answer, answer "Yes, partially". If John's response contains the ground truth answer, answer "Yes". If John's response is more specific than the ground truth answer, answer "Yes".
```

**日本語版**

```
ある文章を読んだ後、ジョンにはその文章に関する以下の質問が与えられました:
{質問文}
ジョンの答えは以下の通りでした:
{モデルの応答文}
正解の答えは以下の通りでした:
{参照応答文}
ジョンの答えは正解と一致していますか?
"Yes"、"Yes, partially"、または"No"で答えてください。ジョンの応答が正解と少しでも重なっている場合は、"Yes, partially"と答えてください。ジョンの応答が正解を含んでいる場合は、"Yes"と答えてください。ジョンの応答が正解よりも具体的である場合は、"Yes"と答えてください。
```

### 比較対象

ReadAgentの性能は、いくつかの異なる手法と比較されました。実験ではすべて同じモデルを使用しています。

1.  関連する文章を検索し、それを用いて質問に答える検索拡張生成（RAG）。
2.  文章全体をモデルに入力して質問に答えるアプローチ。
3.  要点記憶だけを使って質問に答えるアプローチ。

なお、評価指標として、圧縮率が重要な役割を果たします。元の文章の長さに対する、モデルが実際に処理した文章の長さの割合を示します。圧縮率が高いほど、モデルは少ない情報で質問に答えなければならないことを意味します。

また、今回の実験で使用された基盤モデルは以下の通りです。

1.  PaLM 2-L
    -   Googleが開発したLLM
    -   コンテキスト長は8,192トークン
    -   主要な実験と評価に使用
2.  GPT-3.5
    -   OpenAIが開発したLLM
    -   コンテキスト長は16,000トークン以上
3.  DeBERTa-base
    -   Microsoftが開発したBERTベースのモデル
    -   Mind2Webのベースラインモデル「MindAct」で、タスク関連の要素検索に使用

## 実験結果

QuALITYでは、ReadAgentが最も高い性能を示しました。完全な文章を使用するアプローチよりも高い精度を達成し、圧縮率は66.97%でした。ReadAgentが元の文章の3分の1程度の情報で質問に答えられることを示しています。

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_8.png]]

QuALITYの元のテキストと要約の単語数ヒストグラム

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_9.png]]

QuALITYデータセットにおけるReadAgentと他手法の比較結果

NarrativeQAは、3つのタスクの中で最も長い文章を含むデータセットです。平均の文章長は7万語以上、最大では34万語にもなります。このような極端に長い文章に対しても、ReadAgentは最良の結果を示しました。ベストの検索ベースラインと比べ、ROUGE-Lスコアが31.98%向上し、圧縮率は約95%でした。

なおROUGE-Lスコアは、自動要約の評価指標の1つです。ROUGEは「Recall-Oriented Understudy for Gisting Evaluation」の略で、ROUGE-Lはバリエーションの中でも最も広く使われている指標の1つです。単語の一致度だけでなく、単語の並びの最長一致を考慮するため、より文脈を捉えた評価ができると考えられています。

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_10-1024x576.png]]

NarrativeQAデータセットにおけるReadAgentと他手法の比較結果

QMSumでは、ReadAgent-Sが最も高い性能を示しました。順次検索を用いることで、並列検索よりも高いROUGEスコアとLLMレーティングを達成しました。（ただし、順次検索は並列検索よりも多くの計算コストを必要とします。）

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_11-1024x480.png]]

QMSum検証データにおけるReadAgentと他手法の比較結果

以上の結果から、ReadAgentが長文読解タスクにおいて非常に有効であることが示されました。要点抽出と双方向の情報検索を用いることで、LLMの制約を大幅に緩和し、長い文章に対する質問応答の性能を向上させることができました。

### 詳細分析

研究者らはReadAgentの性能をさらに詳しく分析するために、アブレーション実験（条件を細かく変更した実験）を行いました。

まず、エピソードのページ分割方法を比較しました。LLMを用いて自然な一時停止点を選択する方法と、単純に一定の長さで分割する方法を比べたところ、前者の方が高い性能を示しました。これはつまり文章構造を考慮したページ分割を行うのが重要であることを示しています。

また、要点抽出の圧縮率とタスク性能の関係も調べられました。圧縮率が高すぎても低すぎても、性能が低下する傾向が見られました。適度な圧縮率が重要であるということです。

さらに、検索方法の比較も行われました。ReadAgentの検索方法と、ニューラル検索（従来の検索手法）を組み合わせた方法を比べたところ、ReadAgentの方が高い性能を示しました。

![[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト - AIDB/AIDB_68821_12.png]]

上記の結果から、ReadAgentの各要素が巧みに機能していることが明らかになりました。

本記事では、大規模言語モデルの長文読解能力を向上させるReadAgentという手法を紹介しました。人間の読解プロセスを模倣することで、モデルの制約を緩和し、より自然な文章理解を可能にしています。

手法のポイントとしては、長い文章をエピソードに分割し、各エピソードから要点を抽出して要点記憶を作成する点にあります。そして、タスクに応じて、要点記憶と元の文章を双方向に検索することで、必要な情報を効率的に取得します。

実験結果は全体的に、ReadAgentの有効性を強く示すものでした。長文読解タスクにおいて従来の手法を大きく上回る性能を達成しました。極端に長い文章に対しても優れた結果を示しました。

書籍レベルの長い文章をLLMのサポートで読解したいシーンはあらゆる業界や業種で出てくることが予想されます。そんなとき、このような知見を役立てられるかもしれません。

-   URL：[https://doi.org/10.48550/arXiv.2402.09727](https://doi.org/10.48550/arXiv.2402.09727)
-   GitHub：[https://read-agent.github.io/](https://read-agent.github.io/)
