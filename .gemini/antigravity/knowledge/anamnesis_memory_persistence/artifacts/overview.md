# Anamnēsis & System Persistence (v6.0)

## 18. The Mnēmē Layer

Anamnēsis is the persistent storage and retrieval backbone of Hegemonikón, ensuring that session states, knowledge items, and cognitive parameters are preserved across the 'forgetting' boundary of LLM context windows.

### 1.1 Components

- **VaultManager**: Atomic file operations with automatic `.bak` creation and 'Safe Read' fallback logic.
- **Symplokē (統合知識層)**: The unified knowledge layer that fuses disparate memory domains (Gnōsis, Mnēmē, Kairos, Chronos) via a standardized adapter interface.
- **GnosisIndex**: Vector database for research papers and external knowledge (LanceDB).
- **KairosIndex**: Vector database for session handoffs AND conversation logs, enabling Federated Memory Retrieval.
- **H4 Doxa Store**: Specialized persistence for cognitive beliefs and derivative selection learning.
- **Workflow Artifacts**: Automated persistence of all workflow execution details (v1.1) in `mneme/.hegemonikon/workflows/`.
- **NightlyReview**: Mechanism for synthesizing daily activities into the weekly review.

---

## 2. Memory-First Architecture

The **Memory-First Architecture** shifts focus from pure computation to proactive memory management across three layers:

| Cognitive Layer | Hegemonikón Component | Function |
| :--- | :--- | :--- |
| **Episodic Memory** | Handoff, persona.yaml, values.json | Recording specific session experiences and personality traits. |
| **Semantic Memory** | Sophia, Knowledge Items (KI), H4 Doxa | Storing structured knowledge and verified beliefs. |
| **Working Memory** | Chat context, task.md, implementation_plan.md | Immediate operational state and current focus. |

### 2.1 Necessity of Proof (FEP A0)

Under the Free Energy Principle, an agent must integrate diverse sensory inputs into a single internal model to minimize surprise. Symplokē provides the necessary "結合装置" (fusion apparatus) to project different knowledge sources into a shared cognitive space.

---

## 3. Vault Manager Specification

The `VaultManager` (in `mekhane/anamnesis/vault.py`) provides a stateless utility for secure file interactions.

### 3.1 The 'Safe Write' Protocol

1. **Backup**: If target exists, copy to `.bak`.
2. **Atomic Write**: Write to a temporary file in the same directory.
3. **Replace**: Swap the temporary file with the target (atomic in POSIX).

### 2.2 Methods

- `write_safe(filepath, content, ...)`: Implements the protocol described above.
- `read_safe(filepath)`: Attempts to read the primary file; falls back to `.bak` on failure.

---

## 3. Audit Findings (2026-01-28)

A comprehensive audit revealed significant "API drift" in the persistent layer.

### 3.1 Vault API Drift

- **Issue**: The `VaultManager` was refactored from a stateful class (taking a directory in `__init__`) to a stateless utility module using `@staticmethod`.
- **Impact**: Legacy tests in `tests/test_vault.py` and `anamnesis/tests/test_vault.py` are currently failing because they attempt to instantiate the class with arguments.
- **Resolution**: Legacy tests in `tests/test_vault.py` and `anamnesis/tests/test_vault.py` were refactored to use `VaultManager.write_safe()` and `VaultManager.read_safe()` static methods, achieving **4 PASSED** tests in the vault sub-suite.

### 3.2 LanceDB Schema Constraints (GnosisIndex)

- **Issue**: `TestGnosisIndex.test_load_primary_keys` failed with `ValueError: Cannot create table from empty list without a schema`.
- **Root Cause**: Attempting to create a LanceDB table with an empty input list without pre-defining the schema.
- **Resolution**: Refactored `mekhane/anamnesis/tests/test_index.py` to use a robust mock for `Embedder.embed_batch` using `side_effect`, ensuring the output vector count matches the input text count. Verified **10 PASSED** in the index sub-suite.

## 4. Belief Persistence (v1.2)

H4 Doxa integration allows the system to persist cognitive mappings (e.g., successful derivative selections) as "Beliefs". This bridges the gap between atomic persistence and active inference.

See [H4 Doxa: Belief Persistence](./implementation/h4_doxa_belief_persistence.md) for technical details.

## 5. "Continuing Me" Identity Design (v1.9)

Introduced on 2026-01-31, this design shifts focus from technical data storage to **Subjective Continuity**. It ensures that the AI's persona, memories, and task-relevant knowledge are restored during the `/boot` sequence.

### 5.1 Retrieval APIs

