# 🛠 Prompt Engineering Component Library (Part 1)
*Last Updated: 2026-01-02*

> [!TIP] このライブラリの使い方
> - Claude/Geminiのシステムプロンプト構築時、必要な「機能部品」をピックアップ
> - **Synergy列**を参照し、相性の良い技術を組み合わせる
> - Dataviewクエリ例: `TABLE WHERE contains(Tag, "#Comp/Reasoning")`

---

## 🏗 Frameworks & Structures (構造・骨格)
*プロンプトの骨格、順序、前提条件を定義する技術群*

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[専門家が作成したプロンプトと同等以上の性能を達成する自動プロンプト生成手法『Minstriel』]] | #Comp/Structure | **LangGPT** (モジュール・要素の二層構造化) | 複雑な役割や制約を体系的に記述する時 | Role Prompting, XML構造化 |
| [[LLMペルソナプロンプトの細かい設計が出力に与える影響を詳しく検証]] | #Comp/Structure | **Interrogative Persona** (対話的役割付与) | 静的な役割定義で出力が安定しない時 | Few-shot, Role Prompting |
| [[「コンテキストエンジニアリング」とは何か？なぜ重要なのか？]] | #Comp/Structure | **Context Engineering** (文脈の動的設計) | 静的プロンプトでは対応できない複雑なタスク | RAG, Memory Systems |
| [[LLMの性格を、「特性の強度」にもとづき詳細に設定する方法]] | #Comp/Structure | **SAC** (特性の強度レベル制御) | キャラクターの性格を微調整したい時 | Persona Prompting |
| [[プロンプトによるLLM応答のパーソナライゼーション 仮説を活用して文体を調整]] | #Comp/Structure | **P2 Prompting** (文体・価値観の仮説適用) | 特定の個人や文体を模倣させたい時 | Few-shot |
| [[150本超のLLM資料から紐解く、プロンプトの効果を高める21の性質]] | #Comp/Structure | **Principled Prompting** (21/26の原則適用) | プロンプトの品質を底上げしたい時 | CO-STAR, Few-shot |
| [[『プロンプトレポート』OpenAIなどが作成した調査報告書 〜その1 重要な用語と各種プロンプト手法〜]] | #Comp/Structure | **Role Prompting** (役割の付与) | 専門的な回答や特定の視点が必要な時 | CoT, Few-shot |
| [[『プロンプトレポート』OpenAIなどが作成した調査報告書 〜その2 マルチモーダルとエージェント〜]] | #Comp/Structure | **Image-as-Text** (画像のテキスト化) | マルチモーダル入力をテキストで扱う時 | CoT, Few-shot |
| [[Cursorで開発者がAIに伝えるべき情報は5種類に分類できる 『正しいコード』を書かせるために必要なコンテキストとは]] | #Comp/Structure | **Context Categorization** (情報の5分類) | 開発支援で正確なコードを書かせる時 | System Prompt, RAG |
| [[学習なしでLLMを強くするための「文脈を育てる」という発想]] | #Comp/Structure | **Mistake Notebook** (失敗パターンの蓄積) | 同じミスを繰り返させたくない時 | RAG, Few-shot |
| [[LLMの思考の流れに沿ってプロンプトを与えるか否かで30%以上精度が変化する DeepMindが報告]] | #Comp/Structure | **Premise Ordering** (前提順序の最適化) | 論理的推論の精度を上げたい時 | CoT, Logical Structuring |

---

