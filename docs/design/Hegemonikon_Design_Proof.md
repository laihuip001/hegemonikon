# Hegemonikón 設計証明 (Source of Truth)

このドキュメントは、Hegemonikónプロジェクトファイル(`Claude-設計01.md`, `Claude-Hegemonikón01.md`)の深い読み込みと構造的理解を証明する**データ証明**として機能します。文脈を損なうことなく、設計哲学、16機能アーキテクチャ、情報レイヤー、およびPhase 1実装詳細を統合しています。

---

## 1. コア哲学と設計原則

### 1.1 目標 (The Goal)
**Forge**を拡張し、**Google Antigravity**を「人生のCEO」として活用する。
- **ミッション**: 全ての個人情報（デバイス、サービス、性格、スケジュール）の一元管理と、プロアクティブなタスク/リマインド提案。
- **優位性**: Obsidian/GitHubへの「書き込み」能力と、タスク実行能力（Antigravity）。

### 1.2 "Manus" 設計思想の統合
- **Contexting (文脈維持)**: `todo.md`のリサイテーションにより、長時間セッションでも目標を見失わない仕組み。
- **Self-Repair (自己修復)**: 「失敗はループの一部」。エラー発生時に自律的に修正して次のステップへ進むループ。
- **Generality (汎用性)**: 特定の業務に依存しない、あらゆるデジタルタスクに対応する汎用性。

### 1.3 FEP (自由エネルギー原理) 基盤
システムは、**変分自由エネルギー最小化**という統一原理の下での知覚・認知・行動の統合に基づいて構築されています。
- **推論 vs 行為 (Inference vs Action)**: 信念を変える vs 世界を変える。
- **エピステミック vs プラグマティック (Epistemic vs Pragmatic)**: 不確実性の削減 vs 目標の達成。
- **短期 vs 長期 (Fast vs Slow)**: 即時的 vs 長期的。
- **低次 vs 高次 (Low vs High)**: 感覚運動 vs 概念・目標。

---

## 2. Hegemonikón 16機能アーキテクチャ (2x2x2x2)

エージェントのオペレーティングシステムは、4つの軸から導出される16の機能によって定義されます。

**軸の定義:**
1.  **Flow (I/A)**: 推論 (Inference) vs 行為 (Action)
2.  **Value (E/P)**: エピステミック (Epistemic) vs プラグマティック (Pragmatic)
3.  **Tempo (F/S)**: 短期 (Fast) vs 長期 (Slow)
4.  **Stratum (L/H)**: 低次 (Low) vs 高次 (High)

### 2.1 低次階層 (Stratum-L: 感覚運動レベル)
| ID | Code | Name (Greek) | Name (JP) | Definition |
|---|---|---|---|---|
| 01 | I-E-F-L | **Aisthēsis-L** | 感覚知覚 | 感覚入力から即時的に特徴を検出し、予測誤差を処理する。 |
| 02 | I-P-F-L | **Krisis-L** | 運動判断 | 運動パラメータを即時的に選択・調整する。 |
| 03 | A-E-F-L | **Peira-L** | 探索運動 | サッケード、注意移動など情報獲得のための身体運動。 |
| 04 | A-P-F-L | **Praxis-L** | 反射実行 | 目標に向けた即時的・反射的な運動実行。 |
| 05 | I-E-S-L | **Theōria-L** | 感覚学習 | 感覚統計の再推定、知覚モデルの長期更新。 |
| 06 | I-P-S-L | **Phronēsis-L** | 運動計画 | 運動シーケンスの計画、動作パターンの設計。 |
| 07 | A-E-S-L | **Dokimē-L** | 感覚実験 | 感覚空間の系統的走査、環境の探索的検証。 |
| 08 | A-P-S-L | **Anamnēsis-L** | 運動記憶 | 運動学習、技能獲得、手続き記憶の形成。 |

### 2.2 高次階層 (Stratum-H: 概念・目標レベル) - **Forge Phase 1 Focus**
| ID | Code | Name (Greek) | Name (JP) | Definition |
|---|---|---|---|---|
| 09 | I-E-F-H | **Aisthēsis-H** | 文脈認識 | 文脈の認識、意味の推論、状況の即時的理解。 |
| 10 | I-P-F-H | **Krisis-H** | 目標評価 | 目標との整合性評価、優先順位の即時判断。 |
| 11 | A-E-F-H | **Peira-H** | 能動質問 | 能動的な質問、確認行動、情報要求。 |
| 12 | A-P-F-H | **Praxis-H** | 意思決定 | 意思決定、コミットメント、行動の選択と実行。 |
| 13 | I-E-S-H | **Theōria-H** | 世界観構築 | 因果モデルの構築、理論形成、世界観の発展。 |
| 14 | I-P-S-H | **Phronēsis-H** | 人生設計 | 長期計画、人生設計、戦略的方策の評価。 |
| 15 | A-E-S-H | **Dokimē-H** | 検証設計 | 実験設計、介入研究、仮説の系統的検証。 |
| 16 | A-P-S-H | **Anamnēsis-H** | 価値更新 | メタ学習、価値観更新、生成モデル全体の改訂。 |

---

## 3. 情報レイヤー構造 (The "Memory")

Raiの全情報コンテキストは以下の6層で構造化されています。

