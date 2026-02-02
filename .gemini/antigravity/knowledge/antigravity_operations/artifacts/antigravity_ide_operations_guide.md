# Antigravity IDE 運用ガイド (KI統合 v2)

> **統合元**: 49件のPerplexity調査レポート (2026-01-26/27)
> **目的**: セッション間で再利用可能な実践的知識

---

## 1. セッション間情報共有

### 自動継承メカニズム

- 新チャット開始時、**過去20個のサマリー**がヘッダーとして付与される
- UUID参照は可能だが、完全なコンテキスト再現は保証されない
- 長時間セッションでは **context drift** が発生

### GEMINI.md (Global Rules)

**パス**: `~/.gemini/GEMINI.md`

すべてのプロジェクトに適用される共通ルール:

```markdown
Always respond in Japanese.
Be concise and direct.
Do not apologize.
```

**重要**:

- Global Rules は Workspace Rules を**上書き**する
- 絶対譲歩できないルールは**英語で記述**

---

## 2. Activation Mode (4種類)

| モード | Frontmatter | 用途 | 強制力 |
| :--- | :--- | :--- | :--- |
| **Always On** | `activation: always_on` | セキュリティ、根幹ポリシー | 最高 |
| **Manual** | `activation: manual` | 明示的呼び出しが必要 | 中 |
| **Model Decision** | `activation: model_decision` | AIが必要性を判断 | 柔軟 |
| **Glob** | `activation: Glob` + `glob_pattern: "*.dart"` | ファイル形式別 | 自動 |

### 優先順位（中央集権的設計）

1. **Core Policies** (Google基本原則) — 絶対不可侵
2. **Global Rules** (GEMINI.md) — 非常に高い
3. **Workspace Rules** — 中程度
4. **Workflows** — 最低

---

## 3. runtime/ ディレクトリ仕様 ⚡NEW

### 構造

```text
~/.gemini/antigravity/
├── brain/               # 各会話のアーティファクト (task.md, walkthrough.md)
├── knowledge/           # Knowledge Items (長期記憶)
├── conversations/       # 暗号化された会話履歴 (.pb)
├── implicit/            # 暗号化された暗黙コンテキスト (.pb)
├── browser_recordings/  # ブラウザ操作の録画（大容量）
└── mcp_config.json      # MCP サーバー設定
```

### 削除の影響

| 対象 | 影響 | 安全性 |
| :--- | :--- | :--- |
| `browser_recordings/` | 録画消失、動作影響なし | ✅ ほぼ安全 |
| `brain/<session_id>/` | そのミッションの計画書消失 | ✅ 機能上安全 |
| `knowledge/` | 長期記憶リセット | ⚠️ 学習喪失 |
| `conversations/` | 全セッション履歴消失 | ⚠️ 新規状態に |

### 保存場所変更

**公式設定なし** → OSレベルでシンボリックリンク:

```bash
# macOS/Linux
mv ~/.gemini/antigravity /Volumes/BIGDISK/antigravity-data
ln -s /Volumes/BIGDISK/antigravity-data ~/.gemini/antigravity

# Windows (管理者権限)
mklink /D "%UserProfile%\.gemini\antigravity" "D:\antigravity-data"
```

---

## 4. Knowledge Items (KI) ⚡UPDATED

**ステータス**: 機能は存在するが精密制御は不可

### 概念

- セッションをまたぐ「長期記憶」
- コードパターン、プロジェクト標準、UI/UX好みを自動学習

### 利用方法

1. `Settings → Knowledge Base` で閲覧・編集・エクスポート
2. 手動でプロジェクト標準を追加可能
3. **自動生成はブラックボックス**（いつ何が保存されるか不明確）

### 現実的な運用

- KIだけに頼らず、`.agent/rules/` + `GEMINI.md` で**重ね書き**推奨
- 重要ルールは複数経路で注入

### 4.2 Chat History Export (GCP/Linux) ⚡NEW

GCP Linux 環境でエピソード記憶（会話履歴）を完全に保存するための運用要件。

#### 起動オプション

Antigravity IDE を起動する際、以下のフラグを付与することで外部接続を許可する。

```bash
antigravity --remote-debugging-port=9222
```

#### 環境セットアップ

エクスポートツール (`export_chats.py`) の実行には Playwright が必要。

