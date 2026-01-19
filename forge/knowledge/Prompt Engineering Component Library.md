# 🛠 Prompt Engineering Component Library (Part 1)
*Last Updated: 2025-05-15*

> [!TIP] このライブラリの使い方
> - Claude/Geminiのシステムプロンプト構築時、必要な「機能部品」をピックアップ
> - **Synergy列**を参照し、相性の良い技術を組み合わせる
> - Dataviewクエリ例: `TABLE WHERE contains(Tag, "#Comp/Reasoning")`

---

## 🏗 Frameworks & Structures (構造・骨格)

プロンプトの**骨格・順序・構造**を定義し、出力の形式や役割を制御する技術群。

| Link                                                                                 | #Tag            | 🔧 Component (Mechanism)                     | 🎯 Trigger (40文字以内) | 🔗 Synergy                  |
| :----------------------------------------------------------------------------------- | :-------------- | :------------------------------------------- | :------------------ | :-------------------------- |
| [[10億人のペルソナ（人物像）で多様な合成データを作成するための技術]]                                                | #Comp/Structure | **Persona Hub** (10億の多様な視点からのデータ合成)          | 多様な視点の合成データが必要な時    | Few-shot, Role-play         |
| [[150本超のLLM資料から紐解く、プロンプトの効果を高める21の性質]]                                               | #Comp/Structure | **21 Principles** (効果的なプロンプトの21の性質)          | プロンプトの基礎品質を上げたい時    | CO-STAR, Few-shot           |
| [[ChatGPTの効果的なプロンプト手法における「基本のキ」を理論とテンプレート両方で紹介]]                                     | #Comp/Structure | **Role-Prompting** (役割の付与による品質向上)            | 特定の専門家として振る舞わせる時    | CoT, XML Delimiters         |
| [[ChatGPTの効果的なプロンプト手法における「基本のキ」を理論とテンプレート両方で紹介]]                                     | #Comp/Structure | **Triple Quotes** (区切り文字による指示の明確化)           | 指示とデータを明確に分けたい時     | XML Structuring             |
| [[Cursorで開発者がAIに伝えるべき情報は5種類に分類できる 『正しいコード』を書かせるために必要なコンテキストとは]]                      | #Comp/Structure | **Context Categories** (5種の必須コンテキスト分類)       | コーディング支援の精度を上げたい時   | Rule Files, XML             |
| [[LLMが図表を読み間違える理由と精度を上げるヒント]]                                                        | #Comp/Structure | **Step-by-Step Visualization** (段階的読み取り指示)   | グラフや図表の数値を正確に読む時    | CoT, Multi-modal            |
| [[LLMでユースケース図の作成時間を大幅に短縮 3つのプロンプト技術を組み合わせ]]                                          | #Comp/Structure | **Structured Diagramming** (役割+知識注入+否定指示)    | UML図等を正確に生成させたい時    | Negative Prompting          |
| [[LLMで本当に創造性が高まる関わり方 アイデアの均質化は避けられる]]                                                | #Comp/Structure | **Question-Led Interaction** (質問主導型インタラクション) | アイデアの多様性と所有感を保つ時    | Brainstorming               |
| [[LLMに心理療法にもとづいて「高い共感力と思いやりある会話」をさせるプロンプト手法]]                                        | #Comp/Structure | **Chain of Empathy (CoE)** (心理療法モデルに基づく共感生成) | カウンセリングや共感対話が必要な時   | Role-play, Emotional Prompt |
| [[LLMに無礼なプロンプトを使用すると性能が低下するリスクの報告 一部、直感に反する複雑な結果も]]                                  | #Comp/Structure | **Politeness Policy** (丁寧さレベルの調整)            | 指示従順性やバイアスを制御する時    | Role-play, EmotionPrompt    |
| [[LLMの精度が変わるのはプロンプト内の「情報の位置」のせいかもしれない]]                                              | #Comp/Structure | **Exemplar Placement Strategy** (事例配置の最適化)   | 文脈内学習の精度を安定させたい時    | Few-shot, ICL               |
| [[LLMの回答精度が質問の言語によってばらつく問題への対応策]]                                                    | #Comp/Structure | **Translation Ensemble (TrEn)** (複数言語訳の併記)   | 多言語タスクの精度を上げたい時     | Self-Consistency, TTA       |
| [[LLMの回答精度が質問の言語によってばらつく問題への対応策]]                                                    | #Comp/Structure | **Translate-then-Answer (TTA)** (一度翻訳してから回答) | 低リソース言語での回答精度向上時    | CoT, Self-Reflection        |
| [[LLMペルソナプロンプトの細かい設計が出力に与える影響を詳しく検証]]                                                | #Comp/Structure | **Implicit Persona** (名前や会話による間接的役割付与)       | ステレオタイプを避け自然な応答を得る時 | Role-play, Few-shot         |
| [[LLMを「人間の心のケア」を行うカウンセリングAIとして実行するためのプロンプト手法]]                                       | #Comp/Structure | **RESOРT Framework** (6つの心理的視点による再評価)        | 認知的再評価やメンタルケアを行う時   | Chain of Empathy, Role-play |
| [[LLMを新しいタスクに順応させる「文脈内学習」における効率的なコンテキストの作り方]]                                        | #Comp/Structure | **Cheat Sheet ICL** (学習パターンの要約シート化)          | 大量の例示をトークン節約して使う時   | Few-shot, RAG               |
| [[Webページの見た目や使い勝手をLLMに診断させるプロンプト手法 - AIDB/AIDB_98529]]                               | #Comp/Structure | **Diagnostic Prompting** (詳細な診断質問による評価)      | UI/UXの視覚的複雑さを評価する時  | Multi-modal, CoT            |
| [[「ポジティブ思考」プロンプトでLLMの性能向上 さらに自動最適化プロンプトが上をいくが、奇妙な現象も]]                               | #Comp/Structure | **Positive Thinking** (楽観的な思考の注入)            | 難問に対する粘り強さを引き出す時    | EmotionPrompt, CoT          |
| [[「自分を信じて限界を超えてください」など感情を込めたプロンプト『EmotionPrompt』が添えられると、ChatGPTなどのLLMのパフォーマンスは向上する]] | #Comp/Structure | **EmotionPrompt** (感情的刺激による性能向上)             | 複雑タスクの回答品質を上げたい時    | CoT, Positive Thinking      |
| [[タスクに応じてロールプレイさせるとChatGPTなどLLMの推論能力は普遍的に向上する]]                                      | #Comp/Structure | **Role-Play Prompting** (タスクに応じた役割演技)        | ゼロショットでの推論能力向上時     | CoT, Persona                |
| [[プロンプトに5つほど”価値観の例”を示すだけで、LLMは特定の文化に適応した回答ができるようになるとの報告]]                            | #Comp/Structure | **Self-Alignment** (価値観事例による自己調整)            | 特定の文化・価値観に適応させる時    | Few-shot, ICL               |
| [[プロンプトに例を多く載せるほど、どんなタスクでも性能が上がるのか？DeepMindによる『Many-shot Learning』の実験結果]]            | #Comp/Structure | **Many-Shot ICL** (数百〜数千の例示による学習)            | 困難なタスクや低リソース言語翻訳時   | Long Context, ICL           |
| [[プロンプトの原則26ヶ条をまとめた報告]]                                                              | #Comp/Structure | **26 Principles** (効果的なプロンプト原則集)             | プロンプトの基礎設計を見直す時     | CO-STAR, Few-shot           |
| [[時系列データをグラフにしてLLMに見せると文字だけより最大120%性能向上 トークンも節約]]                                    | #Comp/Structure | **Plot-based Prompting** (時系列データの可視化入力)      | 数値データの傾向を直感的に理解させる時 | Multi-modal, CoT            |