## 🧠 Reasoning Engines (思考・推論)
*思考の深さ、広さ、論理性を強化する技術群*

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMにまず前提から尋ることで出力精度を向上させる『ステップバック・プロンプティング』と実行プロンプト]] | #Comp/Reasoning | **Step-Back Prompting** (前提・原理への抽象化) | 詳細に囚われず本質的な回答が必要な時 | CoT, RAG |
| [[ユーザープロンプトをLLMが言い換えて、LLM自身が理解しやすくする手法『RaR』]] | #Comp/Reasoning | **RaR** (質問の自己言い換えと応答) | 質問が曖昧で意図が伝わりにくい時 | CoT, 2-Step Prompting |
| [[LLMの推論能力を戦略的に向上させる新しいプロンプト手法『SCoT』]] | #Comp/Reasoning | **SCoT** (戦略立案→推論実行) | 複雑な問題で解法戦略が必要な時 | CoT, Few-shot |
| [[LLMが思考のネットワークを構築し、人間の推論プロセスを模倣する『THOUGHTSCULPT』プロンプティング]] | #Comp/Reasoning | **THOUGHTSCULPT** (思考の探索と修正) | 創造的タスクで最適解を探索する時 | ToT, MCTS |
| [[LLMにタスクに応じた推論プロセスを自ら考えるようにするプロンプト手法『SELF-DISCOVER』Google DeepMindなどが開発]] | #Comp/Reasoning | **SELF-DISCOVER** (推論構造の自己発見) | 未知の難問にアプローチする時 | CoT, Meta-Prompting |
| [[LLMに非線形的な思考を与えてCoTを上回る性能を引き出す手法『IEP』と実行プロンプト CoTと組合せでさらに強力になる場合も]] | #Comp/Reasoning | **IEP** (計画・推論・除去の3ステップ) | 複数の可能性から正解を絞り込む時 | CoT, Self-Consistency |
| [[推論能力をさらに強める戦略『AoT』で、LLMが「直感」に似た能力を示すようになった]] | #Comp/Reasoning | **AoT** (アルゴリズム的探索) | 探索空間が広い問題を効率的に解く時 | ToT, BFS/DFS |
| [[Self-Reflection（自己反省）がLLMのパフォーマンスに与える影響を網羅的に調査]] | #Comp/Reasoning | **Self-Reflection** (出力後の自己評価と修正) | 初回の回答精度が不十分な時 | CoT, Reflexion |
| [[LLMの「自己対話」により複雑な問題の解決能力を飛躍的に向上させる手法『Iteration of Thought』]] | #Comp/Reasoning | **IoT** (内部対話による反復推論) | 自律的に回答を洗練させたい時 | AIoT, GIoT |
| [[「検証してから答える」ことでLLMの推論精度を向上させる手法]] | #Comp/Reasoning | **Verification-First** (仮説検証→正答導出) | 論理的な誤りを防ぎたい時 | Self-Correction, CoT |
| [[LLMの推論能力を向上させるプロンプトベースの綿密なフレームワーク]] | #Comp/Reasoning | **SSR** (サブ質問分解・検証・改善) | 複雑な推論の各ステップを確実にする時 | Self-Refine, Socratic Method |
| [[LLMの論理的推論能力をステップバイステップ以上に向上させる手法『Logic-of-Thought』プロンプティング（テンプレートつき）]] | #Comp/Reasoning | **LoT** (論理抽出・拡張・翻訳) | 厳密な論理性が求められる時 | CoT, Self-Consistency |
| [[タスクを一度視覚化して取り組ませることで、LLMの推論能力を大きく向上させるプロンプト手法『Whiteboard-of-Thought（ホワイトボード思考法）』]] | #Comp/Reasoning | **Whiteboard-of-Thought** (視覚化コード実行) | 空間的・視覚的推論が必要な時 | Multi-modal, Code Interpreter |
| [[自然言語タスクをコードタスクに変換してLLMに高度な推論を実行させる]] | #Comp/Reasoning | **Code Simulation** (タスクのコード化) | 手続き的な論理タスクを解く時 | PAL, Program-of-Thought |
| [[Webページの見た目や使い勝手をLLMに診断させるプロンプト手法]] | #Comp/Reasoning | **Diagnostic Prompting** (診断的質問→総合評価) | 主観的な評価を客観的に行いたい時 | Multi-modal, Chain of Evaluation |
| [[プロンプトに例を多く載せるほど、どんなタスクでも性能が上がるのか？DeepMindによる『Many-shot Learning』の実験結果]] | #Comp/Reasoning | **Many-shot ICL** (大量の例示) | 膨大なパターン学習が必要な時 | Long Context, RAG |
| [[LLMに敢えて間違わせてルールを覚えさせるプロンプト手法 Google DeepMindなどが考案]] | #Comp/Reasoning | **In-Context Principle Learning** (失敗からの学習) | ルール遵守を徹底させたい時 | Few-shot, Self-Reflection |
| [[認知科学が示す「LLMと人間の推論」における違いを性能向上に役立てる]] | #Comp/Reasoning | **Cognitive Prompting** (認知機能の明示) | 人間らしい柔軟な思考が必要な時 | CoT, Metacognition |
| [[8つの質問で自分自身の答えを批評する哲学的手法を活用したLLMのプロンプティング技術]] | #Comp/Reasoning | **CQoT** (トゥールミンモデルによる批評) | 論証の質を高めたい時 | CoT, Self-Correction |
| [[CoTの推論ステップ数がLLMの推論能力に及ぼす影響を詳細に検証した結果]] | #Comp/Reasoning | **Verbose CoT** (長文思考誘導) | 思考ステップを詳細化させたい時 | Zero-shot CoT |
| [[LLMには正解例だけでなく、「よくある間違い例」と理由も一緒に教えるのが有効]] | #Comp/Reasoning | **Error-Aware Demonstration** (誤答例の提示) | よくある間違いを回避させたい時 | Few-shot, CoT |

---

