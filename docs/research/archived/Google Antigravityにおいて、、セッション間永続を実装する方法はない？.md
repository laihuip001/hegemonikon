<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Google Antigravityにおいて、、セッション間永続を実装する方法はない？

ご質問ありがとうございます。検索結果から、Google Antigravityにおけるセッション間永続性の実装方法について、複数のアプローチが確認できました。[^1_1][^1_2]

## Antigravityでのセッション間永続性の実装方法

### 1. **ナレッジアイテム（Knowledge）機能**[^1_1]

Antigravityには**永続メモリシステム**として「ナレッジアイテム」があります。これはコーディングセッションから重要な洞察、パターン、解決策を自動的にキャプチャして整理するシステムです。セッション間でこれらの情報を参照できます。

### 2. **ADK（Agent Development Kit）の状態管理**[^1_2]

Google ADKを使用する場合、セッション間の永続性には特殊な状態キー接頭辞を使用できます：

```
- `user:` プレフィックス → 同じユーザーのすべてのセッション間で永続化
- `app:` プレフィックス → すべてのユーザーのすべてのセッション間で永続化
```

例：`user:dark-mode=true` のようなシンプルなテキスト設定をセッション間で保持できます。[^1_2]

### 3. **データベースセッションサービス**[^1_3][^1_4]

本番環境では、ADKの**DatabaseSessionService**を使用してセッションデータをSQLiteなどのデータベースに永続化します：

```python
# SQLiteデータベースにセッションを保存
from google.adk.sessions.database_session_service import DatabaseSessionService

session_service = DatabaseSessionService(
    database_url="sqlite:///./sessions.db"
)
```

保存構造：

```
./session_data/
└── app_name/
    └── user_id/
        └── session_id/
            └── session.json
```


### 4. **Vertex AI Session Service**[^1_2]

Google Cloudの本番環境では、**VertexAISessionService**を使用してセッションデータをAgent Engineに保存できます。

### 5. **Document \& Clearメソッド**[^1_5]

複雑なタスクでは「Document \& Clear」メソッドを使用して、永続的な外部「メモリ」を作成することが推奨されています。

## 実装時の注意点

- デフォルトではセッション状態はメモリ内のみ保存されます
- Antigravityが再起動するとすべてのセッションデータが失われます
- 本番運用では必ずデータベースまたはクラウドストレージへの永続化が必要です[^1_2]
- セッションの自動クリーンアップ（TTL設定）を検討してください[^1_4]

ご不明な点がありましたら、さらに詳しい実装例をお示しすることもできます。どの実装方法についてさらに詳しく知りたいですか？
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://note.com/ai_driven/n/n5f30860f2134

[^1_2]: https://cloud.google.com/blog/ja/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk

[^1_3]: https://saptak.in/writing/2025/05/10/google-adk-masterclass-part6

[^1_4]: https://www.linkedin.com/pulse/extending-google-adk-persistent-storage-practical-guide-consonni-2j36f

[^1_5]: https://unikoukokun.jp/n/nd096dd7d4e42

[^1_6]: https://arxiv.org/html/2401.10954v2

[^1_7]: https://arxiv.org/abs/1104.4982

[^1_8]: http://arxiv.org/pdf/2409.18145.pdf

[^1_9]: https://arxiv.org/pdf/2501.10589.pdf

[^1_10]: https://www.reddit.com/r/ClaudeAI/comments/1p1w6am/i_tried_google_antigravity_dont_do_it/

[^1_11]: https://developers.gnavi.co.jp/entry/adventcalendar-251210-1/

[^1_12]: https://www.ai-souken.com/article/what-is-google-antigravity

[^1_13]: https://qiita.com/ma7ma7pipipi/items/90f13f3e7133551a55b2

[^1_14]: https://zenn.dev/oikon/articles/claude-code-2

[^1_15]: https://unikoukokun.jp/n/n543f089015d4

[^1_16]: https://qiita.com/aoinakanishi/items/6661581c36631c8f4431

[^1_17]: https://exbk.jp/5435/

[^1_18]: https://zenn.dev/nono0601/articles/a2ca2a36bd735f

[^1_19]: https://github.com/Chainlit/chainlit/issues/782


---

# Perplexityへの調査依頼

以下の質問をPerplexityに投げてください:
質問1: ナレッジアイテム機能
Google Antigravity IDE (Jules/Gemini in VS Code) において:

- 「ナレッジアイテム (Knowledge Items)」機能は実際に存在するか？
- 存在する場合、どのように作成・参照するか？
- エージェント（AI）側からプログラム的にアクセスできるか？
質問2: 状態プレフィックス
Google ADK (Agent Development Kit) の user: / app: プレフィックス機能について:
- これはAntigravity IDE内で使用可能か？
- IDE環境（VS Code拡張）でセッション状態を永続化する具体的方法は？
- テキストファイルやJSONを保存する以外に、ネイティブの状態ストアはあるか？
質問3: 会話履歴の永続性
Antigravity IDEにおいて:
- 過去の会話履歴はどこに保存されているか？
- エージェントが過去の会話を参照する方法はあるか？
- "conversation_summaries" のような過去セッション参照APIは存在するか？
質問4: DatabaseSessionService
Google ADKのDatabaseSessionServiceについて:
- これはAntigravity IDE（VS Code拡張）環境で使用可能か？
- ローカルのSQLiteをセッションストアとして使う設定方法は？
- Antigravity内部でアクセス可能なセッションIDやユーザーIDはあるか？

調査結果をまとめました。ご質問の4つの項目について、詳細な回答をいたします。

***

# Google Antigravity IDE セッション永続性 調査報告書

## 質問1: ナレッジアイテム機能[^2_1][^2_2][^2_3]

### 存在状況

ナレッジアイテム機能は**ドキュメント上では存在**します。Antigravityの公式ブログ「Self-improvement」セクションで、「エージェントが過去の作業とユーザーフィードバックから学習し、ナレッジベースに貢献する」メカニズムとして説明されています。ただし**実装は不完全な状態**です。[^2_2][^2_1]

### 作成・参照方法

- **手動UI**: Settings → Knowledge Base で確認・編集可能[^2_4]
- **自動作成**: ドキュメントでは「自動生成される」と記載されるも、ユーザーから実際の動作が観察されていないという報告が複数存在[^2_2]
- **保存位置**: `~/.gemini/antigravity/brain` ディレクトリ[^2_5][^2_2]


### エージェント側からのプログラムアクセス

**アクセス不可**。システムプロンプトにナレッジアイテムへの言及がないことが確認されており、モデル側から直接アクセスするAPIは公開されていません。[^2_2]

***

## 質問2: 状態プレフィックス（user:/app:）機能[^2_6][^2_7][^2_8]

### ADK内での機能

Google ADKでは**完全に実装**されています。以下のプレフィックスがサポートされます：


| プレフィックス | スコープ | 永続性（DatabaseService時） | 用途例 |
| :-- | :-- | :-- | :-- |
| なし（プレフィックスなし） | 現在のセッションのみ | セッション固有 | タスク進捗追跡 |
| `user:` | ユーザーID単位（全セッション） | 永続 | ユーザー言語設定、プロフィール |
| `app:` | アプリケーション全体 | 永続 | APIエンドポイント、グローバル設定 |
| `temp:` | 単一invocation | 自動削除 | 一時計算結果 |

### Antigravity IDE環境での可用性

**使用不可**。Antigravity IDEはVSCodeフォークにGemini Gemini統合を施したスタンドアロンアプリケーションであり、ADKの`SessionService`層を公開していません。IDE環境ではセッション状態管理がローカルファイルシステムに限定されています。[^2_9][^2_10]

### IDE環境でのネイティブ状態ストア

テキストファイル（JSON、Markdown）以外に、ネイティブの状態ストアは公開されていません。

***

## 質問3: 会話履歴の永続性[^2_11][^2_12][^2_13]

### 保存場所

会話履歴はローカルファイルシステムに保存されます：

```
~/.gemini/antigravity/conversations/    # セッション会話データ
~/.gemini/antigravity/brain/             # ナレッジアイテム
~/.gemini/GEMINI.md                      # グローバルルール
```


### エージェント参照メカニズム

新規セッション開始時、システムが最直近20セッションの**要約（約3-4行）**を自動的にフィーストメッセージに挿入します。セッションIDが要約に含まれており、理論的には完全なトランスクリプト取得は可能ですが、実装確認はされていません。[^2_11][^2_2]

### 過去セッション参照API

`conversation_summaries`のような**専用APIは存在しません**。参照メカニズムは要約インジェクションに限定されています。