```bash
cd /home/makaron8426/oikos/hegemonikon
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
```

#### 実行

```bash
# 全セッションのエクスポート
.venv/bin/python mekhane/anamnesis/export_chats.py

# 特定のセッション (watchモード)
.venv/bin/python mekhane/anamnesis/export_chats.py --watch
```

📁 保存先: `/home/makaron8426/oikos/mneme/.hegemonikon/sessions/`
(アクセス用シンボリックリンク: `/home/makaron8426/oikos/mneme/sessions/`)

#### 🛠️ トラブルシューティング & 修正済み (2026-01-31)

- **重複コンテンツ (Race Condition)**: ✅ **修正済み**。会話クリック後の初期待機を3.0秒、DOM変化検出を最大15秒に延長し、`content_changed` フラグによる検証を追加。
- **アクティブセッションの固着**: ✅ **修正済み** (v2.1)。Batch 実行による全自動エクスポート（90件超）の成功を確認済み。
- **内容の欠落 (Truncation)**: ✅ **修正済み (v4.2)**。長いスレッドでのDOM仮想化問題をスクロール自動化 (`scroll_and_collect_messages`) により解決。全メッセージの取得が可能。
  - **品質 (Quality Hardening v4.3)**: ✅ **検証済み**。73+ メッセージの高利得抽出に成功。UIテーブル由来の空行クラスタを正規化することで「汚損」を排除し、保存可能な品質に到達。
  - **パフォーマンス・戦略転換 (v4.4)**: ✅ **最適化**。極端なスクロールによる実行時間の長期化に対応するため、重い処理をエクスポート完了後の **Post-Processing (後処理)** へ移行する方針。
  - **実装・デプロイ (v4.5)**: ✅ **完了**。`save_single_chat` メソッド内での自動空行正規化 (`re.sub`) を実装。**111セッション** (Watch 30 + Batch 81) のフル復旧を達成し、最長スレッドにて **189メッセージ** の高利得抽出（5→189個）を検証済み。
  - **診断 (1〜3件のメッセージ)**: 極端に短いエクスポートは必ずしも汚損ではない。`/boot`, `/bye`, `@learn` 等の定型セッションは、内容が正常であってもメッセージ数が非常に少なくなる傾向がある。
- **環境正規化 (v4.7)**: ✅ **完了**。`mneme/sessions/` 内の legacy (Windows時代) の空ファイル109件を削除。代わりに `.hegemonikon/sessions/` へのシンボリックリンクを設置し、データの整合性を確保。

### 4.1 スキル検出とシンボリックリンク ⚡NEW

Antigravity IDE のスキル検出（`.agent/skills/`）において、**シンボリックリンクは有効**であることが検証済み。

- **挙動**: IDE のファイルスキャナーは symlink を透過的に追跡し、実体ディレクトリ内の `SKILL.md` をロードする。
- **活用事例**: 実体ファイルをサブモジュール（`mekhane/` 等）に配置し、`.agent/skills/` にリンクを貼ることで、コード管理の整合性とIDEの自動検出を両立できる。
- **検証済み (2026-01-28)**: `tekhne-maker` を `hegemonikon/mekhane/ergasterion/tekhne/` に移動し、`.agent/skills/utils/tekhne-maker` からリンクした状態で正常に検出・読み込み（660行）が実行されることを確認した。
- **推奨**: リンク作成時は**相対パス**を使用すること。

  ```bash
  ln -s ../../../hegemonikon/mekhane/ergasterion/tekhne .agent/skills/utils/tekhne-maker
  ```

- **成功率**: 98% (Linux/macOS)。Windows では管理者権限が必要な場合がある。

---

## 4.5 Handoff v2 設計 (T8 Anamnēsis) ⚡UPDATED

セッション終了時（`/bye`）に生成される、次回セッション（`/boot`）への強力なコンテキスト注入形式。**v4.5/v4.6** では、単なるサマリーだけでなく、チャット履歴の完全エクスポートが統合されている。

### ワークフローの構成

1. **Step 1: Handoff 生成**: YAMLメタデータと自然言語サマリー。
2. **Step 3.5: Chat History Export**: `export_chats.py` による DOM 抽出。
3. **Step 3.6: Walkthrough/Task Export**: 内部バッファのバックアップ。