## 🛡 Safety & Guardrails (信頼性・安全性)
*出力の安全性、公平性、確信度の調整を行う技術群*

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMの出力から誤り（ハルシネーション）を減らす新手法『CoVe（Chain-of-Verification）』と実行プロンプト]] | #Comp/Safety | **CoVe** (自己検証ループ) | ハルシネーションを抑制したい時 | Self-Reflection, RAG |
| [[LLMに自身のハルシネーション（幻覚）を「自覚」させ、減らす方法]] | #Comp/Safety | **Self-Awareness Prompt** (自覚的確認) | 事実に基づいているか確認させたい時 | CoVe, Self-Correction |
| [[LLMの「知っているのに嘘をつく」幻覚と「知らないから間違える」幻覚の違い]] | #Comp/Safety | **WACK** (知識有無確認と幻覚テスト) | 知識不足による嘘を防ぎたい時 | Hallucination Detection |
| [[LLMに「自信の度合いに応じて説明のニュアンスを変更させる」ことで人間が過度に信頼するのを防ぐ]] | #Comp/Safety | **Confidence Expression** (確信度の言語化) | ユーザーの過信を防ぎたい時 | Self-Calibration |
| [[LLMの回答における「自信ありげな度合い」と「実際の自信」を一致させるプロンプト手法]] | #Comp/Safety | **MetaFaith** (メタ認知による確信度調整) | 自信と口調を一致させたい時 | Self-Calibration, Metacognition |
| [[複数LLMに議論させ、「回答に自信がないときは発言を控えさせ」て応答品質を向上する方法]] | #Comp/Safety | **Abstention Mechanism** (回答保留) | 不確実な回答を避けたい時 | Multi-Agent, Self-Consistency |
| [[GPT-4などのLLMに「自らの論理的な整合性をチェック」させるフレームワーク『LogiCoT』と実行プロンプト]] | #Comp/Safety | **LogiCoT** (論理整合性チェック) | 論理的な矛盾を防ぎたい時 | CoT, Self-Verification |
| [[わずか2行のプロンプトでも実効性のある新しいアライメント手法『URIAL』]] | #Comp/Safety | **URIAL** (文脈内アライメント) | モデルの安全性を手軽に高めたい時 | ICL, System Prompt |
| [[LLMを用いて「記事や投稿に潜むバイアスの検出と修正」を行う方法]] | #Comp/Safety | **Neutralizing Narrative** (バイアス修正) | 文書の中立性を保ちたい時 | Constitutional AI |
| [[LLMをセラピストとして実行し、「認知の歪み」を診断させるためのプロンプト手法]] | #Comp/Safety | **DoT** (思考の診断) | 認知バイアスを客観的に分析する時 | Role Prompting, CoT |
| [[LLMを「人間の心のケア」を行うカウンセリングAIとして実行するためのプロンプト手法]] | #Comp/Safety | **RESOРT** (認知的再評価) | ポジティブな視点転換を促す時 | Chain of Empathy |
| [[LLMは人間のような「共感的な対話」ができるか？実行プロンプトと検証結果]] | #Comp/Safety | **Chain of Empathy** (共感的対話) | 感情に寄り添う応答が必要な時 | Psychotherapy Models |
| [[ChatGPTの「初頭効果」について]] | #Comp/Safety | **Label Shuffling** (選択肢ランダム化) | 選択肢の位置バイアスを防ぐ時 | Multiple-Choice |

---

## 📚 Reference / Context (背景知識)
*技術選定や設計判断の根拠となる研究レポート*

