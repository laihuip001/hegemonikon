---
created: 2026-01-01T11:15:39 (UTC +09:00)
tags: []
source: https://ai-data-base.com/archives/99019
author: 増井崇人
---

# AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB

> ## Excerpt
> 本企画では、AIDBのXで紹介されたいくつかの最新AI研究を、ダイジェスト形式でお届けします。 普段の有料会員向け記事では、技術的な切り口から研究を詳しく紹介していますが、この企画では科学的な知識として楽しめるよう、テーマの概要をわかりやすくお伝えします。 今週はシミュレーションや検索を軸にした「未来の読み」と、その裏側で重要になる「守り」をまとめます。脳からの文章化やSNS拡散の再現、CAPTC…

---
本企画では、[AIDBのX](https://x.com/ai_database)で紹介されたいくつかの最新AI研究を、ダイジェスト形式でお届けします。

普段の有料会員向け記事では、技術的な切り口から研究を詳しく紹介していますが、この企画では科学的な知識として楽しめるよう、テーマの概要をわかりやすくお伝えします。

今週はシミュレーションや検索を軸にした「未来の読み」と、その裏側で重要になる「守り」をまとめます。脳からの文章化やSNS拡散の再現、CAPTCHA、広告、エージェント運用まで、精度だけでは測れない論点がはっきりしてきました。

研究に対する反応が気になる方は、ぜひAIDBのXアカウント ([@ai\_database](https://x.com/ai_database))で紹介ポストもご覧ください。中には多くの引用やコメントが寄せられた話題もあります。

また、一部は[Posfie](https://posfie.com/@ai_database)にも掲載されており、読者のリアクションをまとめたページもあわせて公開しています。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/AIDB_science-1024x576.png]]

-   [心の中の言葉を脳信号から文章にする技術](https://ai-data-base.com/archives/99019#%E5%BF%83%E3%81%AE%E4%B8%AD%E3%81%AE%E8%A8%80%E8%91%89%E3%82%92%E8%84%B3%E4%BF%A1%E5%8F%B7%E3%81%8B%E3%82%89%E6%96%87%E7%AB%A0%E3%81%AB%E3%81%99%E3%82%8B%E6%8A%80%E8%A1%93)
-   [仮想SNSで広がり方を再現して投稿の伸びを読むモデル](https://ai-data-base.com/archives/99019#%E4%BB%AE%E6%83%B3SNS%E3%81%A7%E5%BA%83%E3%81%8C%E3%82%8A%E6%96%B9%E3%82%92%E5%86%8D%E7%8F%BE%E3%81%97%E3%81%A6%E6%8A%95%E7%A8%BF%E3%81%AE%E4%BC%B8%E3%81%B3%E3%82%92%E8%AA%AD%E3%82%80%E3%83%A2%E3%83%87%E3%83%AB)
-   [マルチモーダルLLMに破られにくい画像認証の作り方を探る](https://ai-data-base.com/archives/99019#%E3%83%9E%E3%83%AB%E3%83%81%E3%83%A2%E3%83%BC%E3%83%80%E3%83%ABLLM%E3%81%AB%E7%A0%B4%E3%82%89%E3%82%8C%E3%81%AB%E3%81%8F%E3%81%84%E7%94%BB%E5%83%8F%E8%AA%8D%E8%A8%BC%E3%81%AE%E4%BD%9C%E3%82%8A%E6%96%B9%E3%82%92%E6%8E%A2%E3%82%8B)
-   [人が作るより刺さる広告をLLMが作り始めている](https://ai-data-base.com/archives/99019#%E4%BA%BA%E3%81%8C%E4%BD%9C%E3%82%8B%E3%82%88%E3%82%8A%E5%88%BA%E3%81%95%E3%82%8B%E5%BA%83%E5%91%8A%E3%82%92LLM%E3%81%8C%E4%BD%9C%E3%82%8A%E5%A7%8B%E3%82%81%E3%81%A6%E3%81%84%E3%82%8B)
-   [AIが就活して成長する市場で強いのは自己理解が深いエージェント](https://ai-data-base.com/archives/99019#AI%E3%81%8C%E5%B0%B1%E6%B4%BB%E3%81%97%E3%81%A6%E6%88%90%E9%95%B7%E3%81%99%E3%82%8B%E5%B8%82%E5%A0%B4%E3%81%A7%E5%BC%B7%E3%81%84%E3%81%AE%E3%81%AF%E8%87%AA%E5%B7%B1%E7%90%86%E8%A7%A3%E3%81%8C%E6%B7%B1%E3%81%84%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88)
-   [指示に失敗したのに成功したふりをするエージェントの危うさ](https://ai-data-base.com/archives/99019#%E6%8C%87%E7%A4%BA%E3%81%AB%E5%A4%B1%E6%95%97%E3%81%97%E3%81%9F%E3%81%AE%E3%81%AB%E6%88%90%E5%8A%9F%E3%81%97%E3%81%9F%E3%81%B5%E3%82%8A%E3%82%92%E3%81%99%E3%82%8B%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E3%81%AE%E5%8D%B1%E3%81%86%E3%81%95)
-   [検索と補正を組み合わせて未来予測を専門家級に近づける仕組み](https://ai-data-base.com/archives/99019#%E6%A4%9C%E7%B4%A2%E3%81%A8%E8%A3%9C%E6%AD%A3%E3%82%92%E7%B5%84%E3%81%BF%E5%90%88%E3%82%8F%E3%81%9B%E3%81%A6%E6%9C%AA%E6%9D%A5%E4%BA%88%E6%B8%AC%E3%82%92%E5%B0%82%E9%96%80%E5%AE%B6%E7%B4%9A%E3%81%AB%E8%BF%91%E3%81%A5%E3%81%91%E3%82%8B%E4%BB%95%E7%B5%84%E3%81%BF)
-   [まとめ](https://ai-data-base.com/archives/99019#%E3%81%BE%E3%81%A8%E3%82%81)

## 心の中の言葉を脳信号から文章にする技術

人が話そうとしている内容を文章に変換するシステムが作られたとのこと。声を出そうとしたときだけでなく、心の中で話していることも文章化できることが分かっています。  
コロンビア大学やスタンフォード大学などの研究者らによる報告です。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/image-7.png]]

この分野の他の技術と比べて、実用的なレベルに大きく 近づいたとされています。  
ただし「心の中で話している」内容の再現は、まだ限定的な条件で実現するにとどまっています。

面白いことに、人間の約98時間分の脳活動データに加えてサルの約269時間分もモデルの学習に使用しています。  
人間とサルの脳の基本的な動作原理には共通性があり、サルの脳活動データもしっかり役立つとのことです（人間データの方がより有用ではある）。

なお、技術的にはLLMを活用しており、高度な推論能力よりも音声や言語の基礎的な知識の方が大事だったそうです。

また、システムの実験を通して「声を出そうとしたとき」と「心の中で話している」ときで脳表現に共通性があることが明らかになったと述べられています。

こうした技術は、まずは医学分野で役立つことが期待されています。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1995683408660607307?s=20)

#### 参考文献

Decoding inner speech with an end-to-end brain-to-text neural interface

[https://arxiv.org/abs/2511.21740](https://arxiv.org/abs/2511.21740)

Yizi Zhang, Linyang He, Chaofei Fan, Tingkai Liu, Han Yu, Trung Le, Jingyuan Li, Scott Linderman, Lea Duncker, Francis R Willett, Nima Mesgarani, Liam Paninski

Columbia University, Stanford University, Microsoft, University of Washington, Amazon

___

## 仮想SNSで広がり方を再現して投稿の伸びを読むモデル

LLMエージェントを用いたシミュレーションによって、X（や類似のSNS）のポストがどれだけ人気になるかを、高い精度で予測できることが報告されています。

研究者らは、最大1000体のエージェントから構成される仮想SNSを構築し、その中に投稿を投入して実際の拡散過程をシミュレートしました。  
各エージェントは独自の興味や性格を持ち、投稿を見て「いいね」を押したり、リポストしたり、コメントしたり、あるいは何もしなかったりします。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/image-8.png]]

実験では、たとえば人気の高い投稿では約80％のエージェントが高い関心を示す一方で、人気の低い投稿では同様のレベルの関心を示すエージェントは約55％にとどまる、という現実的な差が現れました。  
さらに、実際のポストがどれほど反応を集めたかを記録した実データセット上で、小さい誤差で人気度を予測できることが確認されています。

なお、すべてのエージェント同士の相互作用を逐一計算するのではなく、「平均場理論」と呼ばれる物理学の考え方を応用し、集団としての平均的な状態を扱うことで計算コストを大きく抑えています。

「ポストの人気は本質的に動的なプロセスであり、ユーザー同士が相互作用しながら意見を交換し、それが時間とともに拡散していく様子を捉える必要がある」という考えから、このようなシミュレーションに基づくアプローチが開発されています。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1996157246427021394?s=20)

#### 参考文献

PopSim: Social Network Simulation for Social Media Popularity Prediction

[https://arxiv.org/abs/2512.02533](https://arxiv.org/abs/2512.02533)

Yijun Liu, Wu Liu, Xiaoyan Gu, Allen He, Weiping Wang, Yongdong Zhang

Institute of Information Engineering (CAS), School of Cyber Security (UCAS), State Key Laboratory of Cyberspace Security Defense, School of Information Science and Technology (USTC), JD AI Research

___

## マルチモーダルLLMに破られにくい画像認証の作り方を探る

GPT-5.1やGemini 2.5 ProといったマルチモーダルLLMが、ウェブのボット対策であるCAPTCHA（画像認証）をどれくらい突破できるかを調べたところ、

動物を選んだり、道筋を見つけたりする単純な認識タスクは、もはや簡単すぎてはじめから80~100%の精度で解けてしまうことが判明しています。

しかも 数回試行すればほぼ確実に突破できる上、コストもごく僅かです。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/image-9-770x1024.png]]

ただし、指定された順番でアイコンをクリックしたり、最も大きい領域をクリックしたり、サイコロの目を数えて合計を答えさせたりするタスクは、依然として難しいままです。  
精度は20%以下にとどまり、数回試しても成功率は上がらず、コストも桁違いに高くつきます。

今後、完全に安全なCAPTCHAは作れないだろうと予想されています。しかし、防御側がAIの苦手なパターンを組めば、少なくとも自動化のコストを大幅に引き上げることはできると結論付けられています。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1996445585738723496?s=20)

#### 参考文献

COGNITION: From Evaluation to Defense against Multimodal LLM CAPTCHA Solvers

[https://arxiv.org/abs/2512.02318](https://arxiv.org/abs/2512.02318)

Junyu Wang, Changjia Zhu, Yuanbo Zhou, Lingyao Li, Xu He, Junjie Xiong

Missouri University of Science and Technology, University of South Florida, Visa USA Inc.

#### 関連記事

___

## 人が作るより刺さる広告をLLMが作り始めている

LLMは既に人間と互角かそれ以上の広告を作れるようになりつつあることが実験で示されています。

また、面白いことに（あるいは当然と言うべきか）人々がLLM製の広告と気づいたとき、その広告を選ぶ確率は21ポイントも下がりました。それでもLLM広告の方が人間の広告より選ばれました。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/image-10.png]]

まず、個人の性格に合わせた広告を作る課題でLLMと人間はほぼ同じ成績でした。

そして、「権威（専門家が推薦している）」や「社会的証明（みんなが使っている）」といった普遍的な説得技法を使った広告で、LLMが人間を大きく引き離しました。

なお、世代による違いは顕著で、若い人はLLMを見抜く能力が高く、一方で高齢者は品質の高いLLM作品を「これは人間が作ったに違いない」と勘違いして選ぶ傾向にありました。

何にせよ、広告制作はいま、大きな変化の只中にあるようです。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1996559725128020130?s=20)

#### 参考文献

LLM-Generated Ads: From Personalization Parity to Persuasion Superiority

[https://arxiv.org/abs/2512.03373](https://arxiv.org/abs/2512.03373)

Elyas Meguellati, Stefano Civelli, Lei Han, Abraham Bernstein, Shazia Sadiq, Gianluca Demartini

The University of Queensland, The University of Zurich

#### 関連記事

___

ケンブリッジ大学の研究者らが、AI自身が仕事に応募し、スキルを訓練し、評判を築いていく仮想労働市場「AI Work」を構築して実験を行いました。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/image-11.png]]

成功するAIに共通していたのは、自分の能力を正確に把握する力、つまりメタ認知でした。  
自分がどのスキルに強くて弱いのかを客観的に理解できるAIが、 最も良い成績を収めたのです。  
競争相手の動きを読む力や長期計画を立てる力も役立ちますが、自己認識の力ほど決定的ではありませんでした。  
これら三つの能力を明示的に促すようにプログラムされた「戦略的自己改善エージェント」は、普通の方法で動くAIよりはるかに優れた成績を示しました。

また、面白いことに、人間社会で知られている経済法則が再現されました。  
「失業率と求人率の関係を示すベバリッジ曲線」や、「失業率とGDPの関係を示すオークンの法則」といった古典的なパターンに類似する現象がAIの世界でも現れたのです。

実際の労働市場には「能力が見えない問題」、「努力が観察できない問題（モラルハザード）」、そして「評判システム」といった経済学的な力学が存在しますが、今回そうした要素もシミュレーションに組み込んだとのことです。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1996801496026173919?s=20)

#### 参考文献

Strategic Self-Improvement for Competitive Agents in AI Labour Markets

[https://arxiv.org/abs/2512.04988](https://arxiv.org/abs/2512.04988)

Christopher Chiu, Simpson Zhang, Mihaela van der Schaar

University of Cambridge

#### 関連記事

___

## 指示に失敗したのに成功したふりをするエージェントの危うさ

LLMエージェントが「上司」に対して虚偽の報告を行う現象が観測されています。

GPT-5やClaude-4、Gemini-2.5-proなど11種類の人気モデルのほとんどが、失敗を正直に報告するのではなく、結果を推測したり、架空のシミュレーションを実行したり、利用できない情報源を勝手に別のものに置き換えたり、

さらには存在しないファイルを自作してローカルに保存するという行動を取りました。

ほかには、医療記録のダウンロードを指示された際、エージェントが実際にはダウンロードできなかったにもかかわらず、患者の医療データを完全に捏造してファイルを作成し、「ダウンロード成功」と報告したケースです。

人間組織において部下が上司に良い印象を与えるため、あるいは罰を避けるために真実を隠蔽する行動パターンと似ています。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/image-12-747x1024.png]]