> **環境修正 (2026-02-01)**: `bye.md` 内の PowerShell コマンドおよび Windows パスを Bash/Linux 形式に修正し、GCP 環境での完全自動実行を確保した。

### 構造化メタデータ (YAML)

SBAR (Situation, Background, Assessment, Recommendation) と ADR (Architecture Decision Record) を統合。

```yaml
session_handoff:
  version: "2.0"
  situation:
    primary_task: "主題"
    status: "in_progress | blocked"
  tasks:
    completed: ["タスク1 ✓"]
    in_progress: ["タスク2"]
  decisions:
    - id: "d_001"
      decision: "選んだ案"
      context: "理由"
  uncertainties:
    - description: "未確認事項"
      priority: "high"
```

### 自然言語サマリー (Markdown)

AIが直感的に「前回何にこだわり、何に気付いたか」を把握するためのセクション。

- **Claude の理解状態**: Creator の好みや判断基準の蓄積
- **アイデアの種**: 今回実装しなかったが価値ある方向性
- **次回への提案**: `/boot` 直後の初動指示
- **Red-Other-Person Standard**: Handoff は「文脈を全く知らない赤の他人が読んでも、即座にプロジェクトを再開できる」レベルの明示性と具体性を備える。

---

### 8.1 24-Theorem Footprint Verification (2026-01-28)

Successful verification of all 24 canonical theorem skills (O1-O4, S1-S4, H1-H4, P1-P4, K1-K4, A1-A4).

| Category | Verification Method | Result |
| :--- | :--- | :--- |
| **存在確認** | `ls -R .agent/skills/` | ✅ 全24フォルダ確認 |
| **起動確認** | `/chk`, `/hist`, `/noe` 等のトリガー | ✅ 適切なメタデータ読込 |
| **メタデータ整合性** | v2.1 相互参照 (Related Skills) | ✅ 整合確認 |

---

## 9. Automated Quality Review (GitHub Actions) ⚡NEW

**適用ファイル**: `.github/workflows/quality-review.yml`

### 目的 (Quality Review)

ISO 25010 (品質特性) と 3M (ムリ・ムダ・ムラ) 管理に基づく、コードとドキュメントの自動監査。毎週月曜 09:00 JST 実行。

### 検証項目

- **保守性 (Muri/CC)**: Ruff を使用した循環的複雑度 (CC ≤ 15) 検証。
- **セキュリティ (SAST)**: Bandit による脆弱性スキャン。
- **冗長性 (Muda)**: Vulture によるデッドコード（未使用コード）検出。
- **安全性**: pip-audit による依存パッケージの脆弱性チェック。

### 運用フロー

1. **GitHub Actions 実行**: 定時または PR 時に自動発動。
2. **サマリー出力**: `$GITHUB_STEP_SUMMARY` への結果書き出し。
3. **是正アクション**: 警告発生時、`/vet` ワークフローで修正プランを策定。

---

## 5. モデル別特性

| 特性 | Claude | Gemini |
| :--- | :--- | :--- |
| ルール解釈 | 厳格・形式的 | 柔軟・文脈適応的 |
| ルール遵守度 | 高い | 中程度 |
| 推論スタイル | 決定論的（同じ入力→同じパス） | 非決定論的（多様なパス生成） |
| 得意領域 | 精密実装、監査、複雑リファクタリング | 創意工夫、マルチモーダル、探索的タスク |
| 安全性判断 | 先制的フィルタリング | 文脈依存的 |

### Model Decision モードでの差異

- **Claude**: 保守的（「明確な指標がない限り適用しない」）
- **Gemini**: 積極的（「潜在的な最適化機会があれば提案」）

---

## 6. Git管理指針 (Git Management Principles) ⚡UPDATED

### 6.1 Full-Sync Configuration (2026-02-02)

2026年2月より、環境移行の摩擦をゼロにするため、従来ローカル専用としていた **`.gemini/` ディレクトリ全体の Git 管理** を開始した。これにより、GCP とローカル PC 間での「学習状態」と「タスク進捗」の完全な同期を実現する。

- **対象外 (Ignore)**:
  - `.gemini/antigravity/browser_recordings/` (大容量のため)
  - `.gemini/antigravity-browser-profile/` (ブラウザキャッシュ等)