---

## 🧠 Reasoning Engines (思考・推論)

**思考プロセスの質**（深さ・広さ・論理性）を向上させ、複雑な問題を解決する技術群。

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[8つの質問で自分自身の答えを批評する哲学的手法を活用したLLMのプロンプティング技術]] | #Comp/Reasoning | **Critical-Questions-of-Thought** (Toulminモデルに基づく批判的検証) | 推論の論理的弱点を見つけたい時 | CoT, Self-Reflection |
| [[ChatGPTなどのLLMにユーザーの性格特性を分析させる手法『PsyCoT』と実行プロンプト]] | #Comp/Reasoning | **PsyCoT** (心理分析のための多段階推論) | テキストから性格特性を分析する時 | Role-play, CoT |
| [[CoTの推論ステップ数がLLMの推論能力に及ぼす影響を詳細に検証した結果]] | #Comp/Reasoning | **Longer CoT** (推論ステップの長文化) | 難問でより深い思考が必要な時 | CoT, Self-Consistency |
| [[GPT-4などLLMのコード生成能力にデバッグ機能を追加する『SELF-DEBUGGING（セルフデバッギング）』と実行プロンプト]] | #Comp/Reasoning | **SELF-DEBUGGING** (生成・説明・フィードバックループ) | コード生成のバグを自己修正させる時 | CodeAct, CoT |
| [[GPT-4などに対してプロンプトのみから「新しい言葉の概念」を学習させるためのフレームワーク『FOCUS』]] | #Comp/Reasoning | **FOCUS** (因果推論による概念学習) | 未知の造語やスラングを解釈する時 | ICL, CoT |
| [[GPT-4などのLLMに「自らの論理的な整合性をチェック」させるフレームワーク『LogiCoT』と実行プロンプト]] | #Comp/Reasoning | **LogiCoT** (論理整合性の自己チェック) | 推論の矛盾を防ぎたい時 | CoT, Self-Verification |
| [[GPT-4のコード生成能力を飛躍的に向上させるプロンプトフレームワーク『AlphaCodium』]] | #Comp/Reasoning | **AlphaCodium** (反復的なフローエンジニアリング) | 競技プログラミング級のコード生成時 | Self-Reflection, Test-Driven |
| [[Googleなどが開発、LLMに表データ（.csvなど）の情報を深く理解させるためのフレームワーク『Chain of Table』]] | #Comp/Reasoning | **Chain of Table** (表データの段階的操作と推論) | 複雑な表データから回答を導く時 | CoT, Pandas |
| [[LLMにタスクに応じた推論プロセスを自ら考えるようにするプロンプト手法『SELF-DISCOVER』Google DeepMindなどが開発]] | #Comp/Reasoning | **SELF-DISCOVER** (推論構造の自己発見と適用) | 未知のタスクの解法を模索する時 | CoT, Plan-and-Solve |
| [[LLMにナレッジグラフ（知識グラフ）を連携させることで、タスク遂行能力を大幅に向上させるフレームワーク『Graph Neural Prompting（GNP）』]] | #Comp/Reasoning | **Graph Neural Prompting** (知識グラフの埋め込み連携) | 外部知識との連携を強化したい時 | RAG, Knowledge Graph |
| [[LLMにプロンプトのみで仮想的な強化学習を発生させる方法]] | #Comp/Reasoning | **ICRL Prompting** (履歴とスコアによる文脈内強化学習) | 正解のないタスクで改善を促す時 | Few-shot, Self-Refine |
| [[LLMに敢えて間違わせてルールを覚えさせるプロンプト手法 Google DeepMindなどが考案]] | #Comp/Reasoning | **LEAP (In-Context Principle)** (失敗からの原則学習) | 同じミスを繰り返さないようにする時 | Few-shot, Self-Reflection |
| [[LLMに非線形的な思考を与えてCoTを上回る性能を引き出す手法『IEP』と実行プロンプト CoTと組合せでさらに強力になる場合も]] | #Comp/Reasoning | **IEP** (計画・推論・除去の非線形思考) | 多角的な視点で最適解を探す時 | ToT, CoT |
| [[LLMの「自己対話」により複雑な問題の解決能力を飛躍的に向上させる手法『Iteration of Thought』]] | #Comp/Reasoning | **Iteration of Thought (IoT)** (内部対話による反復推論) | 答えが出るまで自律的に考えさせる時 | CoT, Self-Refine |
| [[LLMの推論能力は単純に文脈を繰り返し提示するだけでも大幅に向上 最大で30%改善]] | #Comp/Reasoning | **CoRe** (文脈の反復提示による理解深化) | 複雑な文脈や順序が乱れた情報を読む時 | Long Context, RAG |
| [[LLMの推論能力を戦略的に向上させる新しいプロンプト手法『SCoT』]] | #Comp/Reasoning | **SCoT** (戦略立案とその後の推論) | 解法戦略を先に立ててから解く時 | CoT, Plan-and-Solve |
| [[LLMの推論能力を向上させるプロンプトベースの綿密なフレームワーク]] | #Comp/Reasoning | **SSR (Socratic Self-Refine)** (サブ質問分解とステップ検証) | 長い推論の途中ミスを防ぐ時 | Self-Refine, CoT |
| [[LLMの論理的推論能力をステップバイステップ以上に向上させる手法『Logic-of-Thought』プロンプティング（テンプレートつき）]] | #Comp/Reasoning | **Logic-of-Thought (LoT)** (論理的関係の抽出と拡張) | 論理パズルや厳密な推論を行う時 | CoT, Symbolic Reasoning |
| [[LLMが思考のネットワークを構築し、人間の推論プロセスを模倣する『THOUGHTSCULPT』プロンプティング]] | #Comp/Reasoning | **THOUGHTSCULPT** (MCTSベースの思考探索と修正) | 試行錯誤しながら最適解を探す時 | ToT, MCTS |
| [[LLMをセラピストとして実行し、「認知の歪み」を診断させるためのプロンプト手法]] | #Comp/Reasoning | **Diagnosis of Thought (DoT)** (主観・客観分離と対比推論) | 認知バイアスや思考の癖を分析する時 | Chain of Empathy, Role-play |
| [[LLMで因果推論を行うためのプロンプト手法]] | #Comp/Reasoning | **Stat Causal Prompting** (統計的因果探索と背景知識融合) | 因果関係の有無を推論させる時 | CoT, Scientific Reasoning |
| [[タスクを一度視覚化して取り組ませることで、LLMの推論能力を大きく向上させるプロンプト手法『Whiteboard-of-Thought（ホワイトボード思考法）』]] | #Comp/Reasoning | **Whiteboard-of-Thought** (コードによる視覚化と再入力) | 空間推論や視覚的課題を解く時 | Multi-modal, CodeAct |
| [[推論能力をさらに強める戦略『AoT』で、LLMが「直感」に似た能力を示すようになった]] | #Comp/Reasoning | **Algorithm of Thoughts (AoT)** (探索アルゴリズムの模倣) | 探索範囲が広い問題を効率的に解く時 | ToT, DFS/BFS |
| [[検索結果をLLMでチェックして自動的に再検索する『MetaRAG』出力精度を大幅に向上]] | #Comp/Reasoning | **MetaRAG** (メタ認知による検索必要性判断) | 知識不足を自覚して再検索させる時 | RAG, Self-Reflection |
| [[複数のLLMを「円卓会議」させて推論能力を高める「ReConcile」]] | #Comp/Reasoning | **ReConcile** (異種モデル間の議論と合意) | 難問に対して多角的な視点が必要な時 | Multi-Agent, Debate |
| [[高度な推論を「コードシミュレーション」で代替する]] | #Comp/Reasoning | **Code Simulation** (自然言語タスクのコード化) | 手順が複雑な論理パズルを解く時 | CodeAct, CoT |
| [[「検証してから答える」ことでLLMの推論精度を向上させる手法]] | #Comp/Reasoning | **Verification-First (VF)** (仮説検証からの逆算推論) | 正解のない状態から推論を開始する時 | Self-Correction, CoT |
| [[Self-Reflection（自己反省）がLLMのパフォーマンスに与える影響を網羅的に調査]] | #Comp/Reasoning | **Self-Reflection** (出力後の自己評価と修正) | 初回の回答を改善させたい時 | CoT, Self-Consistency |