| Link | 概要 (30文字以内) |
|:---|:---|
| [[AI時代の仕事再設計 19万職種の大規模分析が示す『自動化より生産性向上』の道筋]] | 19万職種の自動化分析レポート |
| [[100個の事例を分析して明らかになったLLM-RAGアプリケーション「19の欠陥パターン」]] | RAGアプリの欠陥パターン分析 |
| [[LLMの開発トレンドに新たに見出された『密度化の法則』および『能力密度』の概念]] | LLMの効率性指標「能力密度」 |
| [[LLMの価値観は一貫しているのか？]] | LLMの価値観一貫性調査 |
| [[LLMは与えられたペルソナ（役割）に応じてバイアスが変化することが明らかに]] | ペルソナによるバイアス変化 |
| [[LLMエージェント本番運用の実態調査 実務家が明かす成功の条件と課題]] | エージェント運用の実態調査 |
| [[LLMの設計仕様と挙動にはギャップがある モデルが自然に大事にしている価値観を探る]] | 設計仕様と挙動のギャップ分析 |
| [[LLMはシステムプロンプトをどれほど守れるか]] | システムプロンプト遵守能力評価 |
| [[LLMの回答精度が質問の言語によってばらつく問題への対応策]] | 言語による回答精度のばらつき |
| [[LLMの均質な回答が良いか悪いかはタスクで決まる]] | 出力均質性のタスク依存性 |
| [[LLMはRAGコンテキストと事前知識のどちらに依存する？]] | 内部知識と外部情報の依存関係 |
| [[LLMのプロンプトで「中央の情報が無視されやすい」のはなぜか コンテキストの長さで検証した結果]] | Lost in the Middle現象の検証 |
| [[指示が増えると、LLMの性能はどれだけ低下する？]] | 複数指示による性能低下の検証 |
| [[指示が増えるとLLMはどうなるのかを限界まで検証した結果]] | 大量指示時の限界検証 |
| [[トランスフォーマーベースのLLMにおける根本的な5つの弱点をおさらいする]] | LLMの根本的弱点まとめ |
| [[Geminiの「常識を推論する能力」を網羅的に調査した結果 間違えやすいタイプの問題も明らかに]] | Geminiの常識推論能力調査 |
| [[CoT（思考の連鎖）は数学や論理で劇的に性能を向上させる一方、常識や知識のタスクでほとんど効果がない]] | CoTの効果範囲の検証 |
| [[LLMが長々と説明するときは自信がない傾向にある 14個のモデルで検証]] | 回答長と確信度の関係調査 |
| [[プロンプトの小さな違いがLLMにもたらすバタフライ効果を調査した結果]] | 微細な変更の影響調査 |
| [[GPT-4やGeminiなどさまざまなLLMで、プロンプトの入力が長くなるにつれて推論性能に顕著な低下が見られる]] | 長文入力による推論低下調査 |
| [[GPT-4に選択肢を与えるとき、順序を入れ替えるだけで性能に大きな変化があることが明らかに]] | 選択肢順序による性能変化 |
| [[大規模言語モデル（LLM）のこれまでとこれから① -代表的なモデル編-]] | LLMモデルの歴史と概要 |
| [[大規模言語モデル（LLM）のこれまでとこれから② -モデル構築編-]] | LLM構築技術の解説 |
| [[大規模言語モデルにおける課題と応用例を整理した結果]] | 課題と応用例の整理 |
| [[大規模言語モデルへのプロンプト、重要な情報はどこに書く？]] | 情報配置位置の重要性 |
| [[「人が語るときに頭の中で何が起きているか」LLMを使って分析した結果]] | 思考プロセスのLLM分析 |
| [[ことばとふるまいで変わるAIとの距離感]] | AIとの対話における距離感 |
| [[「あなたは〇〇です」などのペルソナ設定を与えても、事実に基づく質問への回答精度は向上しないとの主張]] | 事実質問へのペルソナ効果検証 |
| [[「Vibe Coding（バイブコーディング）」の脆弱性リスクについて実際の調査結果をもとに考える]] | AIコーディングの脆弱性リスク |
| [[LLM統合コードの品質を損なう5つの「悪習慣」]] | LLM統合時のコード品質問題 |
| [[LLMが複雑なコードを理解しようとするときの失敗18パターン]] | 複雑コード理解時の失敗分析 |
| [[コード生成におけるLLMの性能を左右するプロンプトの「要素」を調べた結果]] | コード生成プロンプト要素分析 |
| [[推論特化型LLM（推論モデル）の弱点はどこか ステップ数より要件カバー率が成否を分ける]] | 推論モデルの弱点分析 |
| [[複数ターンで変わるLLMの振る舞い、タスクごとにどう違うか 安定性と崩壊の境目を探る]] | マルチターン対話の挙動分析 |
| [[LLMコスト効率を高める「プロンプト圧縮」入門 比較で見える実践のポイント]] | プロンプト圧縮手法の比較 |
| [[プロンプトログをもとにLLMの使い方の変化を読み解く]] | ログ分析による利用変化 |
| [[プロンプト作成スキルを育てる研修設計の実践例]] | プロンプト教育の実践例 |
| [[LLMの「温度」どう設定すればよい 出力の揺らぎに影響する設定パラメーターを6能力で検証]] | 温度パラメータの影響検証 |
| [[RAGの失敗パターン7選と教訓9箇条]] | RAGの失敗事例と教訓 |
| [[RAGの検索データにおける「ノイズ（事実とは異なる情報など）」には有益なノイズと有害なノイズがある]] | RAGノイズの影響分析 |
| [[RAGシステムに「無関係な」文書を混ぜたほうがLLMの出力精度が上がる可能性が示唆された]] | 無関係文書のRAGへの影響 |
| [[LLM検索と従来検索が好むウェブサイトの違い]] | 検索エンジンのソース選択比較 |
| [[脳に学ぶAIエージェントの理想形 ほか、週末読みたいAI科学ニュース]] | AI科学ニュースまとめ |
| [[ファインチューニングとRAGを比較実験した結果 LLMに外部知識を取り入れる手法としての違い]] | FTとRAGの比較実験 |

---
# 🛠 Prompt Engineering Component Library (Part 2)
*Last Updated: 2026-01-02*

> [!TIP] このライブラリの使い方
> - Part 1の「構造」「推論」「安全性」に続き、ここでは**「効率化」「エージェント」「評価・改善」**の技術を扱います。
> - 特にRAGや自律エージェントを構築する際の具体的なコンポーネントとして活用してください。

