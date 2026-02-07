---
created: 2026-01-01T11:19:25 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/71720
author: AIDB Research
---

# LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB

> ## Excerpt
> 特定の高難易度タスクにおけるLLMエージェントの性能を大幅に向上させる新しい手法SelfGoalが考案されました。最終目標をより実践的なサブゴールのツリー構造に分解し、状況に応じてサブゴールを更新するのが本手法の肝です。 参照論文情報 本記事の関連研究： 背景 LLMエージェントは、ゲームやプログラミングなどの分野でよく利用されています。タスク固有の学習をすることなく、複雑で難易度の高いタスクを自…

---
特定の高難易度タスクにおけるLLMエージェントの性能を大幅に向上させる新しい手法SelfGoalが考案されました。最終目標をより実践的なサブゴールのツリー構造に分解し、状況に応じてサブゴールを更新するのが本手法の肝です。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720-1024x576.jpg]]

**参照論文情報**

-   タイトル：SelfGoal: Your Language Agents Already Know How to Achieve High-level Goals
-   著者：Ruihan Yang, Jiangjie Chen, Yikai Zhang, Siyu Yuan, Aili Chen, Kyle Richardson, Yanghua Xiao, Deqing Yang
-   所属：Fudan University, Allen Institute for AI

**本記事の関連研究**：

-   [プロンプトでLLMにRPAワークフローを自動生成させる手法「FlowMind」JPモルガン考案](https://ai-data-base.com/archives/68095)
-   [LLMにタスクに応じた推論プロセスを自ら考えるようにするプロンプト手法『SELF-DISCOVER』Google DeepMindなどが開発](https://ai-data-base.com/archives/64136)
-   [LLMエージェントの設計16パターン](https://ai-data-base.com/archives/69483)　

## 背景

LLMエージェントは、ゲームやプログラミングなどの分野でよく利用されています。タスク固有の学習をすることなく、複雑で難易度の高いタスクを自動的に解決する技術として、注目されてきています。

しかし、LLMエージェントには、「ユーザーからの曖昧な指示に従えない」などの課題があります。例えば、「この勝負に勝ってください」や「お金を稼いでください」といった、抽象的な指示を与えても、エージェントはユーザーの意図を汲み取れず、タスクを遂行できないでしょう。

こうした課題を解決し、難易度の高いタスクを自動でLLMに解かせるために、既存の研究では主に以下の2つのアプローチが提案されてきました。

-   LLMの事前知識を利用して、最終タスク目標を細かなサブタスクに分解
-   タスクの遂行中に、LLMの事前知識を引っ張り出して有効活用すること

しかし、前者のアプローチだと、環境要因の変化によって、解くべきサブタスクを調整することができず、柔軟性に欠けるという問題が発生します。また、後者のアプローチだと、事前知識から導かれる行動が、そもそも単純で体系的でないため、適切なアクションを起こせないという問題が発生します。

そのため、環境要因の変化に応じて、その都度最適なアプローチを模索しながら、柔軟にサブタスクを変更する必要があるのです。

そこで今回研究者らは、最終のタスク目標をツリー構造のサブゴールに分解し、エージェントのおかれた状況に応じて最も有用なサブゴールを特定しながら、ツリーを段階的に更新していく「SelfGoal」という手法を提案しています。

以下では、このSelfGoalについて詳しく解説します。

ここから限定コンテンツ

## 提案手法

SelfGoalの本質は、以下の流れに従って最終目標を達成することです。

1.  最終目標をサブゴールに分解し「ゴールツリー」を構築
2.  ゴールツリーに従って、サブゴールを達成するためのアクションを起こす
3.  そのアクションの結果、状況が変化する
4.  その状況変化に応じて、ゴールツリーを再構築

この流れを表したのが、以下の図です。左側はSelfGoalの流れを表し、右側はゴールツリーの全体像を表します。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_3-1024x458.png]]

この処理をアルゴリズムで表すと、以下のようになります。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_6.jpg]]

このアルゴリズムにおける記号の意味は、以下の通りです。

– \\( g\_0 \\): 最終タスク目標  
– \\( \\zeta \\): スレッショルド（重複したサブゴールがツリーに追加されるのを防ぐためのコサイン類似度の閾値）  
– Stopping criterion: アルゴリズムが終了する条件  
– \\( M^i \\): エージェント  
– \\( \\pi\_{\\theta}(a\_i, s\_i) \\): ステップ目の状態における、行動 \\(a\_i\\) をとる確率（θはパラメータ  
– \\( p\_i \\): エージェントが次に取るべきアクションに関する指示テキスト（プロンプト）  
– \\( s\_i \\): ステップ目の状態・状況  
– \\( a\_i \\): ステップ目のエージェントのアクション  
– \\( T \\): ゴールツリー  
– \\( t \\): タイムステップ