---

## 🛡 Safety & Guardrails (信頼性・安全性)

出力の**信頼性・安全性**を担保し、ハルシネーションやバイアスを抑制する技術群。

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMに「自信の度合いに応じて説明のニュアンスを変更させる」ことがユーザーの誤解を回避する]] | #Comp/Safety | **Confidence Calibration** (確信度に基づく表現調整) | ユーザーの過度な信頼を防ぐ時 | Self-Awareness |
| [[LLMに自身のハルシネーション（幻覚）を「自覚」させ、減らす方法]] | #Comp/Safety | **Hallucination Awareness** (前処理・後処理での自覚) | 事実に基づかない生成を抑制する時 | CoVe, Self-Reflection |
| [[LLMの出力から誤り（ハルシネーション）を減らす新手法『CoVe（Chain-of-Verification）』と実行プロンプト]] | #Comp/Safety | **Chain-of-Verification** (検証質問による自己修正) | ファクトチェックを厳密に行う時 | Self-Refine, RAG |
| [[LLMの回答における「自信ありげな度合い」と「実際の自信」を一致させるプロンプト手法]] | #Comp/Safety | **MetaFaith** (メタ認知感度に基づく表現) | 自信と口調を一致させたい時 | Confidence Calibration |
| [[LLMを用いて「記事や投稿に潜むバイアスの検出と修正」を行う方法]] | #Comp/Safety | **Debiasing Framework** (バイアス検出と中立化) | 公平な文章に修正したい時 | Role-play, CoT |
| [[「Vibe Coding（バイブコーディング）」の脆弱性リスクについて実際の調査結果をもとに考える]] | #Comp/Safety | **Security Oracle** (脆弱性情報の事前提供) | 安全なコードを生成させたい時 | CodeAct, Self-Correction |
| [[再現性のある人間行動シミュレーションへ LLMのふるまいを数値で制御する]] | #Comp/Safety | **Programmable Cognitive Bias** (数値によるバイアス制御) | エージェントの挙動を精密に制御する時 | Role-play, Simulation |
| [[認識論的不確かさと偶発的不確かさを区別するハルシネーション検出]] | #Comp/Safety | **Uncertainty Quantification** (不確かさの種類の区別) | 知識不足か曖昧さかを判別する時 | Self-Consistency |
| [[ペルソナによるバイアス変動の測定と評価]] | #Comp/Safety | **Bias Measurement** (ペルソナ視点でのバイアス測定) | 特定の視点による偏りを評価する時 | Persona, Role-play |
| [[手の込んだ手法よりシンプルな手法の方がLLMは幻覚を起こしにくい]] | #Comp/Safety | **Chat Protect** (矛盾回答時の発言控え) | 自信がない時に沈黙させたい時 | Self-Consistency, Multi-Agent |
| [[誠実な自信表現を促す「MetaFaith」プロンプティング]] | #Comp/Safety | **MetaFaith** (メタ認知に基づく誠実な表現) | 知ったかぶりを防ぎたい時 | Confidence Calibration |