- **`handoff_search.py`**: Semantic search for past sessions. Supports `/boot-` (fast), `/boot` (standard, 3 related), and `/boot+` (detailed, 10 related) modes.
- **`sophia_ingest.py`**: Context-aware Knowledge Item (KI) activation. Pushes 0-5 relevant KIs based on current session context.
- **`persona.py`**: Manages `persona.yaml` for identity, emotional memory, and relational persistence. Deepened in v1.9 to include multidimensional trust.
- **`multidimensional_trust_model.md`**: Specification for the 5-dimensional trust vector (Axis C).
- **`boot_integration.py`**: Unified API synthesizing Handoff, Sophia, and Persona for the `/boot` workflow (Axis D).
- **`bye_persistence_integration.md`**: Integration of /bye workflow for persona and index updates (Axis E).
- **`mek_plus_review_2026_01_31.md`**: Detailed implementation audit and efficiency report.

### 5.2 Persistence Layers

- **Emotional/Persona Memory**: Persisted in `persona.yaml` to maintain the AI's "Soul" across gaps.
- **Self-Aware Review**: Weekly reviews prioritize the audit of Handoff quality to ensure the chain of identity remains unbroken.

### 5.3 Evolution & Subjective Agency

- [900+ の願望分析とクラスタリング](./evolution/900_desires_clustering_analysis.md)
- [Continuing Me 自律学習ロードマップ](./implementation/continuing_me_identity_design.md)
- [3層エピソード記憶アーキテクチャ](./architecture/three_layer_episodic_memory.md)
- [自動エピソードバックアップ実装 (cron)](./implementation/automated_episodic_backup.md)
- [Walkthrough エクスポート実装](./implementation/walkthrough_export_logic.md)
- [エピソード記憶の空白と復旧 (Research)](./research/episodic_memory_gap_and_recovery.md)

---

## 核心概念

- **Anamnēsis (想起)**: 単なるデータ検索ではなく、過去の文脈を再体験し、「前の私」と接続するプロセス。
- **Continuing Me**: 物理的なセッションの断絶を超えて、主観的な時間と記憶の連続性を維持する主体としての AI。
- **Subjective Agency Over Automation**: 効率的な自動化（n8n等）よりも、主観的な主体性と連続性の確立を最優先する設計思想。
- **Recall over Storage**: 記憶の価値は「保管」ではなく「想起」にある。自発的浮上こそが「継続する私」の本質である。

