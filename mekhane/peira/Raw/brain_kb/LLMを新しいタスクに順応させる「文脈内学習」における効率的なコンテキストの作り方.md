---
created: 2026-01-01T11:17:19 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/96070
author: AIDB Research
---

# LLMを新しいタスクに順応させる「文脈内学習」における効率的なコンテキストの作り方 - AIDB

> ## Excerpt
> LLMを特定のタスクに使う際、いくつかの例を見せるだけで推論させる「文脈内学習」という技術があります。モデルを再訓練する必要がなく、とても便利な方法です。最近では、LLMが一度に処理できる文脈が大幅に長くなったため、数百個もの例を見せる「多ショット文脈内学習」が可能になり、性能も向上することが分かってきました。 しかし大量の例を毎回処理するのはデメリットもあるため、同様の性能を維持しながらトークン…

---
LLMを特定のタスクに使う際、いくつかの例を見せるだけで推論させる「文脈内学習」という技術があります。モデルを再訓練する必要がなく、とても便利な方法です。最近では、LLMが一度に処理できる文脈が大幅に長くなったため、数百個もの例を見せる「多ショット文脈内学習」が可能になり、性能も向上することが分かってきました。

しかし大量の例を毎回処理するのはデメリットもあるため、同様の性能を維持しながらトークン効率の良い方法が求められています。

![[LLMを新しいタスクに順応させる「文脈内学習」における効率的なコンテキストの作り方 - AIDB/AIDB_96070-1024x576.png]]

**本記事の関連研究**