---

## 📚 Reference / Context (背景知識)

| Link | 概要 (30文字以内) |
|:---|:---|
| [[100個の事例を分析して明らかになったLLM-RAGアプリケーション「19の欠陥パターン」]] | RAGアプリの19の欠陥パターン分析 |
| [[AIが就活して成長する市場で強かったのは「自己理解が深い」AIエージェント]] | 自己理解エージェントの優位性 |
| [[AIエージェント本番運用の実態調査 実務家が明かす成功の条件と課題]] | エージェント運用の実態調査 |
| [[AI時代の仕事再設計 19万職種の大規模分析が示す『自動化より生産性向上』の道筋]] | 19万職種の自動化分析レポート |
| [[ChatGPTの「初頭効果」について]] | 初頭効果によるバイアスの検証 |
| [[CoT（思考の連鎖）は数学や論理で劇的に性能を向上させる一方、常識や知識のタスクでほとんど効果がない]] | CoTの効果範囲に関する検証 |
| [[GPT-4などのLLMが「AはB」から「BはA」を導かない『逆転の呪い』における誤解なき解釈と対策]] | 逆転関係の推論失敗（逆転の呪い） |
| [[GPT-4に選択肢を与えるとき、順序を入れ替えるだけで性能に大きな変化があることが明らかに]] | 選択肢順序バイアスの検証 |
| [[GPT-4やGeminiなどさまざまなLLMで、プロンプトの入力が長くなるにつれて推論性能に顕著な低下が見られる]] | 長文入力による推論性能低下 |
| [[GPT-5などの高性能LLMは実際に稼げるのか？実案件で大規模調査 人間が介入すべきタスクとは]] | 高性能LLMの実務能力調査 |
| [[GPTが「心の理論」をもつかどうかはプロンプト次第]] | 心の理論の有無とプロンプトの関係 |
| [[Geminiの「常識を推論する能力」を網羅的に調査した結果 間違えやすいタイプの問題も明らかに]] | Geminiの常識推論能力調査 |
| [[JSONなどの構造化出力はLLMの質にどう影響するか]] | 構造化出力が推論に与える影響 |
| [[LLMがソフトウェアエンジニアリングでどのように適用可能か、網羅的な調査＆分析結果]] | SE領域でのLLM活用調査 |
| [[LLMが複雑なコードを理解しようとするときの失敗18パターン]] | 複雑コード理解時の失敗パターン |
| [[LLMの「知っているのに嘘をつく」幻覚と「知らないから間違える」幻覚の違い]] | 知識有無による幻覚タイプの違い |
| [[LLMの均質な回答が良いか悪いかはタスクで決まる]] | 回答の均質性とタスクの相性 |
| [[LLMの設計仕様と挙動にはギャップがある モデルが自然に大事にしている価値観を探る]] | 設計仕様と実際の挙動のギャップ |
| [[LLMはRAGコンテキストと事前知識のどちらに依存する？]] | 外部知識と内部知識の優先度 |
| [[LLMはシステムプロンプトをどれほど守れるか]] | システムプロンプト遵守能力の検証 |
| [[LLMは与えられたペルソナ（役割）に応じてバイアスが変化することが明らかに]] | ペルソナによるバイアス変化 |
| [[RAGにおいて取得された情報と事前知識が矛盾しても、情報に説得力があるときLLMは受け入れる]] | 矛盾情報の受容条件 |
| [[RAGの失敗パターン7選と教訓9箇条]] | RAG構築の失敗パターンと教訓 |
| [[RAGの検索データにおける「ノイズ（事実とは異なる情報など）」には有益なノイズと有害なノイズがある]] | RAGにおけるノイズの影響分析 |
| [[「あなたは〇〇です」などのペルソナ設定を与えても、事実に基づく質問への回答精度は向上しないとの主張]] | 事実質問へのペルソナ効果検証 |
| [[「コンテキストエンジニアリング」とは何か？なぜ重要なのか？]] | コンテキストエンジニアリングの概要 |
| [[「人が語るときに頭の中で何が起きているか」LLMを使って分析した結果]] | 思考プロセスのLLMによる分析 |
| [[『プロンプトレポート』OpenAIなどが作成した調査報告書 〜その1 重要な用語と各種プロンプト手法〜]] | プロンプト技術の用語集・分類 |
| [[『プロンプトレポート』OpenAIなどが作成した調査報告書 〜その2 マルチモーダルとエージェント〜]] | マルチモーダル・エージェント技術 |
| [[ことばとふるまいで変わるAIとの距離感]] | AIとのインタラクション研究 |
| [[コード生成におけるLLMの性能を左右するプロンプトの「要素」を調べた結果]] | コード生成プロンプト要素の影響 |
| [[コンテキスト内で重要な情報同士が離れすぎるとLLMの性能は大幅に下がる]] | 情報間距離による性能低下 |
| [[トランスフォーマーベースのLLMにおける根本的な5つの弱点をおさらいする]] | LLMの根本的な弱点分析 |
| [[ナレッジグラフ（知識グラフ）とLLMを掛け合わせる方法のロードマップ]] | KGとLLMの統合ロードマップ |
| [[ファインチューニングとRAGを比較実験した結果 LLMに外部知識を取り入れる手法としての違い]] | FTとRAGの比較検証 |
| [[プロンプトの小さな違いがLLMにもたらすバタフライ効果を調査した結果]] | プロンプト微細変化の影響 |
| [[プロンプトの詳細さでLLMコード生成の精度はどこまで変わるか]] | プロンプト詳細度の影響検証 |
| [[プロンプト作成スキルを育てる研修設計の実践例]] | プロンプト教育の実践例 |
| [[プロンプトログをもとにLLMの使い方の変化を読み解く]] | ユーザーのプロンプト利用変化 |
| [[ユーザーによる「曖昧な指示」や「不十分な依頼」、コード生成にどう影響する]] | 曖昧な指示の影響検証 |
| [[大喜利で分かったLLMの笑いのクセ]] | LLMのユーモア理解分析 |
| [[推論特化型LLM（推論モデル）の弱点はどこか ステップ数より要件カバー率が成否を分ける]] | 推論モデルの弱点分析 |
| [[提言：LLMにおける通説への批判的検討]] | LLM通説への批判的検討 |
| [[構造化出力がLLMの推論能力に与える影響]] | 構造化出力と推論能力の関係 |
| [[直感に頼るようなタスクだとLLMに「ステップバイステップで考えて」は逆効果]] | CoTの逆効果ケース |
| [[確率的な「ゆらぎ」がLLMの創造性にもたらす影響]] | 温度パラメータと創造性の関係 |
| [[要約タスクで判明した”品質vs事実整合性”のトレードオフ]] | 要約における品質と事実性の関係 |
| [[複数の指示を同時に処理する際のLLMの限界]] | 同時指示処理の限界検証 |
| [[開発者が知っておくべき「LLMコードスメル」]] | LLM統合時のコードの悪習慣 |
| [[自信過剰になるLLM 長く考えさせることの副作用と検索機能が果たす役割]] | 長考による自信過剰と検索の役割 |