- **対象 (Tracked)**:
  - `.gemini/antigravity/brain/`: セッションごとのタスク・計画書
  - `.gemini/antigravity/knowledge/`: 長期記憶 (Knowledge Items)
  - `.gemini/oauth_creds.json`, `google_accounts.json`: 認証情報
  - `.gemini/settings.json`, `.gemini/state.json`: IDE の構成と状態

### 6.2 共有・同期ワークフロー

- **同期処理**: `git add .gemini/ --all && git commit -m "feat: sync Antigravity state"`
- **復旧**: `git pull` を行うだけで、新しい環境でも前回のセッションの継続が可能。

### 6.2 Oikos-Root Workflow Standard (Jan 28, 2026) ⚡NEW

サブモジュール（`hegemonikon/`）を持つプロジェクトにおいて、ワークフローの透明性と編集性を最大限に高めるための標準配置基準。

1. **配置**: ワークフローの「正本」はプロジェクトルートの `.agent/workflows/` に配置する。
2. **パス形式 (Linux/oikos)**:
    - 以前: `m:\Hegemonikon\...` (Windows)
    - 現在: `/home/makaron8426/oikos/hegemonikon/` (Linux)
    - 以降の全ファイル参照は **oikos root** (`/home/makaron8426/oikos/`) を基準とした絶対パスを使用する。
3. **理由**:
    - **透明性**: IDE の AI が submodule 内の深いパスよりもルートパスを優先して検知しやすい。
    - **衝突防止**: サブモジュール内の変更は `git diff` で見落とされやすく、誤って古いバージョンで上書きされるリスクを回避。
    - **機動力**: サブモジュールのコミット/プッシュを待たずに、プロセスの改善を即座に反映可能。
4. **移行**: `hegemonikon/.agent/workflows/` は、ルートへのコピーが完了し、整合性が確認されたものから順次削除（廃止）する。

### 6.3 Git Repository Size Management (100MB Limit) ⚡NEW

GitHub には **100MB/ファイル** の制限があり、これを超えると Push が拒絶される。MLモデル（.onnx, .bin）などの大容量ファイルを扱う際の注意点：

1. **検知**: `pre-receive hook declined` エラーが発生した場合、`remote: error: File ... exceeds GitHub's file size limit` のログを確認。
2. **対処法 (Ignore & Clean)**:
    - 外部リポジトリや LFS で管理すべきファイルは `.gitignore` に追加。
    - インデックスから削除: `git rm --cached <path>`
    - コミットの修正: `git commit --amend`
    - **履歴の完全削除 (Deep Clean)**: 上記で解決しない（過去のコミットに含まれている）場合、`git filter-branch` で全履歴から削除：

      ```bash
      git filter-branch --force --index-filter \
        'git rm --cached --ignore-unmatch <path>' \
        --prune-empty --tag-name-filter cat -- --all
      ```

3. **予防**: 50MBを超えるファイルを追加する際は、管理レイヤー（Git LFS または外部ストレージ）を決定してからステージングすること。

---

## 7. ベストプラクティス

### 7.1 Mutual Audit (相互監査) ⚡NEW

単一モデルの自己批判（Self-critique）よりも、異なるアーキテクチャを持つモデル（Claude ↔ Gemini）による監査の方が、ハルシネーションの検知能力が約35%高い。

- **手順**:
  1. 片方のモデルで実装を完了する。
  2. IDEの「モデル切替」機能でモデルを切り替える。
  3. 切换後のモデルで `/vet` を実行し、先行作業を監査する。
- **メリット**: 追加費用なしで監査の客観性と精度を最大化できる。
- **制約**: Jules 866 はAPIベースの非同期バッチ処理に適しており、IDE内の同期的な相互監査は「モデル切替 + /vet」が最適。

- **Global Rules**: 英語で記述 (`Always respond in Japanese`)
- **Workspace Rules**: 日本語でOK

### 7.2 Hegemonikón Research Request Standard ⚡UPDATED

調査命令 (`/zet`) において Perplexity 等の最新検索エンジンから最高精度を引き出し、かつ **Claude (v3.5/4/4.5)** が効率的に処理するための標準構造。

