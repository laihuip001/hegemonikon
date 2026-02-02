<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# PreplexityにPC上のローカルファイルを参照させることは可能？

可能です。ただし「PC内の任意フォルダを常時スキャンして参照」ではなく、**アップロード（添付）**したローカルファイルの内容を、そのスレッド内の文脈として参照する形になります。[^1_1][^1_2]

## ローカルファイルを参照させる方法

- 新規スレッド開始時に検索バーの「+ Attach」からファイルを添付するか、ドラッグ＆ドロップでファイル（場合によってはフォルダも）を追加できます。[^1_1]
- 添付したファイル内容を読み取り、そのスレッド内の質問への回答に反映します（長いファイルは重要部分を抽出して扱うことがあります）。[^1_1]


## アップロード上限（目安）

- 1回で最大10ファイルまで添付できます。[^1_1]
- 1ファイルあたりのサイズ上限は40MBです。[^1_1]


## 「PCのローカル」を直接参照できない点

- PerplexityがPCのローカルディスクを勝手に巡回して読む、という使い方はできず、参照させたいファイルは都度添付（アップロード）する必要があります。[^1_1][^1_2]
- 添付型の「File upload」はスレッドで一時的に使う用途で、組織全体の検索（Internal Knowledge Search）とは扱いが異なります。[^1_2]


## 代替：クラウド連携（Pro/Enterprise）

- ProでもGoogle Drive等の「File App Connectors」を接続して、そこからファイルを選んで添付できますが、現時点ではProでは“同期（元ファイル更新の自動反映）”はサポートされず、更新内容を反映したい場合は再アップロードが必要です。[^1_3]
- Enterprise ProではGoogle Drive / OneDrive / SharePoint / Dropbox / Boxなどのコネクタが案内されています。[^1_4]