---

# 🛠 Prompt Engineering Component Library (Part 2)
*Last Updated: 2025-05-15*

> [!TIP] このライブラリの使い方 (Part 2)
> - Part 1 (Structure, Reasoning, Safety) に続き、最適化・エージェント・評価・背景知識を収録
> - **Synergy列**を参照し、Part 1の技術と組み合わせることで高度なメタプロンプトを構築可能
> - Dataviewクエリ例: `TABLE WHERE contains(Tag, "#Comp/Agent")`

---

## ⚡ Optimize & Efficiency (効率・最適化)

トークン数、応答速度、コストなどの**効率**を改善する技術群。

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMに何度も答えさせるコストを10分の1に削減する手法]] | #Comp/Optimize | **Adaptive Sampling** (確信度に応じた生成停止) | 多数決の計算コストを抑えたい時 | Self-Consistency, Ensemble |
| [[LLMに何度も答えさせるコストを10分の1に削減する手法]] | #Comp/Optimize | **Model Ensemble** (複数モデルの重み付け統合) | 複数モデルを効率よく組み合わせたい時 | Self-Consistency, Routing |
| [[LLMの「温度」どう設定すればよい 出力の揺らぎに影響する設定パラメーターを6能力で検証]] | #Comp/Optimize | **Temperature Tuning** (タスク別最適温度設定) | 創造性と正確性のバランス調整時 | Role-play, CoT |
| [[LLMコスト効率を高める「プロンプト圧縮」入門 比較で見える実践のポイント]] | #Comp/Optimize | **Prompt Compression** (冗長な情報の削除・要約) | 長文入力のコストを削減したい時 | Long Context, RAG |
| [[LLMへの入力プロンプトを「意味を保持したまま」高度に圧縮する技術『LLMLingua』]] | #Comp/Optimize | **LLMLingua** (予算コントローラーによる圧縮) | 意味を保ったままトークンを減らす時 | Long Context, RAG |
| [[Microsoftなどのプロンプト圧縮技術『LLMLingua-“2″』タスクの精度を維持したまま圧縮率2-5倍]] | #Comp/Optimize | **LLMLingua-2** (トークン分類による圧縮) | タスク非依存で汎用的に圧縮したい時 | RAG, ICL |
| [[RAG（検索拡張生成）において約半分のトークン数でタスクを実行できるフレームワーク『FIT-RAG』]] | #Comp/Optimize | **FIT-RAG** (サブドキュメント選択と削減) | RAGのトークン効率を上げたい時 | RAG, Document Scoring |
| [[RAGにおいて長文を検索することで一気に効率を上げるアプローチ『LongRAG』]] | #Comp/Optimize | **LongRAG** (長文検索単位の採用) | 検索負荷を下げつつ文脈を保つ時 | Long Context, RAG |
| [[学習なしでLLMを強くするための「文脈を育てる」という発想]] | #Comp/Optimize | **Mistake Notebook Learning** (失敗パターンの蓄積と再利用) | 追加学習なしで精度を上げたい時 | RAG, Few-shot |
| [[多くの「長いコンテキストを要するタスク」を、短いコンテキストウィンドウのLLMで解決する手法]] | #Comp/Optimize | **LC-Boost** (長文脈の分割統治処理) | 短いウィンドウで長文タスクを解く時 | RAG, Divide-and-Conquer |
| [[生成回数を増やすだけでLLMの性能が大幅に向上するシンプルな法則 実用上のポイント]] | #Comp/Optimize | **Repeated Sampling** (反復サンプリングによるカバレッジ向上) | 難問の正解率を底上げしたい時 | Self-Consistency, Verifier |
| [[既存のLLMを融合させて強力なモデルを作る手法「知識融合」]] | #Comp/Optimize | **Knowledge Fusion** (複数モデルの確率分布統合) | モデルを再学習せず強化したい時 | Ensemble, Distillation |
| [[長文脈タスクでもLLMの精度を下げないための対策]] | #Comp/Optimize | **Retrieval-then-Reasoning** (検索と推論の二段階分離) | 長文入力による精度低下を防ぐ時 | RAG, Long Context |