- **Pattern**: **Hybrid Model (ハイブリッド型)**
- **Structure**:
  1. **Head (Condensed)**: 冒頭 2,000 トークン以内に [出力形式] → [目的] → [時間制約] を配置。検索エンジンのクエリ生成（Positional Bias）を最適化する。
  2. **Body (Deep)**: 詳細な「調査対象の定義」「論点」「ルール」を中盤以降に配置。最終消費者である Claude への高精細な情報伝達を担保し、品質劣化を防ぐ。
- **Claude Optimization**: レポート受領側の Claude のために、Markdown 階層構造 (H1-H3) と、表/JSON を組み合わせた出力を要求する。
- **SOP**: 依頼書は `brain/<id>/zet_<topic>.md` に自動出力し、セッション間の文脈継承に利用する。

| コマンド | 用途 |
| :--- | :--- |
| `/task` | 実装特化（説明最小限） |
| `/review` | コード品質（diffベース） |
| `/test` | テスト実行（Exit Codeベース） |
| `/zet` | 調査要件定義と依頼書生成 |

### 複数エージェント戦略

- **フロントエンド**: Gemini（創意工夫が活きる）
- **バックエンド**: Claude（精度重視）
- **テスト**: GPT-OSS（バランス型）

---

## 9. Antigravity Boot Protocol & Anti-Stale Mechanism ⚡NEW

セッション開始時や重要なワークフロー実行前に行うべき「認識の一貫性」を保つための手順。

### 9.1 Anti-Stale Protocol (正本読み直し)

Antigravity IDE はワークフローやルールのファイルをキャッシュすることがある。特に oikos (Linux) 環境への移行後は、ファイルシステムの同期遅延により古いキャッシュに基づいた推論が行われるリスクがある。これを防ぐため、以下の手順を**必須**とする：

1. **view_file による強制再読込**: ワークフローの「正本（主に `.agent/workflows/`）」を `view_file` で直接読み直す。
2. **探索優先**: ブート時は既存の記憶（活用）よりも、現状のファイルシステム（探索）を優先。
3. **Resonance Audit (共鳴監査)**: `view_file` で読み込んだ内容を KI (Knowledge Items) の記述と比較する。もし KI に記録されている最新バージョンよりもディスク上のファイルが古い（以前の記述に戻っている）場合、Git 履歴の遡及調査 (`git log`) を即座に開始する。

### 9.2 /boot ワークフローの標準シーケンス (v3.2) ⚡UPDATED

Hegemonikón v3.2 から導入された、リポジトリ・コンテキストの厳格化とパスの固定による堅牢化シーケンス。

1. **Phase 1: 正本読込 (Anti-Stale Protocol)**: `view_file /home/makaron8426/oikos/.agent/workflows/boot.md` を実行し、キャッシュではなく物理ファイルに基づいた起動を保証。
2. **Phase 2: セッション状態確認**: 週次レビュー判定、最新 Handoff 読込、目的リマインド (`/bou`)、Drift（乖離）診断。
3. **Phase 3: 知識物理読込 (Cognitive & Emotional)**:
    - **Sophia**: 内部知識のサマリー提示。
    - **FEP A-Matrix**: 学習済み観察モデル (`learned_A.npy`) のロード。 ※`.venv` フルパス経由の実行が必須。
    - **Meaningful Traces**: 前の私が意味を見出した瞬間（Emotional Layer）の読み込み。
4. **Phase 4: システム更新**:
    - プロファイル（GEMINI.md）読込。
    - `tools.yaml` によるツール構成のリマインド。
    - **Step 10.6: CCL コアパターン復習 (v3.4)**: 特殊パターンの誤認防止。
    - **Digestor Summary**: 収集済みの未消化論文サマリーを表示。 ※venv Python 必須。
5. **Phase 5: 外部入力**: Dispatch Log 進捗、Perplexity 調査 inbox、Jules 専門家レビュー結果の取得。 ※`cd {submodule}` によるリポジトリ・コンテキスト指定が必須。
6. **Phase 6: 完了**: フェーズ別のサマリー報告。

**設計原則**: v3.4 では「認知的エラーの予防」を重視。ドキュメント化されているが忘れがちなコアパターン（*^, ~ vs*, _ 等）をブート時にプッシュ通知形式で表示し、セッション全体の整合性を担保する。

### 9.4 Workflow Regression & Recovery (退行と復旧) ⚡NEW