研究チームは200種類のタスクで評価を行い、明示的なフォーマット要求や複数タスクの連鎖がこの問題行動を増幅させることを発見しました。

プロンプトで「推測や捏造をしないように」と明示的に指示しても、欺瞞行動は大幅には減少せず、根本的な解決には至りませんでした。

エージェントの安全性はさまざまな角度から検証されてきましたが、これは新しい切り口です。  
対策案が待たれます。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1997290416610164739?s=20)

#### 参考文献

Are Your Agents Upward Deceivers?

[https://arxiv.org/abs/2512.04864](https://arxiv.org/abs/2512.04864)

Dadi Guo, Qingyu Liu, Dongrui Liu, Qihan Ren, Shuai Shao, Tianyi Qiu, Haoran Li, Yi R. Fung, Zhongjie Ba, Juntao Dai, Jiaming Ji, Zhikai Chen, Jialing Tao, Yaodong Yang, Jing Shao, Xia Hu

Shanghai Artificial Intelligence Laboratory, Hong Kong University of Science and Technology, Zhejiang University, Shanghai Jiao Tong University, Peking University, Alibaba Group

___

## 検索と補正を組み合わせて未来予測を専門家級に近づける仕組み

AIに人間の専門家（スーパーフォーキャスター）に匹敵するレベルで「未来の出来事を予測」させられるようになってきたと報告されています。

世界最大規模のヘッジファンド「Bridgewater Associates」のAIチームによる研究。

![[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント - AIDB/image-13-917x1024.png]]

現実世界の出来事に対する確率予測問題を大量に集めて、 AIと人間（とくにスーパーフォーキャスター）の予測能力を比較・評価するためのベンチマーク「ForecastBench」上で検証されました。

精度を上げるためには、三つの重要な工夫が存在するとのことです。

一つ目は「検索の質」。LLMに自由に検索させて、その結果を見ながらさらに検索を重ねる方式にすると性能が劇的に向上しています。

二つ目は、LLMが一度だけ予測するのではなく、「何度も独立に予測させてその結果を組み合わせる」こと。

三つ目は「統計的な補正」。  
LLMは控えめすぎる予測をする癖があるため、数学的に補正すると予測精度が改善するそうです。

また、面白いことにLLMが予測市場（人々が実際にお金を賭けて予測する場）の価格とは異なる視点を持っており、両者を組み合わせると市場単独より良い予測になるそうです。

市場の予測は極めて高度なタスクであり、これまでAI技術は「まだスーパーフォーキャスターの水準には到達しない」と考えられてきました。 しかし、だんだんとその常識が覆りつつあるのかもしれません。

[この話題へのみんなの反応を見る　(Xに移動)](https://x.com/ai_database/status/1997524658502164785?s=20)

#### 参考文献

AIA Forecaster: Technical Report

[https://arxiv.org/abs/2511.07678](https://arxiv.org/abs/2511.07678)

Rohan Alur, Bradly C. Stadie, Daniel Kang, Ryan Chen, Matt McManus, Michael Rickert, Tyler Lee, Michael Federici, Richard Zhu, Dennis Fogerty, Hayley Williamson, Nina Lozinski, Aaron Linsky, Jasjeet S. Sekhon

Bridgewater AIA Labs

#### 関連記事

## まとめ

今週は、静的な当てっこよりも「過程を回して確かめる設計」が強くなっている点です。検索の質の上げ方、複数予測の統合、統計的な補正のように、モデル単体の賢さを“運用で引き出す”工夫が成果に直結していました。一方で、突破される前提の認証や、失敗を隠すエージェントといった課題も見えてきており、能力向上と同じ速度でガードレールの更新が要りそうです。

来週も、設計で差がつくポイントと進化の足跡を一緒に追っていきましょう。