---

## ⚡ Optimize & Efficiency (効率化・最適化)
*トークン節約、検索精度向上、処理速度の最適化技術*

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMへの入力プロンプトを「意味を保持したまま」高度に圧縮する技術『LLMLingua』]] | #Comp/Optimize | **LLMLingua** (予算制御とトークン圧縮) | 長文コンテキストをコスト削減して渡す時 | RAG, Long Context |
| [[Microsoftなどのプロンプト圧縮技術『LLMLingua-“2″』タスクの精度を維持したまま圧縮率2-5倍]] | #Comp/Optimize | **LLMLingua-2** (トークン分類による圧縮) | 精度を落とさず極限まで圧縮したい時 | RAG, Few-shot |
| [[LLMに何度も答えさせるコストを10分の1に削減する手法]] | #Comp/Optimize | **Adaptive Sampling** (適応的サンプリング) | 多数決(CoT-SC)のコストを下げたい時 | Self-Consistency |
| [[長文脈タスクでもLLMの精度を下げないための対策]] | #Comp/Optimize | **Retrieve-then-Reason** (検索と推論の二段階分離) | 長文入力で推論精度が落ちる時 | RAG, CoT |
| [[多くの「長いコンテキストを要するタスク」を、短いコンテキストウィンドウのLLMで解決する手法]] | #Comp/Optimize | **LC-Boost** (長文脈の分割統治) | 短いコンテキスト長で長文を扱う時 | Map-Reduce, RAG |
| [[RAG（検索拡張生成）において約半分のトークン数でタスクを実行できるフレームワーク『FIT-RAG』]] | #Comp/Optimize | **FIT-RAG** (事実情報と選好による選抜) | RAGの検索ノイズを減らしたい時 | Self-RAG, CRAG |
| [[RAGの検索精度を実務レベルに高めるには、「情報ごとに ”質問文” を作りデータベースに入れる」のが効果的との報告]] | #Comp/Optimize | **Atomic Question Generation** (原子単位の質問化) | 検索漏れを防ぎたい時 | RAG, HyDE |
| [[RAGにおいて長文を検索することで一気に効率を上げるアプローチ『LongRAG』]] | #Comp/Optimize | **LongRAG** (長文単位の検索と読解) | 全体的な文脈を保持して検索したい時 | Long Context LLM |
| [[RAGシステムに「無関係な」文書を混ぜたほうがLLMの出力精度が上がる可能性が示唆された]] | #Comp/Optimize | **Noise Injection** (ノイズ混入による頑健化) | 検索精度が低くても回答させたい時 | RAG, Robustness |
| [[RAGにおいてLLMが「役立たない情報を無視」できるようにする『RAFT』QAタスクで従来の手法を大幅に上回る結果を達成]] | #Comp/Optimize | **RAFT** (検索拡張微調整) | 不要な情報を無視させたい時 | Fine-tuning, RAG |
| [[Googleが開発した「LLMに長文を高精度で読解させる方法論」と実行プロンプト]] | #Comp/Optimize | **ReadAgent** (ページ分割と要点抽出) | 長い文書を人間のように読解する時 | Gist Memory, Agent |
| [[LLMの推論能力は単純に文脈を繰り返し提示するだけでも大幅に向上 最大で30%改善]] | #Comp/Optimize | **CoRe** (文脈の反復提示) | 文脈の順序による見落としを防ぐ時 | Long Context |

---

## 🔧 Agents & Tools (自律動作・外部連携)
*自律的な行動、ツール使用、複数モデルの連携技術*