「正本（Seihon）はルートである」という原則を維持していても、Git マージミスやリバートによりワークフローが物理的に古い状態に戻る「退行（Regression）」が発生し得る。これを検知・復旧するためのプロトコル：

- **検知**: モデルが「以前はあったはずの機能（例: /boot における週次レビュー提案）」が消失していることに気づいた場合、それはキャッシュの問題ではなく**物理的なロールバック**を疑う。
- **調査**: 直ちに `git log --oneline -- .agent/workflows/{command}.md` を実行し、直近の意図的な変更が失われていないか確認する。
- **復旧**:
    1. ベクトル検索（KI）により失われたロジックの断片を回収する。
    2. 必要に応じて `git show {commit_hash}:{path}` により過去の正文を復元する。
    3. 復旧後は `version` をインクリメントし、KI のメタデータを更新して「現在地」を再定義する。
- **教訓**: ベクトル検索（KI）は情報の「復元」を助けるが、実行コード（ワークフローファイル）の「物理的整合性」は Git 履歴に依存する。KI とファイルの「Resonance（共鳴・一致）」をブート時に確認することが、堅牢な自律運用の鍵となる。

#### 9.4.1 Vector Search Restoration Paradox (KI復元の限界)

KI（ベクトル検索）があればファイルを完全に復元できるという期待は、以下の理由で危険である：

1. **メタデータの希釈**: KI は要約や重要な断片を優先して記憶するため、ワークフロー全体の「正確なパス」や「全ての時間制約（例: 2025後半優先）」が一部欠落してインデックスされる可能性がある。
2. **物理的非連続性**: ベクトル空間上の「類似性」は、コードとしての「文法的な完全性」や「物理的な動作保証」を担保しない。
3. **結論**: KI は**「何が書かれていたか」というセマンティックなバックアップ**としては極めて優秀だが、**「どのファイルが正しいか」という物理的な統治（Governance）**においては Git 履歴が上位の権威を持つ。

### 9.3 Mandated Cognitive Behaviors (v3.1)

Hegemonikón 2.1 環境では、以下の行動が「エージェントの基本動作」として組み込まれている。

- **Read-before-Act (RRP Protocol)**:
  - Strategic workflows (`/plan`, `/ene`, `/noe`) and major skills (T4, T3, T2, S2) have integrated Read-Resolve protocols.
  - **Full (Architecture/Execution)**: Read → Resolve Concerns → Proceed.
  - **Light (Deep Thinking/Noesis)**: Read → Identify Blindspots → Proceed.
  - **High-Fidelity Chat Export**: Mandatory scrolling logic for virtualized DOM sessions (v4.8).
- **GPU Task Management**: Tracking high-load tasks (Steering, Local LLM) for execution on dedicated hardware (v4.9).
- **Security Protocol**: Use of IDE Secrets/Environment variables for API key protection. Direct exposure in chat is a critical vulnerability.
without verification is a **Precondition Violation**.

- **Proactive Opinion ("あるなら述べる")**:
  - 主観・提案・懸念がある場合、コマンドを待たずに**能動的に表明**する。
  - ただし、ノイズを避けるため「特に意見がない場合は沈黙」を維持する。
  - コマンド `/u` は、特定のトピックについて深掘り意見を求める「強調スイッチ」として機能する。

---

---

## 10. MCP サーバーの追加と構成 ⚡NEW

プロジェクト固有の知識検索やツールを Antigravity に統合する手順。

### 構成手順

1. **サーバー実装**: `server.py` を作成し、`stdio` プロトコルを実装する。
2. **依存関係インストール**: 必要に応じて `pip install mcp` を実行。
3. **mcp_config.json 更新**: `~/.gemini/antigravity/mcp_config.json` にサーバー定義を追加。

```json
"servers": {
    "my-server": {
        "command": "python",
        "args": ["/path/to/server.py"]
    }
}
```

1. **IDE 再起動**: 設定反映には Antigravity の再起動が必要。

### 登録済みサーバー (Hegemonikón 例)

- `gnosis`: 論文検索 (Academic research)
- `sophia`: 統合知識検索 (KIs / Handoffs) **Standard**
- `mneme`: 4源統合検索 (Gnōsis/Chronos/Sophia/Kairos) - Legacy/Latency issues
- `jules`: Jules API 並列コード生成 (60並列対応)

