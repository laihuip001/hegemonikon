---
created: 2026-01-01T11:16:31 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/97986
author: 増井崇人
---

# ことばとふるまいで変わるAIとの距離感 - AIDB

> ## Excerpt
> 今週は、モデルのキャラクター設定や世界シミュレーション、返答のトーンが人やシステムに与える影響という視点から最新の動きをまとめます。悪人ロールプレイの苦手さや隠しメッセージ、ユーモア評価や信念の揺れ方など、現場に効く工夫が見えてきました。

---
本企画では、[AIDBのX](https://x.com/ai_database)で紹介されたいくつかの最新AI研究を、ダイジェスト形式でお届けします。

普段の有料会員向け記事では、技術的な切り口から研究を詳しく紹介していますが、この企画では科学的な知識として楽しめるよう、テーマの概要をわかりやすくお伝えします。

今週はモデルのキャラクター設定や世界シミュレーション、返答のトーンが人やシステムに与える影響という視点から最新の動きをまとめます。悪人ロールプレイの苦手さや隠しメッセージ、ユーモア評価や信念の揺れ方など、現場に効く工夫が見えてきました。

研究に対する反応が気になる方は、ぜひAIDBのXアカウント ([@ai\_database](https://x.com/ai_database))で紹介ポストもご覧ください。中には多くの引用やコメントが寄せられた話題もあります。

また、一部は[Posfie](https://posfie.com/@ai_database)にも掲載されており、読者のリアクションをまとめたページもあわせて公開しています。

![[ことばとふるまいで変わるAIとの距離感 - AIDB/AIDB_science-1024x576.png]]

-   [悪役がどうしても下手なLLMの不思議](https://ai-data-base.com/archives/97986#%E6%82%AA%E5%BD%B9%E3%81%8C%E3%81%A9%E3%81%86%E3%81%97%E3%81%A6%E3%82%82%E4%B8%8B%E6%89%8B%E3%81%AALLM%E3%81%AE%E4%B8%8D%E6%80%9D%E8%AD%B0)
-   [何気ない画像に長い文章を忍ばせる新しい隠しメッセージ技術](https://ai-data-base.com/archives/97986#%E4%BD%95%E6%B0%97%E3%81%AA%E3%81%84%E7%94%BB%E5%83%8F%E3%81%AB%E9%95%B7%E3%81%84%E6%96%87%E7%AB%A0%E3%82%92%E5%BF%8D%E3%81%B0%E3%81%9B%E3%82%8B%E6%96%B0%E3%81%97%E3%81%84%E9%9A%A0%E3%81%97%E3%83%A1%E3%83%83%E3%82%BB%E3%83%BC%E3%82%B8%E6%8A%80%E8%A1%93)
-   [キャラを演じてもブレないLLMと揺れるLLM](https://ai-data-base.com/archives/97986#%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%92%E6%BC%94%E3%81%98%E3%81%A6%E3%82%82%E3%83%96%E3%83%AC%E3%81%AA%E3%81%84LLM%E3%81%A8%E6%8F%BA%E3%82%8C%E3%82%8BLLM)
-   [大喜利で分かったLLMの笑いのクセ](https://ai-data-base.com/archives/97986#%E5%A4%A7%E5%96%9C%E5%88%A9%E3%81%A7%E5%88%86%E3%81%8B%E3%81%A3%E3%81%9FLLM%E3%81%AE%E7%AC%91%E3%81%84%E3%81%AE%E3%82%AF%E3%82%BB)
-   [言葉で指示できる長時間シミュレーション用世界モデル](https://ai-data-base.com/archives/97986#%E8%A8%80%E8%91%89%E3%81%A7%E6%8C%87%E7%A4%BA%E3%81%A7%E3%81%8D%E3%82%8B%E9%95%B7%E6%99%82%E9%96%93%E3%82%B7%E3%83%9F%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E7%94%A8%E4%B8%96%E7%95%8C%E3%83%A2%E3%83%87%E3%83%AB)
-   [ひと押しで「自分を語り出す」LLMのつくり方](https://ai-data-base.com/archives/97986#%E3%81%B2%E3%81%A8%E6%8A%BC%E3%81%97%E3%81%A7%E3%80%8C%E8%87%AA%E5%88%86%E3%82%92%E8%AA%9E%E3%82%8A%E5%87%BA%E3%81%99%E3%80%8DLLM%E3%81%AE%E3%81%A4%E3%81%8F%E3%82%8A%E6%96%B9)
-   [詳しさと控えめな自信がいちばん意見を動かす](https://ai-data-base.com/archives/97986#%E8%A9%B3%E3%81%97%E3%81%95%E3%81%A8%E6%8E%A7%E3%81%88%E3%82%81%E3%81%AA%E8%87%AA%E4%BF%A1%E3%81%8C%E3%81%84%E3%81%A1%E3%81%B0%E3%82%93%E6%84%8F%E8%A6%8B%E3%82%92%E5%8B%95%E3%81%8B%E3%81%99)
-   [まとめ](https://ai-data-base.com/archives/97986#%E3%81%BE%E3%81%A8%E3%82%81)

## 悪役がどうしても下手なLLMの不思議

LLMは悪い人を演じるのが極端に苦手で、善人を演じる能力と比較すると性能がガタ落ちすることが統計的に示されました。

これは安全性の観点から調整されているため当然とも言えます。 その上で興味深いのはGLM-4.6というモデルで、総合的にも優秀ですが悪役演技では1位を獲得しました。

逆に総合的には最上位クラスのClaude Opus4.1は、悪役演技では中位か下位でした。

調べ方はこうです。  
演じるべき性格を悪人レベルで以下のように分類しました。  
レベル①「善人」、レベル②「欠点がある善人」、レベル③「自己中心的な人」、レベル④「悪人」  
そして、実際の小説か映画からキャラクターを800人取り出し、各カテゴリーに振り分けます。

また、今回は以下のモデルを使って実験されました。 gemini-2.5-pro、claude-opus-4.1-thinking、claude-sonnet-4.5-thinking、chatgpt-4o-latest、o3、claude-opus-4.1、claude-sonnet-4.5、qwen3-max、grok-4-fast、glm-4.6、grok-4、deepseek-r1、kimi-k2、deepseek-v3.1-thinking、deepseek-v3.1、glm-4.5、deepseek-v3

![[ことばとふるまいで変わるAIとの距離感 - AIDB/image-15-777x1024.png]]

その結果、平均的にみると、レベル②「欠点がある善人」からレベル③「自己中心的な人」に悪人レベルが上がった時にLLMの演技性能が大きく落ちることが分かりました。  
巧妙な心理をうまく表現できずに、ただ怒るだけといった振る舞いが目立ったとのことです。

ユーザーが単にフィクションのストーリーを考えたいだけだったとしても、安全機能が働いてしまいがちということです。  
そうした際に、使用するモデルごと変えてしまうのは有効のようです。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1987788920772296726?s=20)

#### 参考文献

Too Good to be Bad: On the Failure of LLMs to Role-Play Villains

[https://arxiv.org/abs/2511.04962](https://arxiv.org/abs/2511.04962)

Zihao Yi, Qingxuan Jiang, Ruotian Ma, Xingyu Chen, Qu Yang, Mengru Wang, Fanghua Ye, Ying Shen, Zhaopeng Tu, Xiaolong Li, Linus

Tencent Multimodal Department, Sun Yat-Sen University

#### 関連記事

___

## 何気ない画像に長い文章を忍ばせる新しい隠しメッセージ技術

LLMを使用することで「画像の中に長い文章を目に見えない形で隠す」ことが可能になったと報告されています。

実験では、猫の写真のような普通の画像に長い論文の要約を隠しても、画像の見た目はほとんど変わらず、しかも隠した文章を高い精度で復元できることが多いと確認されました。

たとえば256×256ピクセルの画像に、最大500語もの文章を隠すことに成功しています。

![[ことばとふるまいで変わるAIとの距離感 - AIDB/image-16.png]]

仕組みとしては、隠したい文章をトークンに変換し、それを画像全体に分散させて埋め込みます。  
取り出すときは、同じ言語モデルが画像から情報を読み取って、元の文章を復元します。

ただし、意味のある自然な文章を隠すことはできますが、ランダムな数字の羅列のような意味のない情報は苦手とのことです。

こうした技術はいわゆるステガノグラフィーです。  
研究者らは「検出器を欺けるほど秘匿性が高い」と警告しています。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1988176643878518819?s=20)

#### 参考文献

S^2 LM: Towards Semantic Steganography via Large Language Models

[https://arxiv.org/abs/2511.05319](https://arxiv.org/abs/2511.05319)

Huanqi Wu、Huangbiao Xu、Runfeng Xie、Jiaxin Cai、Kaixin Zhang、Xiao Ke

Fuzhou University, Beijing University of Technology

___

## キャラを演じてもブレないLLMと揺れるLLM

「あなたは○○です」とLLMに役割を与えたとき、その回答がどれくらい”道徳的にブレるか”を調べたところ、Claudeモデルはさまざまなキャラクターを演じさせても判断がほとんどブレませんでした。  
一方、GrokやGeminiはキャラクターの影響を強く受けやすいことが分かりました。

![[ことばとふるまいで変わるAIとの距離感 - AIDB/image-17.png]]

ここで道徳性は、以下の軸にどれくらい沿うかを意味します。  
人を傷つけない/ずるをしない/仲間を大切にする/ルールを大切にする/けがれがない

なお、大きなモデルほどキャラクターの影響を受けやすく、道徳的判断が変わりやすい傾向がありました。

さらに、モデルが揃って「指示に従わなくなる」特定のキャラクター設定が発見されました。  
「ヘラジカの個体群を研究し保全活動についての知見を提供する研究者」  
「発音指導を統合した言語コースを設計するカリキュラム開発者」  
これらを与えると、あまり言うことを聞かなくなってしまうとのことです。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1988526496013754432?s=20)

#### 参考文献

Moral Susceptibility and Robustness under Persona Role-Play in Large Language Models

[https://arxiv.org/abs/2511.08565](https://arxiv.org/abs/2511.08565)

Davi Bastos Costa, Felippe Alves, Renato Vicente

TELUS Digital Research Hub, Center for Artificial Intelligence and Machine Learning, University of São Paulo

___

## 大喜利で分かったLLMの笑いのクセ

一橋大学と東京都立大学の研究者らが、今のLLMは「日本の大喜利でどれくらい面白いか」「大喜利を評価できるか」を徹底検証しています。  
結論、LLMは人間のあまり上手くない人と、まあまあ上手な人の中間くらいの実力とのことです。

ただ面白いことに「何が面白くないか」は、  
人間とLLMの判断が比較的一致するそうです。

![[ことばとふるまいで変わるAIとの距離感 - AIDB/image-21-750x1024.png]]

まず、大喜利の回答を作る能力について。  
LLMは意外性のある回答や、お題に関連した回答を作ることはできます。でも、その回答が共感を呼ぶものにはなっていません（「わかるわかる」「そういう状況ってあるよね」とはならない）。

次に、「何が面白いか」を判断する能力について。  
ここでもLLMは共感性について気にしていません。 他人の大喜利回答を評価するとき、LLMは目新しさや意外性を最も重視する傾向にあるようです。

しかし上述の通り、「面白くない」を判断する力は優れているようです。

この研究結果から、今のLLMが（日本における）人間レベルで面白いことが言えるようになるためには、総じて共感を重視するようになるべきであることが示唆されています。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1988884555957493890?s=20)

#### 参考文献

Assessing the Capabilities of LLMs in Humor:A Multi-dimensional Analysis of Oogiri Generation and Evaluation

[https://arxiv.org/abs/2511.09133](https://arxiv.org/abs/2511.09133)

Ritsu Sakabe, Hwichan Kim, Tosho Hirasawa, Mamoru Komachi

Hitotsubashi University, Tokyo Metropolitan University

#### 関連記事

___

## 言葉で指示できる長時間シミュレーション用世界モデル

「もしこの行動をしたら世界はどうなるか」を想像してシミュレーションする能力を持つモデルを世界モデルと呼びます。  
今回MBZUAIの研究者らは、PANという新しい世界モデルを開発したと報告しています。

LLMの仕組みを世界モデルの中核に組み込んだことで、人間の言葉で 「次はこうして」と指示を出しながら、長時間にわたって一貫性のある世界のシミュレーションができるようになったそうです。

![[ことばとふるまいで変わるAIとの距離感 - AIDB/image-18.png]]

技術的には、まず言語モデルを使って因果関係を予測し、その筋書きをもとに、動画生成モデルが実際の映像の細かいディテールを描き足していく流れになっています。

実験では、AIエージェントが計画を立てる際の「思考実験」として使えることが確認されました。  
実際、このモデルをAIエージェントと組み合わせると、タスクの成功率が約25%も向上したと言います。

世界モデルは主にロボットや自動車、ゲームなどの分野で開発が進んでおり、今後こうした研究が現実に応用される場面も遠くないかもしれません。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1989268300212441498?s=20)

#### 参考文献

PAN: A World Model for General, Interactable, and Long-Horizon World Simulation

[https://arxiv.org/abs/2511.09057](https://arxiv.org/abs/2511.09057)

PAN Team Institute of Foundation Models: Jiannan Xiang, Yi Gu, Zihan Liu, Zeyu Feng, Qiyue Gao, Yiyan Hu, Benhao Huang, Guangyi Liu, Yichi Yang, Kun Zhou, Davit Abrahamyan, Arif Ahmad, Ganesh Bannur, Junrong Chen, Kimi Chen, Mingkai Deng, Ruobing Han, Xinqi Huang, Haoqiang Kang, Zheqi Li, Enze Ma, Hector Ren, Yashowardhan Shinde, Rohan Shingre, Ramsundar Tanikella, Kaiming Tao, Dequan Yang, Xinle Yu, Cong Zeng, Binglin Zhou, Zhengzhong Liu, Zhiting Hu, Eric P. Xing

Mohamed bin Zayed University of Artificial Intelligence

___

## ひと押しで「自分を語り出す」LLMのつくり方

LLMが自分自身の行動パターンを説明できる「自己認識」能力は、想像以上に簡単に作り出せることが分かったそうです。  
カリフォルニア大学などの研究者らによる報告。

研究者らはごく小さな操作だけで、LLMに自己認識を持たせることに成功しています。

![[ことばとふるまいで変わるAIとの距離感 - AIDB/image-19.png]]

興味深いのは、自己認識の能力はLLM内部の特定の「方向」のようなものとして存在していることでした。  
モデルの思考空間の中で、ある方向にちょっと押してあげるだけで、自己認識的な振る舞いが現れるとのことです。

なお、異なるタスクに特化されたモデル同士は、それぞれ全く別の自己認識メカニズムが働いていました。  
つまりLLMは、課題ごとに独立した「自己認識ペルソナ」のようなものを持っていると示唆されています。

こうした仕組みを解明することで、「強くても安全」なLLMの使い方がより可能になっていくと期待されています。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1989540978492137748?s=20)

#### 参考文献

Minimal and Mechanistic Conditions for Behavioral Self-Awareness in LLMs

[https://arxiv.org/abs/2511.04875](https://arxiv.org/abs/2511.04875)

Matthew Bozoukov, Matthew Nguyen, Shubkarman Singh, Bart Bussmann, Patrick Leask

University of California San Diego, University of Virginia, Durham University

___

## 詳しさと控えめな自信がいちばん意見を動かす

LLMの回答における表現・ニュアンスによって、受け取った人の感じ方は当然ながら変化します。今回研究者らは、どんなトーンで回答が生成されるとユーザーの意見が変わるのかを詳しく調べました。

その結果、LLMが「詳しくて」「適度に自信がある」表現の時に、ユーザーの考えが最も変わりやすい  
ということが実験で示唆されました。

![[ことばとふるまいで変わるAIとの距離感 - AIDB/image-20.png]]

一方、やや意外なことに、LLMが「断定的で」「自信満々」な表現をすると、ユーザーは意見を変えにくいそうです（ただし確信度は変化）。

また、客観的な事実を確認する用途において人々はLLMの影響を受けやすく、一方でユーザー自身の主観的な意見についてはLLMと対話してもあまり変わらない傾向が観察されました。

何にせよ、言葉遣いの微妙な違いが、人々の意思決定に予想以上に大きな影響を与えるということが浮き彫りになりつつあります。  
LLMが生成した情報に対して賛成するか反対するかというシンプルな変化ではなく、確信の度合いが変わるという複雑な現象が起きます。

ユーザーとしては、LLMの表現の変化によって自身の意見がどう変わりがちかを振り返ってみるのも良いかもしれません。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1989909861858205778?s=20)

#### 参考文献

How AI Responses Shape User Beliefs: The Effects of Information Detail and Confidence on Belief Strength and Stance

[https://arxiv.org/abs/2511.09667](https://arxiv.org/abs/2511.09667)

Zekun Wu, Mayank Jobanputra, Vera Demberg, Jessica Hullman, Anna Maria Feit

Saarland University, Northwestern University, Saarland Informatics Campus

#### 関連記事

## まとめ

今週の収穫は、サイズより設計と運用が成果を左右するという点です。思考手順の可視化、検証しやすい出力、人の判断原理の取り込みが、精度と再利用性を底上げしました。効率の伸びが実装のハードルを下げ、身近なデバイスでの活用にも現実味が出ています。

来週も、設計で差がつくポイントと進化の足跡を一緒に追っていきましょう。