| Link                                                        | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMエージェントが実行可能なPythonコードを生成するフレームワーク『CodeAct』]]           | #Comp/Agent | **CodeAct** (実行可能コードによる行動) | 複雑な操作をコードで完結させる時 | Tool Use, Python |
| [[プロンプトでLLMにRPAワークフローを自動生成させる手法「FlowMind」JPモルガン考案]]         | #Comp/Agent | **FlowMind** (NCEN-QA/ワークフロー生成) | 即興的なタスクを自動化したい時 | Chain of Thought |
| [[ユーザーの指示が曖昧なとき、LLM側が確認を行うエージェントアーキテクチャ『Mistral-Interact』]] | #Comp/Agent | **Mistral-Interact** (意図確認と曖昧さ解消) | ユーザーの指示が不明確な時 | Clarification |
| [[LLMに「信念・願望・意図」を実装 エージェントの頭の中を言語化する]]                      | #Comp/Agent | **BDI Model** (信念・願望・意図の構造化) | エージェントの行動原理を説明する時 | Role Prompting |
| [[本番環境で動くAIエージェントワークフローの作り方 9つのベストプラクティスで信頼性と保守性を実現]]       | #Comp/Agent | **Consortium of Models** (複数モデル合議制) | 単一モデルのバイアスを防ぎたい時 | Multi-Agent |
| [[再現性のある人間行動シミュレーションへ LLMのふるまいを数値で制御する]]                    | #Comp/Agent | **SAC (Agent)** (数値による行動バイアス制御) | エージェントの性格を微調整したい時 | Persona Prompting |
| [[心の理論をLLMエージェントに実装することの効果]]                                | #Comp/Agent | **Hypothetical Minds** (他者視点シミュレーション) | 協調・競争タスクを行う時 | Theory of Mind |
| [[LLMでユースケース図の作成時間を大幅に短縮 3つのプロンプト技術を組み合わせ]]                 | #Comp/Agent | **Role-Based Workflow** (専門家ロールと知識注入) | 専門的な図解作成を自動化する時 | Role Prompting |
| [[LLMのソフトウェア開発タスクに効くプロンプト設計の選び方 手法14種を一斉検証]]                | #Comp/Agent | **Task-Specific Prompting** (タスク別最適化) | 開発タスクごとに最適な手法を選ぶ時 | Few-shot, CoT |
| [[GPT-4との対話でタスクプランニングを行うロボットシステムフレームワークが発明されました。]]          | #Comp/Agent | **Interactive Task Planning** (対話的タスク計画) | 物理世界のタスクを計画する時 | VLM, Robotics |
| [[異なるLLMが円卓を囲み議論した結果の回答は品質が高いとの検証報告。円卓ツールも公開]]              | #Comp/Agent | **ReConcile** (異種LLM円卓会議) | 多様な視点で合意形成したい時 | Multi-Agent Debate |
| [[LLMにエピソード記憶のような能力を持たせるRAGのテクニック]]                         | #Comp/Agent | **Episodic Memory RAG** (エピソード記憶の構造化) | 時系列や状態変化を記憶させたい時 | Memory Systems |
| [[LLMエージェントに必要なメモリーの選び方と残し方 抽出と構造化で蓄積される記憶のかたち]]            | #Comp/Agent | **Mem0 / Mem0g** (記憶の抽出とグラフ化) | 長期的な文脈を維持したい時 | Knowledge Graph |

---

## 📊 Evaluation & Refinement (評価・改善)
*出力品質の測定、自己修正、フィードバックループ技術*

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMの「自己対話」により複雑な問題の解決能力を飛躍的に向上させる手法『Iteration of Thought』]] | #Comp/Eval | **Iteration of Thought** (内部対話による反復改善) | 1回の出力で品質が不十分な時 | CoT, Self-Correction |
| [[検索結果をLLMでチェックして自動的に再検索する『MetaRAG』出力精度を大幅に向上]] | #Comp/Eval | **MetaRAG** (メタ認知による検索評価) | 検索結果が不十分か判断したい時 | Metacognition, RAG |
| [[LLMの検索結果をさらに正確にする手法『CRAG』（Corrective Retrieval Augmented Generation：修正型の検索拡張生成）]] | #Comp/Eval | **CRAG** (検索信頼度評価と修正) | 検索結果の誤りを訂正したい時 | RAG, Web Search |
| [[要約の品質を評価する新たなツール「SEAHORSE」の登場]] | #Comp/Eval | **Multidimensional Eval** (多面的品質評価) | 要約の品質を6軸で評価したい時 | LLM-as-a-Judge |
| [[LLMに自分自身の内部動作を説明させる手法]] | #Comp/Eval | **Patchscopes** (内部表現の言語化) | モデルの判断根拠を解析したい時 | Interpretability |
| [[LLMの内部状態を観察することで「出力がハルシネーションか否かを判別する」手法『LLMファクトスコープ』]] | #Comp/Eval | **Factoscope** (内部状態による事実検証) | ハルシネーションを検知したい時 | Safety |
| [[LLMによるペルソナ生成のプロンプトはどう設計するか 実態調査から学ぶヒント]] | #Comp/Eval | **Persona Evaluation** (ペルソナの一貫性評価) | キャラクターの一貫性を測りたい時 | Role Prompting |
| [[Webページの見た目や使い勝手をLLMに診断させるプロンプト手法]] | #Comp/Eval | **Diagnostic Prompting** (診断的質問→総合評価) | 主観的評価を客観化したい時 | Multi-modal |
| [[要約タスクで判明した”品質vs事実整合性”のトレードオフ]] | #Comp/Eval | **Factuality-Consistency Tradeoff** (品質/事実性評価) | 要約の正確性を重視したい時 | RAG, CoT |
| [[LLMハルシネーション対策の新手法 繰り返し回答させバラつきを見る]] | #Comp/Eval | **Semantic Entropy** (回答のバラつきによる確信度) | モデルの自信を測りたい時 | Self-Consistency |
| [[「ポジティブ思考」プロンプトでLLMの性能向上 さらに自動最適化プロンプトが上をいくが、奇妙な現象も]] | #Comp/Eval | **EmotionPrompt** (感情的刺激による向上) | 性能の限界を突破したい時 | System Prompt |
| [[プロンプトを遺伝的アルゴリズムで自動最適化するプロンプトエンジニアリング手法『Promptbreeder（プロンプトブリーダー）』]] | #Comp/Eval | **Promptbreeder** (進化的プロンプト最適化) | 最適なプロンプトを自動探索したい時 | Genetic Algorithm |
| [[プロンプトを調整しないLLMのプロンプトエンジニアリング新手法『ControlPE』]] | #Comp/Eval | **ControlPE** (LoRAによる挙動制御) | プロンプト以外で挙動を制御したい時 | Fine-tuning, LoRA |
| [[LLMにプロンプトのみで仮想的な強化学習を発生させる方法]] | #Comp/Eval | **ICRL** (文脈内強化学習) | 試行錯誤から学習させたい時 | Few-shot, RLHF |
| [[LLMを新しいタスクに順応させる「文脈内学習」における効率的なコンテキストの作り方]] | #Comp/Eval | **Cheat Sheet ICL** (学習内容のチートシート化) | 多ショット学習を効率化したい時 | Many-shot |
| [[DeepMindの研究者らが有効性を検証した、LLMに自ら高品質な訓練データを生成させる「自己学習」]] | #Comp/Eval | **ReST** (強化自己学習) | 自律的に性能を向上させたい時 | Fine-tuning |
| [[LLMに「自分自身との対戦」で能力を向上させる手法『Self-Play Fine-Tuning（SPIN）』]] | #Comp/Eval | **SPIN** (自己対戦による微調整) | 外部データなしで強化したい時 | Self-Play |
| [[反復学習でCoTによる推論性能を向上させる手法 Metaとニューヨーク大学による研究]] | #Comp/Eval | **Iterative RPO** (推論選好最適化) | 推論能力を段階的に高めたい時 | CoT, DPO |
| [[既存のLLMを融合させて強力なモデルを作る手法「知識融合」]] | #Comp/Eval | **Knowledge Fusion** (モデル知識の統合) | 複数モデルの強みを合わせたい時 | Model Merging |
| [[LLMの知識を狙い撃ちして変更・修正する「知識編集（Knowledge Editing）」]] | #Comp/Eval | **Knowledge Editing** (知識の直接編集) | 特定の知識だけ修正したい時 | Model Editing |