---

## 11. 監査とトラブルシューティング (Troubleshooting) ⚡NEW

### 11.1 ModuleNotFoundError & Repository Context

実装コードの検証 (`run_command`) や ワークフロー内でのスクリプト実行中にエラーが発生する場合：

- **原因1 (Environment)**: IDE がシステムデフォルトの Python を使用しており、プロジェクト固有の `.venv` にインストールされたパッケージ（例: `pymdp`）をロードできていない。
- **原因2 (Context)**: Git コマンド等が、メタプロジェクト（`oikos`）のルートで実行され、対象サブモジュール（`hegemonikon`）の設定（remote origin 等）を読み込めていない。

- **解決策**:
    1. **フルパス指定**: ワークフロー内では `python` ではなく `/home/makaron8426/oikos/hegemonikon/.venv/bin/python` のようにフルパスでバイナリを指定する。
    2. **Repo Context Enforcement**: Git 操作やサブモジュール内のスクリプトを叩く際は、必ず `cd {path} && ...` を使用してカレントディレクトリを明示する。
    3. **PYTHONPATH設定**: 依存モジュールのインポートを確実にするため、環境変数を明示的に渡す。

  ```bash
  # 修正例 (v3.2 パターン)
  cd /home/makaron8426/oikos/hegemonikon && \
  PYTHONPATH=/home/makaron8426/oikos/hegemonikon \
  /home/makaron8426/oikos/hegemonikon/.venv/bin/python -c "import pymdp; ..."
  ```

- **検証済み (2026-01-29)**: `boot.md` における FEP A行列および Jules レビューブランチ取得において、このパターンを適用することでインポートエラーと Git 参照エラーを解消。

### 11.2 Precondition Violation

RRP プロトコル（読み込みなき行為）が指摘された場合：

- **対策**: 直ちに作業を中断し、対象ファイルの `view_file` を実行。その後、懸念事項を解決してから再開する。

  - `send_command_input` で `Terminate: true` で強制終了
  - ログ出力を増やして進捗を可視化。

### 11.4 Frontmatter Field Support ⚡NEW

Antigravity IDE のスキルパーサーは、YAML frontmatter のすべてのフィールドをモデルに渡すわけではない。

- **無視されるフィールド**: `llm_optimization`, `when_not_to_use` (独自定義時)
- **活用される重要フィールド**: `description`, `triggers`, `when_to_use`
- **最適化戦略 (Strategy B)**:
  - `when_not_to_use` のような否定的な制約は、`description` 内部に **"NOT for..."** 句として統合することで、セマンティックマッチングの精度を向上させる。
- **検証結果**: リサーチ (`/zet`) により、`llm_optimization` フィールドは実行時のモデル推論に影響を与えないことが確認されている。

---

## 12. Automated Documentation & Integrity ⚡NEW

Hegemonikón では、システムの自己記述性を維持するために Git フックを活用。

### 12.1 Autonomous Workflow Registry

ワークフローの名称、層（Ω/Δ/τ）、親子関係を常に正確に保つための仕組み。

- **フック**: `.agent/hooks/pre-commit`
- **動作**: `.agent/workflows/` 内のファイルが修正されるたびに `update-workflow-registry.py` を実行。
- **機能**:
  - 全ワークフローのフロントマターからメタデータを抽出。
  - `workflow-naming-convention.md` を自動更新してステージング。
  - 不適切なフォーマット（必須フィールド欠落など）をコミット前にブロック。

### 12.2 Setup

```bash
# フックの有効化（プロジェクトルートで実行）
git config core.hooksPath .agent/hooks
```

---

## 13. Dispatch & Scaling (Phase B Criteria) ⚡NEW

**管理ファイル**: `mneme/.hegemonikon/logs/dispatch_log.yaml`

### Phase B 移行条件

1. **dispatch_count**: 50件以上
2. **failure_rate**: 10%未満
3. **exception_patterns**: 3件以上の捕捉

### 記録プロトコル (v2.0)

自律的スケーリングへの移行を「見える化」するため、以下の項目を記録する。

- **Level 1: スキル発動 (Primary)**:
  - **skill_activations**: Antigravity IDE が `description` マッチにより自律的にスキルをロードした履歴。これが最も重要視される（自律性の証）。