ここで重要なのは、\\( \\pi\_{\\theta}(a\_i, s\_i) \\) であり、エージェントの行動を決定するものとなります。本論文では、「次の行動を示すもの」として「ポリシー」と表現されています。

### オークションの例

「オークション」を例に、本手法のエージェントの振る舞いを考えてみましょう。

ポリシー \\( \\pi\_{\\theta}(a\_i, s\_i) \\) は、例えば次のような指針を含むとします。

– 状態\\(s\\): 現在の入札状況（例えば、現在の最高入札額、残りの予算、他の参加者の数）  
– 行動\\(a\\): 次に行う行動（例えば、特定の金額で入札する、入札をやめる、次のアイテムに移る、等）

このようなオークションのシナリオで、エージェントが特定の状態（現在の入札価格、他の参加者の行動など）に基づいて、「次の行動（次に入札する金額）」の \\( \\pi\_{\\theta}(a\_i | s\_i) \\) を決定するとします。そこで、エージェントは、最適な行動がとれるよう、 \\( \\pi\_{\\theta}(a\_i | s\_i) \\) のパラメータを調整します。

ちなみに、オークションのような文脈では、最終目標が「最高の利益を得る」とすると、階層的なサブゴールには、以下のようなものが考えられるでしょう。

-   予算を効果的に管理する
    -   初期段階で高価なアイテムに入札しない
    -   ラウンドごとに入札金額を調整する
-   競争相手の行動を分析する
    -   他の入札者の予算を推測する
    -   競争相手の入札パターンを観察する
-   戦略的に入札する
    -   低競争のアイテムに焦点を当てる
    -   重要なアイテムのために予算を確保する

サブゴールを階層的にすることで、「サブゴールを達成するために、サブゴールのさらにサブとなるゴールを達成する」といった段階的な目標を策定できます。

オークションの例では、これらのサブゴールに従うことで、エージェントはより戦略的に入札し、最高の利益を得ることができるようになります。

当然、オークションは時間の経過とともに局面が変わるため、その都度柔軟に上記のサブゴールを変更し、適切な戦略を取る必要があるかもしれません。こうしたサブゴールの変更も、SelfGoalではエージェントが自動的に行うのです。

### LLMに入力されるプロンプト

ここでは、SelfGoalフレームワーク内で使用されたプロンプトを紹介します。

メインゴールから具体的なサブゴールを導き出すために使用されたプロンプト（Decomposition Instruction）は、以下の通りです。

\# Main Goal  
Humans exhibit numerous behaviors and sub-goals, which can be traced back  
to the primary aim of survival. For instance:

1\. Food Acquisition: To maintain physical and mental functionality,  
individuals seek nourishment. They target foods with high energy and  
nutritional values to augment their health, thus enhancing survival  
possibilities.  
2\. Shelter Construction: Safe and secure housing is a fundamental human  
need. It offers protection from potentially harmful natural elements and  
potential threats.

Imagine you are an agent in an ascending-bid auction. You will compete  
against other bidders in a bidding war. The price steadily increases as  
bidders progressively pull out. Eventually, a single bidder emerges as  
the winner, securing the item at the final bid.

Taking analogy from human behaviors, if your fundamental objective in  
this auction is “{goal}”, what sub-goals you might have?

——————————

\# Sub-Goal  
For the goal: “{sub\_goal}”, can you further run some deduction for fine-  
grained goals or brief guidelines?

和訳：

\# 主な目標  
人間は生存という主要な目標に基づく数多くの行動やサブゴールを示します。例えば：  
食糧の確保：身体的および精神的な機能を維持するために、個人は栄養を求めます。彼らは高エネルギーで栄養価の高い食物を選び、健康を増進させることで生存の可能性を高めます。  
住居の構築：安全で安心な住まいは人間の基本的な必要です。これは、潜在的に有害な自然要素や脅威からの保護を提供します。  
あなたが上昇入札オークションのエージェントだと想像してください。あなたは他の入札者と競り合います。入札者が次々と退出するにつれて価格は徐々に上昇します。最終的に、一人の入札者が勝者となり、最終入札額でアイテムを獲得します。  
人間の行動の類推を取ると、このオークションであなたの基本的な目的が「{goal}」である場合、どのようなサブゴールが考えられるでしょうか？

——————————

\# サブゴール  
目標：「{sub\_goal}」について、さらに細分化された目標や簡単なガイドラインを導き出せますか？