使いたい環境は「Web版（ブラウザ）」ですか、それとも「デスクトップ/モバイルアプリ」ですか？用途に合わせて最短手順を具体的に案内できます。
<span style="display:none">[^1_10][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://www.perplexity.ai/help-center/en/articles/10354807-file-uploads

[^1_2]: https://www.perplexity.ai/help-center/en/articles/10352914-what-is-internal-knowledge-search

[^1_3]: https://www.perplexity.ai/help-center/en/articles/11185364-file-app-connectors-for-perplexity-pro-subscribers

[^1_4]: https://www.perplexity.ai/help-center/en/articles/10672063-introduction-to-file-connectors-for-enterprise-organizations

[^1_5]: https://www.perplexity.ai/help-center/en/collections/8935812-file-uploads-file-app-connectors

[^1_6]: https://www.perplexity.ai/help-center/en/articles/10354810-security-and-privacy-with-file-uploads

[^1_7]: https://www.perplexity.ai/help-center/en/articles/12053065-enterprise-organization-permissions

[^1_8]: https://www.perplexity.ai/help-center/en/articles/12009761-enterprise-file-limits

[^1_9]: https://www.perplexity.ai/hub/blog/getting-started-with-perplexity

[^1_10]: https://www.perplexity.ai/help-center/en/collections/15347354-app-connectors


---

# デスクトップ

添付する以外の方法はない？
最悪GitHubのレポジトリでもいい

デスクトップでも「添付」以外の方法はありますが、現実的な選択肢は **(1) コネクタ（クラウド）**、(2)（Macのみ）ローカルMCP、(3)（条件付きで）GitHub です。[^2_1][^2_2]

## 添付以外の選択肢

- クラウドストレージをPerplexityに接続する「File App Connectors」を使う方法があります。[^2_1]
- もう1つは、PerplexityのMacアプリで「Local MCP」を有効化し、ローカルディレクトリ（の一部）へアクセスさせる方法です。


## Macならローカル参照（Local MCP）

- Local MCPは「PC上のファイル/DB/アプリ等」に対して操作・検索などを行える仕組みで、Perplexityへ送るデータを最小限にする、という位置づけです。
- 現時点でPerplexityがサポートしているLocal MCPはmacOS（Mac App Store版のMacアプリ）で、Remote MCPは今後提供予定とされています。
- 例として「Filesystem Access」MCPを使うと、ローカルの特定ディレクトリ配下を読み取り・検索できると案内されています。


## GitHubを使う場合

- **Enterprise（Enterprise Pro/Max）** なら「GitHub Connector」を有効化して、GitHubリポジトリをPerplexity内で横断的に検索・活用できます。[^2_2]
- 一方で、このGitHub Connector自体はEnterprise限定です（個人のPro契約だけだと基本的に使えません）。[^2_2]
- Enterpriseで有効化する場合は、SettingsのConnectorsからGitHubをEnable→GitHubでAuthorize、という手順が案内されています。[^2_2]


## Pro（個人）で現実的な代替

- Pro（個人）なら、GitHubではなくGoogle Drive等の「File App Connectors」をつないで、必要なファイルを選んでスレッドで使うのが現実的です。[^2_1]
- ただしProでは「ファイル同期（元ファイル更新の自動反映）」がサポートされておらず、更新した内容を反映したい場合は再アップロード（再添付）が必要とされています。[^2_1]

使っているのは **macOS**（Perplexity Macアプリが入れられる）ですか、それとも **Windows** ですか？ OSが分かると、最短ルート（Local MCPに行けるか／クラウドコネクタで組むか）を具体的に手順化できます。
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_3][^2_4][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://www.perplexity.ai/help-center/en/articles/11185364-file-app-connectors-for-perplexity-pro-subscribers

[^2_2]: https://www.perplexity.ai/help-center/en/articles/10354807-file-uploads

[^2_3]: https://www.perplexity.ai/help-center/en/articles/11502712-local-and-remote-mcps-for-perplexity

[^2_4]: https://www.perplexity.ai/help-center/en/articles/10672063-introduction-to-file-connectors-for-enterprise-organizations

[^2_5]: https://www.perplexity.ai/hub/getting-started

[^2_6]: https://www.perplexity.ai/help-center/en/articles/11185411-faq-file-app-connectors-for-pro-subscribers

[^2_7]: https://www.perplexity.ai/help-center/en/articles/12275669-github-connector-for-enterprise

[^2_8]: https://comet-help.perplexity.ai/en/articles/12867415-comet-assistant-privacy-data-use

[^2_9]: https://www.perplexity.ai/help-center/en/articles/11172798-getting-started-with-comet

[^2_10]: https://www.perplexity.ai/help-center/en/articles/12167711-linear-connector-for-enterprise

[^2_11]: https://www.perplexity.ai/help-center/en/articles/10354769-what-is-a-thread

[^2_12]: https://www.perplexity.ai/help-center/en/articles/10354775-technical-capabilities-of-threads

[^2_13]: https://www.perplexity.ai/hub/blog/getting-started-with-perplexity

[^2_14]: https://www.perplexity.ai/hub/blog/introducing-the-perplexity-search-api

[^2_15]: https://www.perplexity.ai/help-center/en/articles/10352903-what-is-pro-search

[^2_16]: https://www.perplexity.ai/help-center/en/articles/10352895-how-does-perplexity-work

[^2_17]: https://www.perplexity.ai/hub/blog/perplexity-pages

[^2_18]: https://www.perplexity.ai/hub/blog/introducing-comet


---

# Windows

可能な方法と詳細な実装手順を教えて

**Windowsの場合、残念ながら Local MCP はサポートされていません**（macOS のみ）。[^3_1]

その代わり、現実的な方法は以下の2つです：

***

## **方法1：クラウドストレージコネクタ（現実的）**

### 対応プラン

- **Pro（個人）**：Google Drive / Dropbox のみ
- **Enterprise Pro/Max**：Google Drive / OneDrive / SharePoint / Dropbox / Box


### Windowsデスクトップでの実装手順（Pro の場合）

#### **Step 1: Google Drive / Dropbox にファイルをアップロード**

1. ファイルを Google Drive または Dropbox に配置
2. クラウドストレージ内で管理・整理

#### **Step 2: Perplexity Web版でコネクタを有効化**

**⚠️ 重要：Windowsデスクトップアプリではなく、ブラウザ版を使用してください**
（Windows デスクトップアプリはコネクタ機能をサポートしていません）[^3_2]

1. `https://www.perplexity.ai` にブラウザでアクセス
2. **Settings**（画面左下、ユーザー名メニュー）を開く
3. 左サイドバーから **Connectors** を選択
4. 「Google Drive」または「Dropbox」を探して **Enable** をクリック
5. クラウドストレージのアカウント認証画面が出るので、ログイン
6. Perplexity への権限を付与（ファイルアクセス許可）
7. 成功すると **Connected** と表示される

#### **Step 3: ファイルを選択してスレッドで使用**

**方法A：ソースとして有効化**

1. 新規スレッド作成時に、チャット入力ボックス上の **Sources** (またはプラス記号)から、接続したクラウドストレージを選択
2. 特定のフォルダ・ファイルを指定
3. 質問を入力すると、そのファイルを参照して回答

**方法B：ファイル添付として使用**

1. スレッド内で「**Attach**」または「**File Attachments**」をクリック
2. Google Drive / Dropbox のファイル一覧から選択
3. 質問に含める

### 注意点

- **Pro では ファイル同期がない**：元ファイルを編集しても自動反映されず、再度アップロードが必要 [^3_3][^3_4]
- **Spaces との連携不可**：Pro ではコネクタは個人スレッド内でのみ利用可能 [^3_3]
- **ブラウザ版のみ**：Windows デスクトップアプリでは使用不可 [^3_2]

***

## **方法2：GitHub リポジトリ（制限あり）**

### 対応プラン

- **Enterprise Pro/Max のみ** [^3_5]
- 個人の Pro では使用不可


### GitHub を使いたい場合の代替案

個人 Pro なら、GitHub 上のファイルを「**URL 参照**」として活用：

1. GitHub でファイルを Raw 形式で表示
    - 例：`https://raw.githubusercontent.com/[ユーザー]/[リポジトリ]/[ブランチ]/[ファイルパス]`
2. その URL をPerplexity の質問内に貼り付けるか、Perplexity が自動的に URL 先のコンテンツを取得できるか確認
    - 実装方法は試行が必要

***

## **Windows での推奨フロー**

```
Windowsローカルファイル
    ↓
① Google Drive/Dropbox にアップロード（手動 or 同期フォルダ使用）
    ↓
② ブラウザで Perplexity にアクセス
    ↓
③ Settings → Connectors で Google Drive/Dropbox を有効化
    ↓
④ スレッドで接続ファイルを Sources か Attachments として使用
```


### 効率化のコツ

- **Dropbox や Google Drive の同期フォルダ** を使うと、PCローカルフォルダが自動的にクラウドに反映される
    - PC上の `C:\Users\[ユーザー名]\Dropbox\` など
    - ファイルを同期フォルダに置く → Dropbox が自動的に cloud にアップロード → Perplexity で参照可能

***

## 使用プランの確認

使っているのは **Pro（個人）** ですか、それとも **Enterprise** ですか？
Enterprise なら GitHub や SharePoint など追加の選択肢が増えます。
<span style="display:none">[^3_10][^3_11][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://www.perplexity.ai/help-center/en/articles/11502712-local-and-remote-mcps-for-perplexity

[^3_2]: https://www.perplexity.ai/help-center/en/articles/13014066-microsoft-onedrive-connector

[^3_3]: https://www.perplexity.ai/help-center/en/articles/11185364-file-app-connectors-for-perplexity-pro-subscribers

[^3_4]: https://www.perplexity.ai/help-center/en/articles/11185411-faq-file-app-connectors-for-pro-subscribers

[^3_5]: https://www.perplexity.ai/help-center/en/articles/12275669-github-connector-for-enterprise

[^3_6]: https://www.perplexity.ai/help-center/en/articles/12569435-how-to-use-the-microsoft-sharepoint-connector

[^3_7]: https://www.perplexity.ai/help-center/en/articles/10672063-introduction-to-file-connectors-for-enterprise-organizations

[^3_8]: https://www.perplexity.ai/help-center/en/collections/8935108-perplexity-pro-and-max

[^3_9]: https://www.perplexity.ai/hub/blog/introducing-internal-knowledge-search-and-spaces

[^3_10]: https://www.perplexity.ai/help-center/en/articles/13130932-using-the-box-connector

[^3_11]: https://www.perplexity.ai/help-center/en/collections/15347354-app-connectors


---

# pro

つまりGoogleドライブしか方法がない？

結論から言うと、**Pro（個人）ユーザーが「PCローカルの大量ファイル」を継続的に扱いたい場合、実質的な選択肢は：**

- **Google Driveコネクタ**
- **Dropboxコネクタ**

の2つだけです。[^4_1][^4_2][^4_3]

***

## Proで使えるファイル系コネクタ

公式ヘルプでは、Pro向けのファイルコネクタは次の2種と明記されています。[^4_1]


| プラン | 利用できるファイルコネクタ |
| :-- | :-- |
| Pro / Max | Google Drive, Dropbox[^4_1][^4_2] |
| Enterprise Pro / Max | Google Drive, Dropbox, OneDrive, SharePoint, Box など[^4_4][^4_5][^4_6] |

つまり、**個人Proの場合は「Google Drive か Dropbox」以外に、クラウドストレージをPerplexityに直結する方法はありません。**

***

## あなたのケース（Windows + Pro）で現実的な構成

### 1. クラウドストレージ側

どちらか好きな方でOKです。

- **Google Drive**
    - Pro / Max / Enterprise 全プランで利用可能[^4_3]
    - ドキュメント類やスプレッドシート中心なら相性が良い
- **Dropbox**
    - Pro / Max / Enterprise 全プランで利用可能[^4_2]
    - ファイルサーバーっぽくフォルダ構成で使いたいならこちらでも良い

Windows側は、どちらも「同期クライアント」を入れておけば、
`C:\Users\<ユーザー>\Google Drive\` や `C:\Users\<ユーザー>\Dropbox\` に置いたファイルが自動的にクラウドと同期されます。

### 2. Perplexity側（ブラウザ版での設定）

1. ブラウザで `https://www.perplexity.ai` を開く
2. 右上 or 左下のアイコンから **Settings** を開く
3. 左メニューで **Connectors** を選択
4. 一覧から
    - **Google Drive** または
    - **Dropbox**
を探して **Enable** をクリック[^4_1][^4_2][^4_3]
5. 連携したいアカウントでログインし、アクセス権限を許可
6. 成功するとステータスが **Connected** になる

※注意：
Google Drive / Dropbox コネクタは、**Webブラウザ版のみサポート**で、
Windowsデスクトップアプリ・モバイルアプリでは使えません。[^4_2][^4_6]

### 3. 実際にファイルを検索に使う方法

#### パターンA：検索ソースとして使う

1. 新規スレッド作成画面で、入力欄の上にある **Sources**（または「Set sources for search」）をクリック
2. Web / Academic に加えて、**Google Drive** や **Dropbox** をオンにする
3. 「このフォルダ配下だけ」など、必要に応じて範囲を指定（高精度検索の設定がある場合）
4. 通常どおり質問を書く
例：「このプロジェクトフォルダの設計書を前提に、仕様の抜け漏れをチェックして」

→ Perplexityが、接続されたDrive/Dropbox内の対象ファイルを横断的に見て回答します。[^4_1][^4_2][^4_3]

#### パターンB：特定ファイルを添付して使う

1. スレッドの入力欄下にある **File Attachments** / 「添付」ボタンをクリック
2. 「My device」ではなく **Google Drive / Dropbox** を選択
3. 目的のファイルを選んで添付
4. 「この添付の仕様書を要約して」「この設計とコードの差分を洗い出して」などと質問

→ 添付したファイルの中身を重点的に使って回答します。[^4_1][^4_2]

***

## Proでの制約ポイント（重要）

- **同期の自動反映（Proでは限定的）**
    - 古い説明では「同期なし、更新時は再アップロード必要」とありますが[^4_1]、
    - 新しいGoogle Drive / Dropboxのコネクタは、選択したファイルを「同期」して検索対象にする仕組みがあり、ファイルの更新も自動反映されます。ただし、
        - 高精度検索用に「どのファイル・フォルダを同期するか」を自分で選ぶ必要があります[^4_2][^4_3]
        - Enterpriseほど柔軟なMy Files / Spaces連携は使えません[^4_3]
- **Windowsデスクトップアプリではコネクタ非対応**
    - OneDriveコネクタの説明に「WindowsアプリやMacアプリ、モバイルアプリではコネクタは使えず、ブラウザ版が必要」と明記されています[^4_6]
    - Dropboxコネクタも同様の記述があります[^4_2]
→ 実質「**ブラウザ版Perplexity + Google Drive or Dropbox**」が正解構成です。
- **ローカルフォルダそのものを直接クロールする手段はない**
    - MCPのローカル接続はmacOSのみ[^4_7]
    - Windowsローカルの任意フォルダをPerplexityが直接クロールする仕組みは、現状提供されていません。

***

## まとめ

- ProユーザーがWindowsで「ローカルファイルをほぼ自動的に参照させたい」場合、
    - **Google Drive**
    - **Dropbox**
のどちらかを同期フォルダとして使い、
そこをPerplexityの**コネクタ**としてつなぐのが、現時点でのベストプラクティスです。[^4_1][^4_2][^4_3]
- もし「ソースコード中心で、GitHubリポジトリを丸ごと読ませたい」レベルまで踏み込みたいなら、
→ そのときは **Enterprise Pro/Max + GitHubコネクタ** を検討、という位置づけになります。[^4_8][^4_4]

***

「こういうフォルダ構成・ファイル種別（例：ソースコード+設計書+議事録）」で運用したい、など具体的なユースケースがあれば、それに合わせた

- Drive/Dropboxのフォルダ設計
- Perplexityでの検索プロンプトの型（テンプレ）
まで一緒に設計できます。
<span style="display:none">[^4_10][^4_11][^4_12][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: https://www.perplexity.ai/help-center/en/articles/11185364-file-app-connectors-for-perplexity-pro-subscribers

[^4_2]: https://www.perplexity.ai/help-center/en/articles/13060839-using-the-dropbox-connector

[^4_3]: https://www.perplexity.ai/help-center/en/articles/12870620-connecting-perplexity-with-google-drive

[^4_4]: https://www.perplexity.ai/help-center/en/articles/12053065-enterprise-organization-permissions

[^4_5]: https://www.perplexity.ai/help-center/en/articles/12569435-how-to-use-the-microsoft-sharepoint-connector

[^4_6]: https://www.perplexity.ai/help-center/en/articles/13014066-microsoft-onedrive-connector

[^4_7]: https://www.perplexity.ai/help-center/en/articles/11502712-local-and-remote-mcps-for-perplexity

[^4_8]: https://www.perplexity.ai/help-center/en/articles/12275669-github-connector-for-enterprise

[^4_9]: https://www.perplexity.ai/help-center/en/articles/10452641-which-apps-is-the-perplexity-assistant-able-to-use

[^4_10]: https://www.perplexity.ai/help-center/en/articles/10673201-enterprise-connector-troubleshooting-guide

[^4_11]: https://www.perplexity.ai/help-center/en/articles/12674820-microsoft-teams-connector

[^4_12]: https://www.perplexity.ai/hub/blog/how-perplexity-enterprise-pro-keeps-your-data-secure