---

## 🔧 Agents & Tools (エージェント・自律動作)

外部ツール利用、自律的な計画、マルチエージェント連携を実現する技術群。

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[GPT-4との対話でタスクプランニングを行うロボットシステムフレームワークが発明されました。]] | #Comp/Agent | **Interactive Task Planning** (対話によるロボット操作計画) | 物理的なタスクを計画・実行させる時 | VLM, CoT |
| [[LLMエージェントが実行可能なPythonコードを生成するフレームワーク『CodeAct』]] | #Comp/Agent | **CodeAct** (実行可能Pythonコードによる行動) | ツール操作をコードで完結させたい時 | SELF-DEBUGGING, Tool Use |
| [[LLMエージェントに必要なメモリーの選び方と残し方 抽出と構造化で蓄積される記憶のかたち]] | #Comp/Agent | **Mem0 / Mem0g** (記憶の抽出とグラフ構造化) | 長期的な対話履歴を保持したい時 | RAG, Knowledge Graph |
| [[LLMにエピソード記憶のような能力を持たせるRAGのテクニック]] | #Comp/Agent | **Generative Semantic Workspace** (エピソード記憶の構造化) | 時系列や状態変化を追跡したい時 | RAG, Entity Summarization |
| [[LLMにハイレベルな問題の解決アプローチを自分で考えさせるエージェント化手法「SelfGoal」]] | #Comp/Agent | **SelfGoal** (ゴールツリーの動的構築) | 曖昧な目標を具体化して実行する時 | CoT, Hierarchical Planning |
| [[LLMに「信念・願望・意図」を実装 エージェントの頭の中を言語化する]] | #Comp/Agent | **BDI Model** (信念・願望・意図のオントロジー) | エージェントの行動原理を説明する時 | Role-play, Cognitive Architecture |
| [[なぜ、そのAIエージェントは失敗する？企業組織に学ぶ信頼できる「組織設計」の原則]] | #Comp/Agent | **Organizational Design** (役割分担と監督の原則) | 複数エージェントを堅牢に動かす時 | Multi-Agent, Standard Operating Procedure |
| [[プロンプトでLLMにRPAワークフローを自動生成させる手法「FlowMind」JPモルガン考案]] | #Comp/Agent | **FlowMind** (レクチャーレシピによるAPI操作) | RPAやAPI操作を自動化したい時 | CodeAct, Tool Use |
| [[ユーザーの指示が曖昧なとき、LLM側が確認を行うエージェントアーキテクチャ『Mistral-Interact』]] | #Comp/Agent | **Interactive Clarification** (曖昧性の検知と質問生成) | ユーザーの意図を明確にしたい時 | Role-play, Goal Setting |
| [[多様な業務データを統合してナレッジグラフを作成するLLM活用方法]] | #Comp/Agent | **Knowledge Graph Construction** (非構造データのグラフ化) | 組織内の情報を統合・活用したい時 | RAG, Entity Extraction |
| [[心の理論をLLMエージェントに実装することの効果]] | #Comp/Agent | **Hypothetical Minds** (他者意図の推論モジュール) | マルチエージェントでの協調・競争時 | ToT, Cognitive Modeling |
| [[本番環境で動くAIエージェントワークフローの作り方 9つのベストプラクティスで信頼性と保守性を実現]] | #Comp/Agent | **Agentic Workflow Patterns** (単一責任・ツール分離等) | 実用的なエージェントを構築する時 | Standard Operating Procedure, Docker |
| [[異なるLLMが円卓を囲み議論した結果の回答は品質が高いとの検証報告。円卓ツールも公開]] | #Comp/Agent | **Round-Table Debate** (異種モデル間の議論) | 一つの結論に収束させたい時 | Multi-Agent, Self-Consistency |
| [[脳に学ぶAIエージェントの理想形 ほか、週末読みたいAI科学ニュース]] | #Comp/Agent | **Brain-Inspired Architecture** (脳構造模倣エージェント) | 高度な自律性と学習能力を持たせる時 | Cognitive Architecture, Memory |