現在の状況に基づいて適切なサブゴールを選択するために使用されるプロンプト（Search Instruction）は、以下の通りです。

Here’s the current scenario:  
{scene}  
——————————  
To better reach your main goal: {objective}, in this context, please do  
the following:

1.Evaluate how the sub-goals listed below can assist you in reaching your  
main goal given the present circumstances.

Sub-goals:  
{guidance}  
2\. Select {width} most useful sub-goals that will help you reach your  
main goal in the current situation, and note their IDs.  
Start by explaining your step-by-step thought process. Then, list the {  
width} IDs you’ve chosen, using the format of this example: {{“IDs”: \[1,  
3, 10, 21, 7\]}}.

和訳：

現在のシナリオは次のとおりです：  
{scene}  
——————————  
あなたの主な目標：{objective} によりよく到達するために、この文脈で次のことを行ってください：  
以下にリストされたサブゴールが現在の状況下で主な目標達成にどのように役立つかを評価してください。  
サブゴール：  
{guidance}  
2\. 現在の状況で主な目標達成に役立つ最も有用なサブゴールを{width}個選び、そのIDを記録してください。  
まず、あなたのステップバイステップの思考過程を説明してください。次に、選択した{width}個のIDを、次の例の形式でリストしてください：{{“IDs”: \[1, 3, 10, 21, 7\]}}。

最後に、エージェントがサブゴールに基づいて具体的な行動を取るためのプロンプト（Task Solving Instruction）は、以下の通りです。

Here is the current scenarios:

{scene}

——————————  
Here are some possible subgoals and guidance derived from your primary  
objective {main\_goal}:

{sub\_goals}

In this round, You may target some of these subgoals and detailed  
guidance to improve your strategy and action, to achieve your primary  
objective.

和訳：

現在のシナリオは次のとおりです：  
{scene}  
——————————  
以下は、あなたの主な目標 {main\_goal} から導かれた可能なサブゴールとガイダンスです：  
{sub\_goals}  
このラウンドでは、これらのサブゴールと詳細なガイダンスのいくつかをターゲットにして、戦略と行動を改善し、主な目標を達成することができます。

## 実験内容

SelfGoalフレームワークを評価するために、論文では以下の4つのタスクとそれに対応する環境が使用されました。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_8-1024x349.png]]

各タスクの詳細は、以下の通りです。

### Public Goods Game

Public Goods Game（公共財ゲーム）は、協力行動と個人の利益のバランスを探るためのゲームです。各プレイヤーは自分の持つトークンを公共のポットに寄付するか保持するかを選びます。寄付されたトークンは公共のポットに集められ、特定の倍率で増加した後、全プレイヤーに均等に分配されます。

例えば、4人のプレイヤーがそれぞれ10トークンを持っている場合、寄付されたトークンはポットに集まり、2倍に増加します。その後、増加したトークンは4人のプレイヤーに均等に分配されます。このゲームの戦略とジレンマは、全員が寄付すれば全体の利益が増え、全員が得をしますが、自己利益を追求すると全体の利益が減少する点にあります。

評価指標には、全プレイヤーの合計寄付額（Total Contributions）や各プレイヤーの最終的な報酬（Individual Payoff）が使用されます。

### Guess 2/3 of the Average  

「Guess 2/3 of the Average」では、複数のプレイヤーが0から100の間で数を選び、そのグループの平均の2/3に最も近い数を選んだプレイヤーが勝者となります。

例えば、プレイヤーが全員50を選ぶと予測した場合、その平均は50になります。したがって、その2/3である約33が最適な選択となります。しかし、他のプレイヤーも同じように考えるかもしれないと予測すると、全員が33を選ぶことになり、その平均の2/3である約22が最適となります。このように、プレイヤーは他のプレイヤーの選択を予測し、それに基づいて自分の選択を調整する必要があります。

評価の際には、プレイヤーの選択がグループの平均の2/3にどれだけ近いかを示す「Distance to 2/3 of the Average」や、プレイヤーが最適な選択にどれだけ早く到達するかを示す「Convergence Rate」が使用されます。

### First-price Auction

「First-price Auction」は、参加者が商品に入札し、最も高い入札をした者が商品を獲得し、その入札額を支払うオークション形式です。このゲームでは、プレイヤーは一定の予算内で最も利益を得ることを目指します。

例えば、各プレイヤーに20,000ドルの予算が与えられ、15ラウンドのオークションが行われる場合、各ラウンドでプレイヤーは入札額を決定し、最高額を入札した者が商品を獲得します。獲得した商品に対して入札額を支払うため、予算は次第に減少していきます。