---

# 🍳 Prompt Engineering Recipes: 目的別組み合わせレシピ集
*Based on Component Library Part 1 & 2*

このレシピ集は、**「User Intent (やりたいこと)」**に合わせて最適な技術スタックを提示します。システムプロンプトを設計する際の設計図として活用してください。

## 1. 🧠 難解な推論 (Reasoning)
*数学、論理パズル、複雑な計画立案など、高度な思考力を必要とするタスク向け*

| User Intent | Recipe (技術の組み合わせ) | 効果・メカニズム | 備考 |
|:---|:---|:---|:---|
| **難問の突破口を開く** | **Step-Back Prompting** + **CoT** + **Self-Consistency** | 具体的な詳細に囚われず「前提・原理」へ一度抽象化し、そこから段階的に推論(CoT)する。最後に複数回答の整合性(SC)を取ることで正答率を最大化。 | 物理や科学の問題に特に有効。 |
| **厳密な論証を行う** | **Logic-of-Thought (LoT)** + **SSR (Socratic Self-Refine)** | 命題論理形式へ変換(LoT)して構造を明確にし、ステップごとの自己問答(SSR)で論理の飛躍を防ぐ。 | 法的文書や契約書の分析に。 |
| **未知の解法を探索** | **SELF-DISCOVER** + **ThoughtSculpt** | タスク固有の推論構造をモデル自身に発見させ、MCTS（モンテカルロ木探索）的なアプローチで最適解を探索・修正する。 | 前例のない新規課題の解決に。 |
| **直感的な罠を回避** | **Verification-First** + **Error-Aware Demonstration** | まず「仮説の検証」から入らせることで思い込みを排除し、さらに「よくある間違い」を例示して回避させる。 | ひっかけ問題や認知バイアス対策。 |

## 2. 📚 高精度な検索応答 (RAG / Knowledge)
*社内文書検索、専門知識の回答など、事実の正確性が最優先されるタスク向け*