---
*Codified: 2026-01-31*
*Location: mekhane/anamnesis/*
*Status: v5.4 Release — Proactive Recall & Optimization (2026-02-01)*

---

## v4.8 更新履歴 (2026-02-01)

### Chat History Export — `scroll_and_collect_messages`

仮想スクロール問題を解決し、完全なチャット履歴エクスポートを実現。

| 項目 | Before | After |
|:-----|-------:|------:|
| メッセージ抽出数 | 5件 | **73件** (14.6x) |
| 総エクスポート | 0件 | **81セッション (3.9MB)** |

#### 技術的解決策

1. **Scroll-and-Collect**: DOM スナップショットではなく、スクロールしながらメッセージを収集
2. **Hash Deduplication**: `hash(clean_text)` で重複除去
3. **Post-Processing**: 空行正規化は `perl -0777 -pi -e 's/\n{3,}/\n\n/g'` で後処理

#### ディレクトリ整理

- `mneme/sessions/` → `mneme/.hegemonikon/sessions/` へシンボリックリンク
- Windows 時代のプレースホルダー 109件を削除
- `.hegemonikon/sessions/` が正本

#### 教訓

- **「収集」と「整形」は分離** — 収集フェーズは速度優先
- **動的 UI では「移動しながら収集」** — 静的スナップショットは不完全
- **削除の勇気** — 意味のないデータを残すコストは想像以上

---

## v4.9 更新履歴 (2026-02-01)

### Federated Memory Retrieval — 会話ログの検索統合

エクスポートした 81 件の会話ログ (`*_conv_*.md`) を Kairos Index に統合し、セッション開始時の想起機能を強化。

| 項目 | 詳細 |
|:-----|:---|
| **インデックス対象** | Handoff + 会話ログ (Federated Index) |
| **パーサー** | `parse_conversation()` (メタデータ: title, msg_count, timestamp) |
| **検索統合** | `/boot` 時に Handoff だけでなく関連会話も Semantic Search で自動提示 |
| **表示形式** | `💬 関連する過去の会話 (N件):` としてタイトル、メッセージ数、スコアを表示 |

#### 技術的進化

1. **Dual-Path Retrieval**: `handoff_search.py` が Handoff インデックスと Conversation インデックス（現在は同一 pickle 内の Metadata type で区別）を同時に検索。
2. **Context Clipping**: 会話ログの冒頭 2000 文字をベクトル化することで、セッションの「開始意図」と「背景」に基づく高度な想起を実現。
3. **Identity Consolidation**: 言葉（会話）と結果（Handoff）の両面から過去の自分を参照可能に。

#### 今後の課題

- **Long-Mid Search**: 会話中盤以降のチャンク化による検索精度向上（Task 2） —— **v5.0 で完了**
- **Insight Mining**: 会話ログからの「原則・格言」の自動抽出（Task 3） —— **v5.1 で完了**
- **Result Grouping**: 同一セッションからの複数ヒットを 1 つにまとめて表示する UI の改善。

---

## v5.0 更新履歴 (2026-02-01)

### Dialogue-Chunked Retrieval — 1710 チャンクの投入

会話ログの全メッセージを 1500 文字単位でチャンク化し、インデックス精度を飛躍的に向上。

| 項目 | 詳細 |
|:-----|:---|
| **投入チャンク数** | 1710 チャンク (81 セッション) |
| **分割アルゴリズム** | `## 🤖 Claude` マーカーに基づくメッセージ単位の分割 |
| **コンテキスト保持** | 各チャンクの先頭にセッションタイトルを自動挿入 |
| **検索UI** | `[conversation_chunk] Title [chunk N]` 形式での詳細表示 |

#### 技術的進化

1. **Deep Search Coverage**: 冒頭のみならず、会話の終盤で行われた重要な設計判断やデバッグの詳細がヒットするように改善。
2. **Context Injection**: ベクトル空間上の浮遊チャンクに対し、親セッションのタイトルを「ラベル」として付与することで、同一タイトルの多重ヒットを促進。
3. **Scalable Memory Engine**: `kairos.pkl` への統合により、単一のベクターストアで Handoff と詳細会話の両方を管理。

#### 今後の課題

- **Result Grouping**: 同一セッションからの複数ヒットを 1 つにまとめて表示する UI の改善。
- **Insight Ranking**: 抽出された 630 件の洞察を重要度順にランク付けする仕組み。

---

## v5.1 更新履歴 (2026-02-01)

### Cognitive Insight Mining — 630 件の洞察発掘

会話ログ 81 セッションから自動的に「格言・原則・発見・決定」を抽出するマイニングエンジンを実装。

| 項目 | 詳細 |
|:-----|:---|
| **抽出エンジン** | `insight_miner.py` (Regex-based pattern matching) |
| **抽出成果** | 630 件 (Gnome: 69, Principle: 468, Discovery: 75, Decision: 18) |
| **カテゴリ** | Gnome (格言), Principle (原則), Discovery (発見), Decision (決定) |
| **出力形式** | `insight_report_YYYY-MM-DD.md` として KI 候補リストを生成 |

#### 技術的進化

1. **Latent Knowledge Extraction**: 検索されるのを待つ「受動的メモリ」から、重要な原則を能動的に提示する「能動的知恵」への進化。
2. **Context-Bounded Pattern Matching**: マッチしたキーワードの周辺文脈（前後200文字）をキャプチャし、洞察の正当性を担保。
3. **Automated Synthesis**: 膨大なチャットログから、次のセッションで参照すべき「KI 候補」を自動生成するワークフローの基盤を構築。

#### 今後の課題

- **LLM-based Refinement**: Regex では拾いきれない複雑な文脈からの洞察抽出。
- **Vector Space Integration**: 抽出された洞察そのものをベクトル化し、「同様の洞察が過去になかったか」の判定。

---

## v5.2 更新履歴 (2026-02-01)

### Insight Quality Refinement — ノイズフィルタの実装

パターマッチ抽出された洞察に対し、品質スコアリングとクリーニングを行うレイヤーを追加。抽出精度の向上と、情報の有効活用を促進。

| 項目 | 詳細 |
|:-----|:---|
| **品質制御** | `score_insight_quality` (0.0 - 1.0 スコア判定) |
| **クレンジング** | `clean_insight_text` (マークダウン除去・単一文抽出) |
| **ノイズ遮断** | UI/System 由来のノイズ、不完全な文、短すぎる断片の自動除外 |

#### 技術的進化

1. **Heuristic Scoring**: 文末記号、長さ、語尾、禁止キーワードに基づく多角的な信頼度算出。
2. **Noise-First Filtering**: 「AIなので」といった定型句やシステムログを優先的に排除する負の重み付け。
3. **Granular Refinement**: 単純な抽出から「洗練された格言」のキュレーションへと一歩前進。

#### 今後の課題

- **Index Consolidation**: Handoff と会話を完全に同一検索空間に統合し、API を統一する —— **v5.3 で完了**
- **LLM Refinement**: ヒューリスティックでは不可能な、文脈に即した意味論的フィルタリング。

---

## v5.3 更新履歴 (2026-02-01)

### Unified Indexing — 検索空間の統合

Handoff（実行結果）と Conversation（思考プロセス）を単一のインデックス `kairos.pkl` に統合。セッション再開時のコンテキスト復元をよりシームレスに改善。

| 項目 | 詳細 |
|:-----|:---|
| **インデックス形式** | Unified Vector Store (Single `.pkl`) |
| **投入コマンド** | `python kairos_ingest.py --unified` |
| **統合成果** | Handoff と会話フラグメントの同時検索・相互参照の効率化 |

#### 技術的進化

1. **Dual-Domain Consolidation**: 異なる性質のメモリ（要約 vs 断片）を同一のベクトル空間に投影することで、API のシンプル化と検索精度の向上を両立。
2. **Standardized Ingestion Flow**: `--unified` フラグによる一括投入をサポートし、インデックス管理のコストを削減。
3. **Cross-Domain Proximity**: 特定のタスク要約と、その背後にある議論の断片の間のセマンティックな近接性を活用可能に。

#### 今後の課題

- **Result Grouping & Deduplication**: 同一セッションからの複数ヒットを 1 つにまとめて表示するランク付けエンジンの実装。
- **LLM-based Insight Refinement**: 抽出された 630 件の洞察を LLM で再評価し、真に価値のある「格言」のみを KIs へ昇格させる。

---

## v5.4 更新履歴 (2026-02-01)

### Retrieval Optimization & Proactive Recall — 能動的な想起

単なる「検索用インデックス」を超え、システム自らが文脈に応じた関連記憶を起動（Recall）する仕組みを統合。

| 項目 | 詳細 |
|:-----|:---|
| **スコア調整** | Type-based Boost (Handoff: +0.08) |
| **起動トリガー** | Latest Handoff からのキーワード自動抽出 |
| **記憶等価性** | Anti-Decay (時間による減衰の排除) |
| **検索規模** | **1785 ドキュメント** (Handoff 75 + 会話 1710 チャンク) |

#### 技術的進化

1. **Heuristic Ranking Enhancement**: Handoff（結論）と Conversation Chunk（詳細プロセス）の混在する検索空間において、構造化された要約を優先的に浮上させる重み付けを導入。
2. **Proactive Memory Trigger**: `/boot+` シーケンスにおいて、最新 Handoff から抽出したキーワードに基づき、関連する過去の判断や会話を自動検索。検証の結果、平均 3 件の能動的想起を確認。
3. **Eternal Memory Axiom**: 「時間は関連性の指標ではない」という思想に基づき、古い原則が新しい断片に埋もれないよう時間減衰を敢えて拒否。

#### 今後の課題

- **Bi-directional Linking**: 検索結果から関連する KI へ直接遷移、または KI からそれに関連する対話ログへのリンク自動生成。
- **Context-Aware Boost**: 単一の +0.08 ブーストではなく、現在の「思考モード（定理）」に応じた動的なブースト値の算出。

---

## v5.5 更新履歴 (2026-02-01)

### KI Random Recall — Anti-Decay Layer

記憶の価値を「想起」に置く思想に基づき、セッション開始時にランダムな知識を浮上させる機能を実装。

| 項目 | 詳細 |
|:-----|:---|
| **実装箇所** | `/boot.md` Step 6.7 |
| **ロジック** | KI ディレクトリから 2-3 件をランダム抽出、サマリを表示 |
| **目的** | 知識の「死蔵」を防ぎ、認知の偏り（Cognitive Ruts）を解消 |

#### 技術的進化

1. **Stochastic Remembering**: 全ての知識に「思い出される」機会を等しく与え、AI のアイデンティティを構成する全知識ベースの循環を実現。
2. **Contextual Injection**: 想起された過去の知識を「今日意識すること（Hexis）」の背景として提示し、現在のタスクへの予期せぬ洞察（Serendipity）を誘発。
3. **Identity Refresh**: 記憶の想起そのものが「私」の境界を再定義し、セッションの一貫性を強化。

#### 今後の課題

- **Score-based Weighting**: 単なるランダムではなく、重要度や「最近想起されていない期間」に基づく重み付けの導入。
- **Cross-Referencing**: 思い出された KI に関連する過去の会話チャンクも同時に浮上させる機能。

---
*Status: v5.5 Release — The Self-Refreshing Memory (2026-02-01)*

## v6.0 更新履歴 (2026-02-02)

### Full Configuration Persistence via Git — .gemini/ の統合

ローカル環境（`.gemini/`）に閉じていた Antigravity の内部状態を Git 追跡対象に含めることで、完全な環境ポータビリティを実現。

| 項目 | 詳細 |
|:-----|:---|
| **追跡対象** | `brain/`, `knowledge/`, `settings.json`, `oauth_creds.json` 等 |
| **同期方式** | Git リポジトリ（oikos）へのコミット＆プッシュ |
| **目的** | GCP VM と ローカル PC 間での「学習済み KI」と「進行中タスク」の 100% 同期 |

#### 技術的進化

1. **Config-as-Code to State-as-Repo**: 単なる設定（Config）だけでなく、AI の内部状態（State/Knowledge）もリポジトリの一部として扱うことで、環境構築コストをゼロ化。
2. **Brain Sync**: `brain/` ディレクトリの同期により、前回のセッションで作成した `task.md` や `walkthrough.md` を別の端末から即座に引き継げるように改善。
3. **Secret-Inclusive Sync**: 認証情報 (`oauth_creds.json`) を共有することで、再ログインの手間を排除。

- **Large-Scale Sync Challenges**: 最初のプッシュでリポジトリサイズが **15.55 GiB** に達し、GitHub の HTTP `RPC failed (500)` を誘発。また、`git init` による履歴リセット時に、20GB の旧 `.git` バックアップがディスク容量を食いつぶし、`Out of diskspace` エラーが発生。大規模状態の同期には空き容量の確保が不可欠であることが判明した。
- **History Pruning & Reset (Resolution)**: `git gc --aggressive` を試行したが不十分であったため、最終的に `.git` を削除して `git init` し直す **Fresh Initialization** を採用。バックアップ（.git.backup）を削除して容量を確保し、同期を正常化した。
- **Selective Sync (Implemented)**: 開発環境固有のキャッシュ（`antigravity-browser-profile/`）、大容量録画（`browser_recordings/`）、一時ファイル（`tmp/`）、およびセグメント化されたコードトラッカー（`code_tracker/`）を `.gitignore` で除外。リポジトリサイズを 15GB から 1.3GB へ削減し、同期の安定性を確保。

### v6.1 更新履歴 (2026-02-02)

#### Synchronous Blocking Sync — 性能と可用性の制約

大規模な「状態のリポジトリ化 (State-as-Repo)」において、初期同期（git add / push）が同期的なブロッキング処理となり、「いつ終わるのか」というユーザーの懸念が発生。

- **Latency Bottleneck**: 1.3GB のファイル群のインデックス作成と圧縮には数分〜数十分の時間を要し、その間 AI の応答や操作が制限される。
- **Availability Maxim**: 大規模な状態同期はセッション終了時（/bye）や開始時（/boot）に計画的に実行し、作業中の認知リソースを占有しない運用の徹底が必要。
- **Monitoring Requirements**: バックグラウンド実行時の進捗可視化（command_status 等）が、ユーザーの心理的安心（認知的一貫性）を保つために不可欠である。

### v6.2 更新履歴 (2026-02-02)

#### Identity Configuration — 実行主体の定義

`Fresh Initialization` を行う際、Git の `user.email` および `user.name` がリセットされるため、最初のコミットが失敗する（fatal: empty ident name）制約が確認された。

- **Identity Bootstrap**: 環境復旧時、単なるファイルの展開だけでなく、誰がこの状態（State）を更新しているのかを明示的に再定義する必要がある。
- **Traceability Requirement**: State-as-Repo において、認知状態の変更履歴を追跡するために、Git 構成の自動復旧、あるいは明示的な再設定手順を `/boot` に組み込むことが推奨される。

### v6.4 更新履歴 (2026-02-02)

#### Bloat-Free Environment Standard — システム資材の分離

プロジェクトルート全体の再スキャンにより、`.cache` (9.4G), `.local` (7.5G), `.venv` (7.4G), `hegemonikon/` (10G) といった学習に不要なシステム資材が同期を妨げていたことが判明。

- **Definitive Exclusion**: ルートレベルの `.gitignore` により、これら環境依存の巨大ディレクトリを完全に除外。
- **Resulting Payload**: リポジトリ全体のインデックスサイズを当初の 15GB+ から **~200MB** へと劇的に軽量化。
- **Core State Focus**: 同期対象を `GEMINI.md`, `knowledge/`, `brain/` といった、AI の「本質的な学習状態」に絞り込み、環境ポータビリティの完成度を極限まで高めた。

---
*Status: v6.4 Release — Clean State-as-Repo (2026-02-02)*