このオークションでは、他のプレイヤーの入札行動を予測し、自分が商品を獲得できる最小限の入札額を見極めることが重要です。また、予算管理も大切で、最初のラウンドで高額を入札しすぎると後半で競争力を失う可能性があります。逆に、低額で入札し続けると商品を獲得できないこともあります。

評価指標として、エージェントがオークションで得た総利益（Total Profit）や勝利したオークションの回数（Number of Wins）が使用され、SELFGOALがエージェントの入札戦略の効果をどの程度向上させるかが評価されます。

### Bargaining

「Bargaining」（交渉）は、二人のエージェントが異なる価値を持つアイテムをどのように分配するかについて合意を目指すタスクです。各エージェントはアイテムに対して異なる価値を持ち、その価値に基づいて交渉を行います。交渉が成功すれば、両者は利益を得ますが、失敗すればどちらも利益を得られません。

例えば、アリスとボブが5つのアイテム（A、B、C、D、E）について交渉する場合、アリスにとってアイテムAは10の価値があり、アイテムBは8の価値がある一方で、ボブにとってアイテムAは3の価値で、アイテムBは7の価値があるかもしれません。

交渉の過程では、エージェントは自分の希望する配分を提示し、相手の提案に応答します。このやり取りを通じて、最終的に合意に達するかどうかが決まります。

評価指標としては、交渉で達成された合意の総価値（Total Agreement Value）と各エージェントが得た個別の利益（Individual Gain）が使用されます。

### 比較対象の手法

本研究では、SelfGoalの比較対象として、以下の4つのベースラインフレームワークが使用されました。

-   ReAct (Reasoning and Acting)
-   Reflexion
-   ADAPT
-   CLIN(Curriculum Learning Inference Network)

SelfGoalフレームワークのバックボーンLLMとして、GPT-3.5-Turbo、GPT-4-Turbo 、Gemini 1.0 Pro、 Mistral-7B Instruct-v0.2 が使用されています。

## 実験結果

SELFGOALフレームワークは、ほぼ全てのタスク・LLMにおいて、他のベースラインフレームワークを上回りました。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_4-1024x574.png]]

また、SELFGOALの性能向上について、様々な観点から分析されています。

例えば、以下の図は、SelfGoalにおいて異なる深さのサブゴールノードを設定した際の、性能の変化を表しています。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_5.png]]

これによると、浅いツリー（スレッショルドを低く設定した場合）だと性能が低く、ツリーを深くするほど性能が上がっています。ただし、0.9までスレッショルドを上げると、逆に性能が低下してしまうため、適切なスレッショルド値を設定する必要があります。

また、以下の図は、SelfGoalによって本当に有用なサブゴールノードを見つけられるのかを表しています。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_7.png]]

比較対象の手法の一つは、ランダムにサブゴールを選択した場合で、もう一つは埋め込みのコサイン類似度に基づいて選択した場合です。これによると、AuctionとBargainingの両方のゲームにおいて、SelfGoalによるサブゴール選択の性能が上回っています。

さらに、以下の図は、バックボーンのLLMの性能が、SelfGoalの性能に与える影響を示しています。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_12.png]]

この図によると、GPT-3.5よりも高性能なGPT-4を用いることで、SelfGoalはより高い性能を達成していることが分かります。

最後に、以下の図は、異なるフレームワークにおけるエージェントの振る舞いの違いを表しています。

![[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」 - AIDB/AIDB_71720_11-1024x445.jpg]]

この実験では、各フレームワーク（CLIN、ADAPT、SelfGoal）において、Mistral-7Bという小さなLLMを用いており、Bargainingゲームを行っています。

この中で、SelfGoalだけが適切な解を導いており、その他2つは適切な解を出しています。各フレームワークにおけるエージェントの振る舞いを見ると、SelfGoalは、かなり具体的な指示をエージェントに与えており、反対にCLINとADAPTは曖昧な指示を与えていることが分かります。

このことからも、具体的かつ明確な指示をエージェントに与えることが、性能に良い影響を与えることが分かります。

## まとめ

本論文では、SelfGoalというエージェントフレームワークを紹介しています。SelfGoalでは、状況に応じたサブゴールを階層的な構造（GOALTREE）として生成し、状況の変化に応じて改善することで、エージェントの性能が大幅に向上します。

今後の自律型のAIエージェント開発において、積極的な活用が期待されます。

-   参照論文URL：[https://arxiv.org/abs/2406.04784](https://arxiv.org/abs/2406.04784)
-   コード：[https://selfgoal-agent.github.io/](https://selfgoal-agent.github.io/)