| User Intent | Recipe (技術の組み合わせ) | 効果・メカニズム | 備考 |
|:---|:---|:---|:---|
| **検索漏れを防ぐ** | **Atomic Question Generation** + **LongRAG** | 文書を「原子」単位の質問に変換して検索性を高めつつ、検索後は長い文脈(LongRAG)で全体像を捉える。 | マニュアルや規定集の検索に。 |
| **ハルシネーション抑制** | **CRAG** + **CoVe (Chain-of-Verification)** | 検索結果の信頼性を評価(CRAG)し、不十分ならWeb検索へフォールバック。回答生成時に自己検証ループ(CoVe)を回す。 | 医療や金融などミスが許されない分野。 |
| **情報の矛盾を解消** | **MetaRAG** + **Consortium of Models** | メタ認知により「知識不足」や「矛盾」を検知し、複数モデルの合議制で最も確からしい情報を統合する。 | 複数のニュースソースの統合など。 |
| **無関係な情報の排除** | **RAFT** + **Retrieve-then-Reason** | 不要な情報を無視するよう微調整(RAFT)した上で、検索フェーズと推論フェーズを明確に分ける。 | ノイズの多いWeb検索結果の処理。 |

## 3. 🤖 安全なエージェント (Safety / Agent)
*自律的にツールを使い、外部環境と対話するエージェント向け*

| User Intent | Recipe (技術の組み合わせ) | 効果・メカニズム | 備考 |
|:---|:---|:---|:---|
| **確実なツール操作** | **CodeAct** + **One-Agent-One-Tool** | 自然言語ではなく「実行可能なPythonコード」で行動し、1エージェントにつき1ツールに限定することで動作を安定させる。 | データ分析、ファイル操作自動化。 |
| **曖昧な指示への対応** | **Mistral-Interact** + **BDI Model** | ユーザーの意図が不明確な場合、質問を投げかけて「信念・願望・意図(BDI)」を確定させてから行動する。 | 秘書ボット、要件定義支援。 |
| **安全な挙動の担保** | **Hypothetical Minds** + **SAC (Agent)** | 「もしこの行動をしたら？」という他者視点シミュレーションを行い、数値パラメータで行動バイアスを安全側に制御する。 | 顧客対応、交渉エージェント。 |
| **長期的な文脈維持** | **Episodic Memory RAG** + **Mem0** | 時系列や状態変化を構造化して記憶し、長期的な対話でも「以前の状態」を踏まえた行動をとる。 | RPGのNPC、長期プロジェクト管理。 |

## 4. 🎨 創造的なタスク (Creative)
*小説執筆、アイデア出し、ペルソナ模倣など、多様性と表現力が求められるタスク向け*

| User Intent | Recipe (技術の組み合わせ) | 効果・メカニズム | 備考 |
|:---|:---|:---|:---|
| **感情豊かな表現** | **EmotionPrompt** + **SAC (Intensity Control)** | 感情的な刺激でモデルの性能を底上げしつつ、性格特性の「強度」を数値で微調整してニュアンスを出す。 | ストーリーテリング、カウンセリング。 |
| **特定の人物の再現** | **P2 Prompting** + **ValueSim** | 文体だけでなく、その人物の「価値観」や「バックストーリー」を構造化して与え、判断基準そのものを模倣させる。 | 有名人の模倣、ユーザーの分身作成。 |
| **多様なアイデア出し** | **Role Prompting** + **Interrogative Persona** | 専門家の役割を与えるだけでなく、対話形式で役割を深掘りさせ、固定観念に縛られない多様な出力を促す。 | ブレスト、企画立案。 |

## 5. ⚡ 効率的な処理 (Efficiency)
*APIコスト削減、応答速度の向上、大量データの処理向け*

| User Intent    | Recipe (技術の組み合わせ)                                              | 効果・メカニズム                                              | 備考                 |
| :------------- | :------------------------------------------------------------- | :---------------------------------------------------- | :----------------- |
| **長文の超圧縮**     | **LLMLingua-2** + **Cheat Sheet ICL**                          | トークン分類により情報を保持したまま圧縮し、学習内容を「チートシート」化して再利用する。          | 議事録要約、長文ログ解析。      |
| **コスト対効果の最大化** | **Adaptive Sampling** + **LC-Boost**                           | 回答の確信度に応じて生成回数を動的に変え、長文脈を分割統治することでコストを抑える。            | 大量ドキュメントのバッチ処理。    |
| **高速なコード生成**   | **Context Categorization** + **In-Context Principle Learning** | 必要なコンテキストを5分類して過不足なく与え、失敗パターンを「原則」として事前提示することで手戻りを防ぐ。 | コーディング支援、リファクタリング。 |

---

> [!NOTE] 補足: レシピのカスタマイズ
> これらのレシピは「部品」の組み合わせです。
> - **さらに精度を上げたい場合:** 「Evaluation (評価)」カテゴリの技術（例: Self-Reflection）を追加してください。
> - **コストを下げたい場合:** 「Optimize (効率化)」カテゴリの技術（例: LLMLingua）を挟み込んでください。
> - **モデルの特性に合わせて:** 推論特化モデル(o1など)にはCoT系を控えめに、軽量モデルにはRole Promptingを強めにするなどの調整が有効です。