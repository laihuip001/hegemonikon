# ルールとワークフローのインポート計画

## ゴール
外部バックアップ（`G:\その他のパソコン\太郎`）からワークフロー定義をインポートし、さらに現在のコンテキスト（MEMORY）に存在するAI開発ルール（`GEMINI.md`）をファイルとして実体化させます。これにより、Forgeプロジェクトのルールと自動化プロセスを復元します。

## ユーザー確認事項
> [!NOTE]
> `G:` ドライブ上の `GEMINI.md` は空でしたが、ユーザー指示により、「このIDEのもの（MEMORYにある定義）」を正として `c:\Users\raikh\.gemini\GEMINI.md` に復元します。

## 変更内容

### 1. ディレクトリ作成
以下のディレクトリが存在しない場合、作成します。
- `c:\Users\raikh\.gemini\.agent\workflows`

### 2. ワークフローのインポート
`G:\その他のパソコン\太郎` から以下のファイルを `c:\Users\raikh\.gemini\.agent\workflows` にコピー（新規作成）します。

#### グローバルワークフロー
ソース: `G:\その他のパソコン\太郎\dev\.agent\workflows`
- [NEW] [do.md](file:///c:/Users/raikh/.gemini/.agent/workflows/do.md)
- [NEW] [flow-dev-ecosystem.md](file:///c:/Users/raikh/.gemini/.agent/workflows/flow-dev-ecosystem.md)
- [NEW] [global-rules.md](file:///c:/Users/raikh/.gemini/.agent/workflows/global-rules.md)

#### Forge ワークフロー
ソース: `G:\その他のパソコン\太郎\dev\Forge\.agent\workflows`
- [NEW] [update-manual.md](file:///c:/Users/raikh/.gemini/.agent/workflows/update-manual.md)



## 検証計画

### 手動検証
1. `c:\Users\raikh\.gemini\.agent\workflows` 内のファイル一覧を確認し、4つのワークフローファイルが存在することを確認する。
2. `c:\Users\raikh\.gemini\GEMINI.md` の内容を表示し、MEMORY内のルール（Forge Edition v1.0.0）と一致することを確認する。