***

## 質問4: DatabaseSessionService[^2_14][^2_15][^2_16][^2_17]

### Antigravity IDE内での使用可能性

**使用不可**。DatabaseSessionServiceはGoogle ADKの下位層インターフェースであり、Antigravity IDE内から直接呼び出すことはできません。

### ADK開発環境での設定方法（Antigravity外）

ADK統合開発環境でセッションをSQLiteに永続化する場合：

```python
from google.adk.sessions import DatabaseSessionService

# 重要: SQLiteの場合、aiosqlite（非同期ドライバ）を使用
db_url = "sqlite+aiosqlite:///./session_data.db"
session_service = DatabaseSessionService(db_url=db_url)
```

作成されるテーブル：

```
- sessions      (セッションメタデータ)
- user_state    (user:プレフィックス付きデータ)
- app_state     (app:プレフィックス付きデータ)
- raw_events    (全イベント・ツール呼び出し履歴)
```


### Antigravity IDE内のセッション情報アクセス

Antigravity IDEが公開するセッションID・ユーザーIDへのプログラム的アクセス方法は**ありません**。ローカルファイルは保存されますが、APIとして提供されていません。

***

## 結論

Antigravity IDEの現在の制限：

1. **ナレッジアイテム機能**は未完全実装で、自動作成・参照は実用レベルでない
2. **状態管理**はADKレベルの抽象化ではなく、ローカルファイルに依存
3. **会話履歴**はセッション要約のみ自動参照され、完全なトランスクリプトAPIはない
4. **DatabaseSessionService**はADK開発環境でのみ利用可能

本格的なセッション永続化が必要な場合は、別途ADK開発環境での実装か、IDEの自動保存ファイルをカスタム処理する必要があります。

***

**参考文献**
Antigravity Blog - Self-improvement[^2_18][^2_1]
Antigravity Beginner's Guide[^2_19][^2_3]
Reddit - Has anyone seen Knowledge Items[^2_20][^2_2]
Google AI Developers Forum[^2_21][^2_4]
Reddit conversation[^2_22][^2_5]
Google Cloud Blog - Agent State[^2_23][^2_6]
Google ADK Docs - State[^2_24][^2_7]
ADK Sessions, State \& Memory[^2_25][^2_8]
Qiita - Antigravity vs VS Code[^2_26][^2_9]
Reddit - Antigravity IDE review[^2_27][^2_10]
Reddit - Conversation history context[^2_28][^2_11]
Google AI Forum - Delete conversation[^2_12][^2_21]
GitHub issue - Chat persistence[^2_29][^2_13]
ADK Masterclass - Database Sessions[^2_14][^2_11]
LinkedIn - Building Persistent Sessions[^2_30][^2_15]
YouTube - SQLite storage for ADK[^2_31][^2_16]
ADK Docs - SessionService Overview[^2_32][^2_17]
<span style="display:none">[^2_33][^2_34][^2_35][^2_36][^2_37][^2_38][^2_39][^2_40][^2_41][^2_42][^2_43][^2_44][^2_45][^2_46][^2_47][^2_48][^2_49][^2_50][^2_51][^2_52][^2_53][^2_54][^2_55][^2_56][^2_57][^2_58][^2_59][^2_60]</span>

<div align="center">⁂</div>

[^2_1]: https://arxiv.org/html/2401.10954v2

[^2_2]: http://arxiv.org/pdf/2409.18145.pdf

[^2_3]: https://arxiv.org/abs/1104.4982

[^2_4]: https://arxiv.org/pdf/2501.10589.pdf

[^2_5]: https://note.com/ai_driven/n/n5f30860f2134

[^2_6]: https://www.reddit.com/r/ClaudeAI/comments/1p1w6am/i_tried_google_antigravity_dont_do_it/

[^2_7]: https://developers.gnavi.co.jp/entry/adventcalendar-251210-1/

[^2_8]: https://cloud.google.com/blog/ja/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk

[^2_9]: https://www.ai-souken.com/article/what-is-google-antigravity

[^2_10]: https://qiita.com/ma7ma7pipipi/items/90f13f3e7133551a55b2

[^2_11]: https://saptak.in/writing/2025/05/10/google-adk-masterclass-part6

[^2_12]: https://unikoukokun.jp/n/nd096dd7d4e42

[^2_13]: https://zenn.dev/oikon/articles/claude-code-2