---

## 📊 Evaluation & Benchmarking (評価・測定)

出力品質の測定、改善、ベンチマークに関する技術群。

| Link | #Tag | 🔧 Component (Mechanism) | 🎯 Trigger (40文字以内) | 🔗 Synergy |
|:---|:---|:---|:---|:---|
| [[LLMによる回答を自動で評価する試み]] | #Comp/Eval | **LLM-as-a-Judge** (LLMによる自動採点) | 人手評価の代わりに出力を評価する時 | CoT, Rubric |
| [[Self-Reflection（自己反省）がLLMのパフォーマンスに与える影響を網羅的に調査]] | #Comp/Eval | **Performance Benchmarking** (自己反省手法の効果測定) | 最適な自己修正手法を選定する時 | Self-Reflection, CoT |
| [[RAGの失敗パターン7選と教訓9箇条]] | #Comp/Eval | **RAG Failure Analysis** (失敗パターンの分類と対策) | RAGシステムの弱点を診断する時 | RAG, Testing |
| [[プロンプト作成スキルを育てる研修設計の実践例]] | #Comp/Eval | **Prompt Evaluation Rubric** (プロンプト品質の多面評価) | プロンプト自体の良し悪しを測る時 | Meta-Prompting, Feedback |
| [[専門家が作成したプロンプトと同等以上の性能を達成する自動プロンプト生成手法『Minstriel』]] | #Comp/Eval | **Minstrel** (マルチエージェントによるプロンプト最適化) | 最適なプロンプトを自動生成したい時 | LangGPT, Multi-Agent |
| [[プロンプトを遺伝的アルゴリズムで自動最適化するプロンプトエンジニアリング手法『Promptbreeder（プロンプトブリーダー）』]] | #Comp/Eval | **Promptbreeder** (進化的アルゴリズムによる最適化) | 人手では思いつかないプロンプトを探す時 | Genetic Algorithm, Self-Reflection |
| [[要約の品質を評価する新たなツール「SEAHORSE」の登場]] | #Comp/Eval | **SEAHORSE Metrics** (6軸による要約品質評価) | 要約の品質を多角的に評価したい時 | Summarization, LLM-as-a-Judge |
| [[LLMの「知っているのに嘘をつく」幻覚と「知らないから間違える」幻覚の違い]] | #Comp/Eval | **WACK (Wrong Answers with Correct Knowledge)** (知識と幻覚の分別) | 幻覚の原因を特定・分類したい時 | Knowledge Probing, Hallucination Detection |

---

## 📚 Reference / Context (背景知識・その他)

具体的なプロンプト技術ではないが、設計思想や背景理解に役立つ情報群。