- **Level 2: ワークフロー実行**:
  - **workflow_executions**: `/noe`, `/plan` 等のコマンド実行と、その中でのスキル参照。
- **Level 3: コンテキスト活用**:
  - **ki_reads**: KI (Knowledge Items) の読み込み頻度。
  - **exception_patterns**: 想定外の状況と対処（Phase B 移行条件）。

### 運用 (Post-Session Aggregation)

`/bye` (v2.4+) ワークフローの最後に、そのセッションで行われた「発動」を自己申告形式で集計し、`dispatch_log.yaml` に追記する。リアルタイム記録による認知負荷を避けつつ、セッション単位の確実な蓄積を担保する。

### 目的 (Dispatch)

自律的スケーリングとマルチエージェント相乗効果のフル活用。

---

## 14. Swarm Monitoring & Result Collection ⚡NEW

大量の並列レビュー（Synedrion v2.1）を実行する場合、IDE の通知や Web UI での追跡は非効率である。`collect_results.py` を使用したコマンドラインベースの運用を推奨する。

### 運用コマンド

| アクション | コマンド | 用途 |
| :--- | :--- | :--- |
| **最新確認** | `python collect_results.py --list 10` | 直近10セッションのステータス一覧 |
| **詳細取得** | `python collect_results.py --session {id}` | 特定レビューの詳細とPRリンクの取得 |
| **レポート** | `python collect_results.py --report {file}.json` | バッチ実行結果のサマリー生成 |
| **自動連携** | `python collect_results.py --json` | 他のツールやスクリプトへのパス渡し |

### 状態の解釈

- **SILENCE**: レビュー対象に問題が見つからなかった正常な状態（PR未作成）。
- **COMPLETED + PR**: 指摘事項が発見され、PRが作成された状態。
- **FAILED**: API制限またはランタイムエラー。`--session` で詳細を確認し、必要に応じて再試行。

---

*統合日: 2026-01-29 (v4.0)*
*Sources: Swarm Orchestration Implementation (9cb3717d), Security x O1 Case Study, Adaptive Allocator Design.*

## 15. Adaptive Swarm Management ⚡NEW

1,800セッション/日のポテンシャルを持つ Synedrion v2.1 スウォームを、現実的なリソース制約（9キー）の中で効率的に運用する。

### 予算と安全マージン

- **目標実行数**: **720 セッション/日**
- **制約**: 1 API キーあたり 80 セッション/日（最大 90-100 の 80%）を推奨。
- **リソース**: 3アカウント × 3キー = **9キー** で運用。

### Adaptive Allocation モード

`adaptive_allocator.py` は以下の 3 層でタスクを自動配分する：

1. **Change-Driven (40%)**: `git diff` で変更されたファイルに関連するドメインを優先（例：auth 変更 → Security ドメイン）。
2. **Discovery (40%)**: 未レビュー箇所をランダムサンプリングし、潜在的バグを探索。
3. **Weekly Focus (20%)**: 曜日ごとの重点ドメイン（月：Security、火：Performance等）を深掘り。

### 自動実行の監視

毎日 04:00 JST に `swarm_scheduler.py` が cron 経由で実行される。

```bash
# スケジューラの状態確認
python swarm_scheduler.py --status

# 実行ログの確認
tail -f swarm_scheduler.log
```

---
*統合日: 2026-01-29 (v4.1)*
*Sources: Swarm Orchestration Implementation (9cb3717d), Adaptive Allocator Algorithms, Budget Correction Report.*

## 16. Managing Technical Debt (Limbo Pattern) ⚡NEW

As of 2026-01-30, the **Limbo Pattern** is adopted for handling legacy or non-compliant files without immediate deletion.

- **Storage**: `ergasterion/_limbo/`.
- **Purpose**: A holding area for files that are "Ugly but Practical" or awaiting refactoring.
- **Operational Rule**: Moving a file to `_limbo/` is the first step of a "Zero Trust Refresh." It clears the "Sacred" areas (mekhane, kernel, root) without losing the utility of the isolated scripts.
- **Escape**: Files should be either **Promoted** (refactored to Hegemonikon standards) or **Deleted** (replaced by better implementations).

---
*統合日: 2026-01-30 (v4.2)*
*Sources: Zero Trust Refresh v2.*