[^2_14]: https://unikoukokun.jp/n/n543f089015d4

[^2_15]: https://www.linkedin.com/pulse/extending-google-adk-persistent-storage-practical-guide-consonni-2j36f

[^2_16]: https://qiita.com/aoinakanishi/items/6661581c36631c8f4431

[^2_17]: https://exbk.jp/5435/

[^2_18]: https://antigravity.google/blog/introducing-google-antigravity

[^2_19]: https://help.apiyi.com/google-antigravity-ai-ide-beginner-guide-2025-en.html

[^2_20]: https://www.reddit.com/r/google_antigravity/comments/1p7h6yl/has_anyone_seen_it_use_knowledge_items/

[^2_21]: https://discuss.ai.google.dev/t/how-to-delete-conversation-antigravity/114671

[^2_22]: https://www.reddit.com/r/google_antigravity/comments/1pi6tsa/dont_use_antigravity_conversation_and_files/

[^2_23]: https://cloud.google.com/blog/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk

[^2_24]: https://google.github.io/adk-docs/sessions/state/

[^2_25]: https://arjunprabhulal.com/adk-sessions-state/

[^2_26]: https://qiita.com/00b012deb7c8/items/5f9c333e33cc94c11144

[^2_27]: https://www.reddit.com/r/ChatGPTCoding/comments/1p35bdl/i_tried_googles_new_antigravity_ide_so_you_dont/

[^2_28]: https://www.reddit.com/r/google_antigravity/comments/1pc6qa4/ysk_antigravity_will_provide_all_of_your/

[^2_29]: https://github.com/google-gemini/gemini-cli/issues/5930

[^2_30]: https://www.linkedin.com/pulse/building-persistent-sessions-google-adk-comprehensive-juan-carlos-ixave

[^2_31]: https://www.youtube.com/watch?v=yuvDbpOa3b0\&vl=ja

[^2_32]: https://google.github.io/adk-docs/sessions/session/

[^2_33]: http://arxiv.org/pdf/2312.11805.pdf

[^2_34]: http://arxiv.org/pdf/2412.00707.pdf

[^2_35]: http://arxiv.org/pdf/2411.09224.pdf

[^2_36]: http://arxiv.org/pdf/2403.05530.pdf

[^2_37]: https://arxiv.org/pdf/2405.08704.pdf

[^2_38]: https://arxiv.org/pdf/2107.03374.pdf

[^2_39]: http://arxiv.org/pdf/2405.03162.pdf

[^2_40]: https://dl.acm.org/doi/pdf/10.1145/3613904.3642239

[^2_41]: https://zenn.dev/miz_1123/articles/ea8bb8a5811307

[^2_42]: https://www.youtube.com/watch?v=vjMqV5awh80

[^2_43]: https://www.youtube.com/watch?v=QOpfCGa_2SU

[^2_44]: https://google.github.io/adk-docs/artifacts/

[^2_45]: https://dev.to/willvelida/how-to-store-chat-history-using-external-storage-in-microsoft-agent-framework-3io2

[^2_46]: https://news.ycombinator.com/item?id=45967814

[^2_47]: https://www.reddit.com/r/google_antigravity/comments/1p8rw3r/does_antigravity_keep_memory_across_conversations/

[^2_48]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^2_49]: https://vertu.com/ai-tools/google-antigravity-vibe-coding-gemini-3-pro-developer-guide-claude-code-comparison/

[^2_50]: http://arxiv.org/pdf/2405.01470.pdf

[^2_51]: https://www.aclweb.org/anthology/D18-1076.pdf

[^2_52]: https://aclanthology.org/2022.findings-emnlp.247.pdf

[^2_53]: https://arxiv.org/html/2405.05038v3

[^2_54]: http://arxiv.org/pdf/2503.12370.pdf

[^2_55]: https://antigravity.google/docs/rules-workflows

[^2_56]: https://www.youtube.com/watch?v=wVSkfz9wHlw

[^2_57]: https://discuss.ai.google.dev/t/antigravity-knowledge-items-prbl/111234

[^2_58]: https://www.youtube.com/watch?v=gd8YgIau3Lw

[^2_59]: https://www.youtube.com/watch?v=yuvDbpOa3b0\&vl=it

[^2_60]: https://www.leoniemonigatti.com/blog/building-ai-agents-with-google-adk.html