**Layer 1: Factual Identity (事実的アイデンティティ)**
- 1.1 生物学的・法的基盤 (本名, 住所, マイナンバー等)
- 1.2 医療・健康 (既往歴, 服薬, AuDHD, INTP-T)
- 1.3 経済・資産 (口座, カード, サブスクリプション)
- 1.4 所有物 (デバイス, スペック, 物理的所有物)

**Layer 2: Contextual Operating State (文脈的稼働状態)**
- 2.1 時間管理 (カレンダー, ルーティン, 期限)
- 2.2 プロジェクト・タスク (進行中案件, ステータス, 保留事項)
- 2.3 人間関係 (家族, "おばあちゃん", 仕事, プロトコル)
- 2.4 使用サービス・ツール (AI, 開発, 生産性ツール)
- 2.5 学習・スキル (資格, 学習中領域, Vault知識ベース)

**Layer 3: Psychological Operating System (心理的OS)**
- 3.1 認知アーキテクチャ (実用的構成主義, A/Bテスト型思考)
- 3.2 ドーパミン経済 (トリガー: 新規性/ハック, ブロッカー: ルーチン)
- 3.3 スキーマ状態 (欠陥/恥: 活性, 情緒的剥奪, 不信/虐待)
- 3.4 コーピングモード (遮断された護り手 - 高機能版)
- 3.5 愛着システム (休眠状態, 条件付き起動)

**Layer 4: Philosophical Axioms (哲学的公理系)**
- 4.1 認識論 (根拠ベースの信念のみ採用)
- 4.2 価値論 (価値 = 間主観的構成物/社会的効用)
- 4.3 意思決定公理 (可逆性原則, ゼロベース, システム的利己主義)
- 4.4 未解決変数 (「見下される」視線の正体, 愛着の検証)

**Layer 5: Operational Protocols (運用プロトコル)**
- 5.1 AI対話プロトコル (Dense Clinical Analysis, 説教禁止)
- 5.2 情報更新フロー (保存ルール, 更新頻度)
- 5.3 失敗時プロトコル (自己修復ループ, エスカレーション)

**Layer 6: Long-term Vision (長期ビジョン)**
- 6.1 人生の方向性 (キャリア, 経済目標)
- 6.2 制約条件 (仮釈放条件, 健康, 経済)
- 6.3 未回答の問い (未解決の探索領域)

---

## 4. Phase 1 実装仕様

**目的**: Antigravityによる「Push型」（プロアクティブな提案）能力の確立。

### 4.1 Phase 1 コアモジュール
| Module | Function Mapping | Purpose |
|---|---|---|
| **`/boot`** | **Aisthēsis-H** | ブートシーケンス: プロファイル読込 → 履歴同期 → レビュー生成。 |
| **`/sync-history`** | **Aisthēsis-L** | チャット履歴 (Gemini Takeout JSON) をVault Markdownに変換。 |
| **`/review`** | **Krisis-H / Theōria-H** | 履歴/文脈をスキャンし、「今日のレビュー」（タスク/提案）を生成。 |

### 4.2 モジュールロジック仕様 (設計XMLより抽出)

#### **MODULE: `/boot`**
- **Trigger**: セッション開始時。
- **Flow**:
    1.  `load_profile`: GEMINI.md / システム設定を読み込み。
    2.  `sync_history`: /sync-history を実行（前回から6時間以上経過時）。
    3.  `daily_review`: /review を実行。
- **Output**: 要約された「FORGE BOOT SEQUENCE」ステータスブロック + `/review` の内容。

#### **MODULE: `/sync-history`**
- **Inputs**: Google Takeout JSONファイル (Gemini, ChatGPT) at `/Google Drive/Takeout/...`。
- **Destination**: `/vault/chat-history/{source}/{date}_{topic}.md`。
- **Logic**:
    1.  新規ファイルを検知（vs `.sync-state.json`）。
    2.  JSONを解析し、タスクを抽出（高確度: "ToDo", "やる"; 中確度: "確認", "次"）。
    3.  トピックスラッグを生成。
    4.  Vault Markdown（YAML Frontmatter + Content）として出力。
- **Constraints**: 1回最大50ファイル, 重複スキップ。

#### **MODULE: `/review`**
- **Inputs**: チャット履歴（直近7日）, カレンダー（Phase 2）, `current.md`。
- **Logic**:
    - **タスクシグナル**のスキャン: "ToDo", "やります...", "期限"。
    - 除外: "完了", "情報収集のみ"。
- **Output Structure**:
    - 🔴 **要アクション** (期限あり/明示的コミット)
    - 🟡 **フォローアップ候補** (暗黙的/保留中)
    - 🟢 **完了確認待ち** (報告済みだが未確認)
    - 💡 **提案** (プロアクティブな提案)

---

## 5. 次のステップ (Roadmap)

### 完了 ✅
1. **Kernel統合**: `GEMINI.md`最上位にHegemonikón Doctrine追加
2. **Rules作成**: `.agent/rules/hegemonikon.md` 作成（詳細仕様）

### 次のアクション
1. **Forge Module マッピング検証**: 各機能と既存Forge Moduleの対応確認
2. **Phase 1 テスト**: `/boot` → `/sync-history` → `/review` の動作検証
3. **Phase 2 計画**: Theōria-H, Phronēsis-H, Dokimē-H の設計
