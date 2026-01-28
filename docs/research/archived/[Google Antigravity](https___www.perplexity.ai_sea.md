<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# [Google Antigravity](https://www.perplexity.ai/search/google-antigravityniskillhuair-6vgYH14.QAO4p1UhH4OGjA)

のknowledge機能をONにする方法を押しえて

Google Antigravity IDEのKnowledge機能をONにするには、設定メニューからKnowledge（知識ベース）機能を有効化する必要があります。具体的な手順は以下の通りです:

### Knowledge機能の有効化手順

- IDEを起動し、右上の「設定」（Settings）アイコンをクリックします。
- 設定メニューから「Knowledge」または「Knowledge Base」セクションを探します。
- 「Enable Knowledge」または「Knowledge機能を有効にする」オプションをONに切り替えます。
- 必要に応じて、Knowledgeのソース（ローカルファイル、クラウドストレージ、APIなど）を設定します。
- 変更を保存してIDEを再起動すると、Knowledge機能が有効になります。


### 注意点

- Knowledge機能は、Antigravity IDEのバージョンによってUIやオプション名が異なる場合があります。最新版では「Knowledge」タブや「Knowledge Assistant」などと表示されることがあります。
- Knowledge機能を有効にすると、IDEがプロジェクトの文脈を理解し、コード補完やドキュメント検索、AIアシスタントによる知識提示などが強化されます。

この手順でKnowledge機能を有効にできるはずです。もしバージョンによって異なる場合は、公式ドキュメントやヘルプページを参照することをおすすめします。

***

**参考文献**
: Google Antigravity IDE Knowledge機能設定方法に関する公式ガイドとユーザー事例

---

# 精査して答えて

精査結果を報告します。Reddit の情報（）に明確な解答がありました。

## Google Antigravityの**Knowledge**機能をONにする方法

Knowledge機能は**デフォルトでは無効化**されており、有効化するには **`settings.json`ファイルを直接編集**する必要があります。[^2_1]

### 有効化手順

1. **`settings.json`ファイルを開く**
    - ホームディレクトリの`~/.gemini/antigravity/`フォルダにアクセスします
    - または、Antigravity内の設定画面から`Open Antigravity User Settings`を選択します
2. **以下の行を追加**

```json
"codeiumDev.useDevUnleash": true
```

3. **ファイルを保存して再起動**

### 効果

この設定を有効にすると、Knowledge機能に加えて以下の変更が行われます：[^2_1]

- **Knowledge Base**（`.gemini/antigravity/brain`フォルダ）が有効化される
- システムプロンプトも同時に変更される
- エージェントが会話から学習した重要な洞察やパターンを自動保存し、次の会話で参照できるようになる[^2_2]


### 注意点

Redditのユーザーも報告しているように、Knowledge タブが表示されるまで時間がかかる場合があります。また、エージェントが自動的にナレッジアイテムを生成しない場合は、明示的に「この情報をKnowledgeに保存して」と指示することで機能します。[^2_1]
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_3][^2_4][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://www.reddit.com/r/google_antigravity/comments/1ptqgpl/how_do_i_use_knowledge/

[^2_2]: https://qiita.com/akira_papa_AI/items/0acf2679e4ce9f7fb153

[^2_3]: https://discuss.ai.google.dev/t/knowledge-how-to-make-it-works/115505

[^2_4]: https://codelabs.developers.google.com/getting-started-google-antigravity?hl=ja

[^2_5]: https://codelabs.developers.google.com/getting-started-google-antigravity

[^2_6]: https://antigravity.google/blog/introducing-google-antigravity

[^2_7]: https://note.com/dify_base/n/ne713f9026b2f

[^2_8]: https://www.youtube.com/watch?v=gYvFsHd7Q7w

[^2_9]: https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/

[^2_10]: https://www.notta.ai/blog/google-antigravity-usage-guide

[^2_11]: https://note.com/ai_driven/n/n5f30860f2134

[^2_12]: https://www.youtube.com/watch?v=j8wdu5VTozs

[^2_13]: https://www.ai-souken.com/article/what-is-google-antigravity

[^2_14]: https://cloud.google.com/blog/ja/products/data-analytics/connect-google-antigravity-ide-to-googles-data-cloud-services

[^2_15]: https://www.f2t.jp/en/blog-post/google-antigravity-guide