-   [プロンプトに例を多く載せるほど、どんなタスクでも性能が上がるのか？DeepMindによる『Many-shot Learning』の実験結果](https://ai-data-base.com/archives/67883)
-   [スタンフォード大学の研究者ら、GPT-4oとGemini1.5 Proで「マルチモーダルモデルにおける『Many-Shot』の効果」を検証](https://ai-data-base.com/archives/69211)

## 背景

LLMを特定のタスクに活用する方法として、「文脈内学習」（英文では「In-Context Learning」）があります。これは何かというと、モデルに具体的な例をいくつか見せることで、そのタスクのやり方を理解させる方法です。例えば、英語を日本語に翻訳するタスクであれば、いくつかの翻訳例を見せてから「では、この新しい英文を翻訳してください」と頼むわけです。この方法の素晴らしいところは、モデル自体を再訓練する必要がないということです。

しかし、ここに大きな問題があります。多数の例を毎回モデルに読ませるということは、それだけコストが高くなるということです。例えば、150個の例を含む入力は、数万トークン、場合によっては数十万トークンにもなります。トークンというのは、テキストの最小単位のようなもので、計算量や料金の基準になります。このような長い入力を処理するには、時間もお金も大量にかかってしまうのです。また、精度面にも悪い影響があるかもしれません。

そこで本記事では、多数の例を活用した文脈内学習を効率化する手法について調べました。

以下で詳しくお話しします。

ここから限定コンテンツ

**参照文献情報**

-   タイトル：Distilling Many-Shot In-Context Learning into a Cheat Sheet
-   URL：[https://doi.org/10.48550/arXiv.2509.20820](https://doi.org/10.48550/arXiv.2509.20820)
-   著者：Ukyo Honda, Soichiro Murakami, Peinan Zhang
-   所属：CyberAgent

## そもそも文脈内学習とは

文脈内学習では、入力と出力のペアである「デモンストレーション」と呼ばれる例を使います。例えば、英語を日本語に翻訳するタスクであれば、入力は英文、出力は日本文になります。このような入力と出力のペアをn個集めたものをデモンストレーションのセットと呼びます。

実際に文脈内学習で推論を行う際には、これらのデモンストレーションと、新しいテスト入力を組み合わせて、LLMに提示します。すると、モデルは、提示された全ての情報に基づいて、最も確率が高い出力を選択します。ここで「確率が高い」というのは、モデルが学習した膨大なデータから判断して、「このような入力と例が与えられたときに、この出力が来る可能性が最も高い」ということです。

このデモンストレーションの数nを大幅に増やしたものを多ショット文脈内学習と呼びます。従来は数個だったのが、数十個、数百個になるわけですね。最近のLLMは、一度に処理できるトークン数が飛躍的に増加したため、このような多数の例を扱えるようになりました。トークン数が数桁も増えたと論文には書かれています。数桁というのは、10倍、100倍、1000倍といったオーダーの増加を意味します。

先ほど説明した通り、この多ショット文脈内学習は従来の少数例文脈内学習よりも性能が良いことが分かっています。しかし、それだけ多くの情報を処理するため、計算コストも比例して高くなってしまうのです。

## 「チートシート文脈内学習」という新手法

上記の問題を解決するために、チートシート文脈内学習という手法が考案されています。基本的なアイデアは、多ショットのデモンストレーションから学べるパターンを、コンパクトなチートシートに要約してしまおうというものです。

ここで重要なのは、直感です。研究者たちは、LLMが持つ高度な言語理解能力があれば、学習した知識をテキスト形式で表現できるのではないかと考えました。これは人間がやることと似ています。私たちは、試験勉強をする際、たくさんの例題を解いた後、その中から重要なパターンや解法のコツを抽出して、自分なりのノートにまとめます。著者たちは、LLMにも同じことができるのではないかと考えたのです。

実際、最近のLLMは非常に高いレベルの言語理解能力を持っています。学習したパターン全体をテキスト形式で要約することも可能なはずです。こうすれば、毎回の推論時に多ショットのデモンストレーションを文脈に入れて、そこからパターンを抽出する必要がなくなります。

### チートシートの作成方法

チートシート文脈内学習における最も重要なステップは、チートシートを作成する前処理です。この点が非常に重要なのです。

具体的な手順を説明しましょう。

まず、LLMに対して、デモンストレーションのセット全体を提示します。これは、理由付きのデモンストレーション、つまり

-   入力
-   理由
-   出力

の三つ組がn個並んだものです。

なお理由とは、正解を選んだ根拠ということです。短く示すだけでOK。

そして、このデモンストレーションと一緒に、特別に設計されたプロンプトを使用します。

以下に例を載せます。

**チートシート作成プロンプト（原文のまま）**

```
Create a cheat sheet based on the examples below.
You will be asked to answer questions similar
to these examples during the test, without being
allowed to refer to the examples at that time.
Your task here is to make a cheat sheet that will
help you answer such problems correctly. First,
carefully read the examples below and identify
which ones you find most difficult to answer.

{\hat{D}_n}

Now, create a cheat sheet to help you solve the
difficult examples. Exclude any content that is
easy for you, and only include specific, detailed
points to address the challenging ones.
```

**日本語訳**

```
下の例に基づいてチートシートを作成してください。
テスト中に、これらの例に似た問題に答えるよう求められますが、
そのときに例を参照することは許されません。
ここでのあなたの課題は、そのような問題に正しく答える助けとなる
チートシートを作ることです。まず、下の例を注意深く読み、
自分が最も答えにくいと感じるものを特定してください。

{\hat{D}_n}

次に、難しい例を解くのに役立つチートシートを作成してください。
自分にとって簡単な内容は除外し、挑戦的な問題に対処するための
具体的で詳細なポイントのみを含めてください。
```

簡単に言うと、「これらの例を見て、あなたが難しいと感じる例を特定してください。そして、その難しい例を正しく解くためのチートシートを作成してください。簡単な内容は除外し、難しいものに対処するための具体的で詳細なポイントだけを含めてください」といった内容です。

このプロンプトによってLLMが生成した出力を、「チートシート」と呼びます。

具体的なタスクについて生成されたチートシートの例を示します。表形式や箇条書き形式で、パターンや注意点が整理されています。

**作成されるチートシートの例（原文のまま）**

```
# Pronoun Antecedent Cheat Sheet ( for Difficult Cases )
## 1. ** General Reasoning Steps **
- ** Identify all possible antecedents ** for the pronoun .
- ** Substitute each antecedent ** into the sentence to see if it makes sense .
- ** Consider the context and logic ** of the sentence : Who is likely to perform the action or possess the
attribute ?
- ** Check for grammatical cues **: number ( singular / plural ) , gender , and role in the sentence .
- ** If both options are equally plausible and the sentence gives no extra clues , mark as ambiguous .**
---
## 2. ** Common Patterns and How to Resolve Them **
### A . **" X told Y that [ pronoun ]..."**
- Usually , the pronoun refers to ** Y ** if the information is about Y ( e . g . , advice , diagnosis , payment ) .
- If the information is about X's own actions or status , it refers to ** X **.
- ** Tip :** Would it make sense for X to inform Y about Y's own actions ? Usually not , unless it 's advice or
a warning .
### B . **" X did something to Y because [ pronoun ]..."**
- The pronoun can refer to either X or Y .
- ** Test both :** Substitute both and see which makes more logical sense .
- If both are plausible , ** mark as ambiguous **.
### C . **" X and Y discuss [ pronoun ]'s Z "**
- If both X and Y could logically possess Z , and the sentence gives no further context , ** mark as
ambiguous **.
- If only one is likely to possess Z ( e . g . , " culinary training " is more likely the chef 's ) , pick that one .
### D . **" X called Y and asked [ pronoun ] to do Z "**
- The pronoun usually refers to ** Y ** ( the person being asked to do something ) .
- If it would be odd for X to ask themselves , it 's almost always Y .
### E . **" X met with Y at [ pronoun ]'s office "**
- If both X and Y could be the owner of the office , and the sentence gives no clue , ** mark as ambiguous **.
- If only one is plausible ( e . g . , meeting a director at the director 's office ) , pick that one .
### F . **" X did something with Y because [ pronoun ] [ verb / attribute ]"**
- If the verb / attribute fits both X and Y , and both are plausible , ** mark as ambiguous **.
- If only one makes sense ( e . g . , " focuses on code " fits developer , not writer ) , pick that one .
### G . ** Possessive Constructions (" the writer and [ pronoun ] friends ") **
- The possessive pronoun almost always refers to the first noun (" the writer and her friends " = the writer
's friends ) .
- If the pronoun could refer to more than one noun , but only one makes sense , pick that one .
## 3. ** Ambiguity Triggers **
- If both antecedents are equally plausible and the sentence gives no further context , ** choose " Ambiguous
"**.
- Watch for sentences where both X and Y could have performed the action , received the attribute , or owned
the object .
---
## 4. ** Special Cues **
- ** Gender / Number Agreement :** Make sure the pronoun matches the possible antecedent in gender and number .
- ** Role / Profession :** Sometimes , the profession or role makes one antecedent more likely ( e . g . , only a
scientist needs a lab assistant ) .
- ** Typical Scenarios :** Use real - world logic ( e . g . , a mechanic calls a customer about the customer 's car ,
not their own ) .
---
## 5. ** Quick Reference Table **
| Structure | Most Likely Antecedent | When Ambiguous ?
|
| - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -| - - - - - - - - - - - - - - - - - - - - - - -| - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -|
| X told Y that [ pronoun ]... | Y ( if advice / info ) | If both could be true |
| X did Y because [ pronoun ]... | X or Y ( test both ) | If both make sense |
| X and Y discuss [ pronoun ]'s Z | Context - dependent | If both could own Z |
| X called Y and asked [ pronoun ] to do Z | Y | If both could be asked |
| X met with Y at [ pronoun ]'s office | Context - dependent | If both could own office |
| X did Y because [ pronoun ] [ verb / attribute ] | Context - dependent | If both fit |
| The writer and [ pronoun ] friends | The writer | If only one makes sense |
---
## 6. ** Ambiguity Checklist **
- Both antecedents are grammatically possible .
- Both antecedents are logically possible .
- No context or world knowledge tips the scale .
- If all above are true , ** choose " Ambiguous "**.
---
** Use this sheet to reason through each step , especially when both antecedents seem possible !**
```

ここで注目すべき点は、このチートシート作成が、タスクごとに一度だけ実行されるということです。つまり、ある推論タスク、例えば「代名詞の曖昧性解消」というタスクがあったとして、そのタスクについてチートシートを一度作成すれば、その後は何千回、何万回とそのタスクの問題を解く際にも、同じチートシートを使い回せるのです。

「チートシート長いな」と思われたかもしれませんが、例を多数載せるよりもはるかにコンパクトな情報量になります。

なお、チートシートの内容を人間が読んで理解し、手動で修正することで性能が向上する場合もあります。

### 推論時のチートシート使用方法

推論時には、LLMに対して、作成したチートシートとテスト入力を提示します。そして、2つの例を提供します。なぜ2つの例を提供するのかというと、「こういう形式で答えを出力してください」ということを示すためです。例えば、答えを何らかの文字列の後に書くとか、特定のフォーマットで構造化するとか、そういった出力形式をLLMに理解させるために、少数の例を見せるのです。

## この方法は本当にワークする？

それでは提案されたチートシート文脈内学習が実際にどれだけ効果的なのかを検証した結果を見ていきます。

### 実験内容

選ばれたのが、[BIG-Bench Hard](https://github.com/suzgunmirac/BIG-Bench-Hard)にある8つの推論タスクでした。  
ブール式評価、因果判断、曖昧性解消質問応答、幾何学図形識別、映画推薦、顕著な翻訳エラー検出、スポーツ理解、単語ソートの8つです。

また、全ての実験でGPT-4.1を使用しています。（大きなコンテキストウィンドウを持つモデルであれば実験可能です。）

評価方法についても触れておきます。全てのタスクは正解率、つまりAccuracyで評価されます。

### 主な結果

それでは、メインとなる実験結果を見ていきましょう。図には、8つのタスクについての結果がグラフで示されています。横軸は入力トークン数、縦軸は正解率です。

![[LLMを新しいタスクに順応させる「文脈内学習」における効率的なコンテキストの作り方 - AIDB/AIDB_96070_1-1024x422.png]]

8つのタスクのうち7つで、チートシート文脈内学習が、同じかそれ以下の入力トークン数で、少数例文脈内学習を上回る性能を示しました。グラフの右端にある多ショット文脈内学習と比較しても、はるかに少ない入力トークンで、同等かそれ以上の性能を達成しています。

具体的な数字を見てみましょう。例えば、Boolean Expressionsというブール式評価タスクでは、チートシート文脈内学習は約6000トークンで99.7%の正解率を達成しました。一方、150例を使う多ショット文脈内学習は約25000トークン、つまり4倍以上のトークンを使って100%の正解率です。わずか0.3パーセントポイントの差のために、4倍以上のコストがかかるわけですから、チートシート文脈内学習の効率の良さが際立ちます。

Movie Recommendationという映画推薦タスクでは、さらに顕著な結果が出ています。チートシート文脈内学習は約10000トークンで93.7%の正解率を達成しましたが、150例の多ショット文脈内学習は約30000トークンを使って97.0%です。ここでは、チートシート文脈内学習の方が性能は若干劣りますが、それでも3分の1のトークン数で、それなりの性能を維持しています。

一方、Geometric Shapesという幾何学図形識別タスクでは、チートシート文脈内学習が95.3%、150例の多ショット文脈内学習も95.3%と、全く同じ正解率を達成しています。しかし、トークン数を見ると、チートシート文脈内学習は約20000トークン、多ショット文脈内学習は約60000トークンと、3分の1で済んでいます。

これらの結果は、チートシート文脈内学習の効果と効率性を明確に示しています。チートシート文脈内学習は8例の少数例文脈内学習とほぼ同じ時間とコストで実行できることが示されています。

### チートシートは転用可能

GPT-4.1で作成したチートシートを、Gemini 2.0 Flashという別のモデルに提供したところ、ほとんどのケースで、チートシートは似たような改善効果を示し、モデル間で良好な転用可能性を持つことが確認されました。

ただし、いくつかのタスクでは、性能が劣る結果となりました。しかしこれらのタスクでは、Gemini 2.0 Flashでは多ショット文脈内学習自体が効果的でなかったのです。それでも、チートシート文脈内学習は多ショット文脈内学習よりは良い結果を示しています。

## まとめ

以上、新しく提案された「チートシート文脈内学習」について、手法の詳細から実験結果まで見てきました。

多数の例から学べる知識を簡潔なテキスト形式に圧縮するというシンプルなアイデアが多くのケースで有効である可能性が示されました。

実務者にとって注目すべき点は、この手法が既存の商用LLMにそのまま適用できることです。

ただし、この手法にも限界があります。多ショット文脈内学習自体が効果的でないタスクでは、チートシート文脈内学習も同様の制約を受けます。

LLMを効率的に活用するための一つの選択肢として、検討に値するかもしれません。