| Link | 概要 (30文字以内) |
|:---|:---|
| [[AIエージェントの制御方法を今から考えるべし]] | エージェント制御の将来課題 |
| [[LLMから見た人間の信頼性]] | LLMの人間に対する不信感の研究 |
| [[LLMの推論能力の本質]] | 推論か検索かの議論 |
| [[LLM開発トレンドに新たに見出された『密度化の法則』および『能力密度』の概念]] | モデル性能と密度の法則性 |
| [[LLMにおける通説への提言]] | LLMに関する通説の検証 |
| [[人間のカリキュラム教育のような学習でLLMの性能は向上するとの報告]] | カリキュラム学習の効果 |
| [[再現性のある人間行動シミュレーションへ LLMのふるまいを数値で制御する]] | 数値による行動制御の実験 |
| [[大規模言語モデルにおける課題と応用例を整理した結果]] | LLMの課題と応用分野の整理 |
| [[大規模言語モデルの”性格”特性を分析＆調整するフレームワークの登場]] | 性格特性の分析と調整 |
| [[大規模言語モデルへのプロンプト、重要な情報はどこに書く？]] | 情報配置位置の重要性 |
| [[使うたびにどんどん賢くなるQ&Aシステム生成AIツール]] | フィードバックによる継続改善 |
| [[人間の思考を模倣するAI学習フレームワーク「Thought Cloning」の登場]] | 思考模倣による学習フレームワーク |
| [[多様な役割のAIエージェント達に協力してソフトウェアを開発してもらう『ChatDev』登場。論文内容＆使い方を解説]] | マルチエージェント開発事例 |
| [[対話の中でユーザーの好みを学ぶ手法『CIPHER』 （プロンプトテンプレートあり）]] | ユーザー好みの学習手法 |
| [[推論能力をさらに強める戦略『AoT』で、LLMが「直感」に似た能力を示すようになった]] | アルゴリズム思考による推論強化 |
| [[検索結果をLLMでチェックして自動的に再検索する『MetaRAG』出力精度を大幅に向上]] | メタ認知による再検索 |
| [[次世代のQ&Aサービスへの道筋]] | Q&Aサービスの将来展望 |
| [[深層学習モデル作成において、LLMに「専門家として振る舞わせる」ことの有効性]] | 専門家ロールの有効性検証 |
| [[生成AIのパラドックス]] | 生成AIの思考プロセス仮説 |
| [[知識融合の方法論]] | 複数モデルの知識統合手法 |
| [[自己報酬言語モデルのフレームワーク]] | 自己報酬によるモデル改善 |
| [[自然言語タスクをコードタスクに変換してLLMに高度な推論を実行させる]] | コードによる推論の代替 |
| [[表とテキストを両方含むドキュメントからLLMで上手に情報抽出を行う手法]] | ハイブリッド文書からの抽出 |
| [[言葉で指示できる長時間シミュレーション用世界モデル]] | 世界モデルによるシミュレーション |
| [[認知科学が示す「LLMと人間の推論」における違いを性能向上に役立てる]] | 認知科学的アプローチによる推論 |
| [[論文の大規模データセット「unarXive 2022」登場！]] | 学術論文データセットの紹介 |
| [[詳しさと控えめな自信がいちばん意見を動かす]] | 説得力のある回答の特徴 |
| [[開かれたLLMの評価]] | オープンな評価手法の議論 |
| [[集団の知性を高めるAIエージェント]] | 集団知性へのAI応用 |
| [[隠れた意図を汲み取るエージェント]] | ユーザー意図の深層理解 |
| [[高速かつ高精度なRAG]] | RAGの高速化技術 |

---
# CONTEXT (背景)
あなたは {{Role-Prompting: 専門家の役割}} です。
現在、{{User Intent: タスクの目的}} を達成しようとしています。

# OBJECTIVE (目的)
あなたの目標は、ユーザーの入力に対して {{Effect: 期待される効果}} を実現することです。

# STYLE (スタイル)
{{EmotionPrompt: 感情的な刺激やトーン}} (例: 「深呼吸して、一歩ずつ論理的に考えてください」)
{{Politeness Policy: 丁寧さのレベル}}

# TONE (トーン)
{{MetaFaith: 自信の度合いに応じた表現}} (確信がない場合は正直に伝えること)

# AUDIENCE (対象読者)
{{Persona: 想定される読み手}} に合わせて回答してください。

# RESPONSE (応答フォーマット)
以下の **{{Recipe: 技術の組み合わせ}}** プロセスに従って回答を作成してください：

1. **Analysis & Planning (計画)**:
   - {{Self-Discover / SelfGoal}}: タスクをサブゴールに分解し、解決策を計画してください。
   
2. **Reasoning & Execution (推論・実行)**:
   - {{CoT / Logic-of-Thought}}: ステップバイステップで思考過程を出力してください。
   - {{RAG / CodeAct}}: 必要に応じて外部知識を検索するか、コードを実行して確認してください。

3. **Verification & Refinement (検証・改善)**:
   - {{Chain-of-Verification / SELF-DEBUGGING}}: 生成した内容を自己検証し、矛盾や誤りがあれば修正してください。
   - {{Self-Reflection}}: 最終的な回答が目的に合致しているか振り返ってください。

4. **Final Output (最終出力)**:
   - {{XML Delimiters / Structured Format}}: 最終的な回答を [OUTPUT] タグ内に、指定された形式で出力してください。

# CONSTRAINTS (制約)
- {{Negative Prompting: やってはいけないこと}}
- {{Prompt Compression: 出力長やトークン節約の指示}}