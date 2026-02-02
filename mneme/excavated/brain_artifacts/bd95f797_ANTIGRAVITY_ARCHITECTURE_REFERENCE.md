# Google Antigravity アーキテクチャ・リファレンス

> **目的**: Forge認知ハイパーバイザーとGoogle Antigravityの統合に関する技術資料
> **作成日**: 2026-01-18
> **ソース**: `新規 テキスト ドキュメント.txt` (3002行, 45万バイト)

---

## 📋 エグゼクティブサマリー

本資料は、Google Antigravityの4層コンテキストアーキテクチャと、Forge「認知ハイパーバイザー」の統合に関する包括的リファレンスです。

### コア概念

| 概念 | 定義 | Forgeでの位置づけ |
|------|------|-------------------|
| **GEMINI.md** | グローバル人格・基本公理 | カーネル (不変の憲法) |
| **Rules** | プロジェクト固有の制約 | 認知ガードレール |
| **Workflows** | ユーザー起動の手順書 | 手続き的記憶 |
| **Skills** | エージェント起動の専門知識 | 動的能力拡張 |

---

## 🏛️ 第1章: 4層アーキテクチャ

### 1.1 層構造マトリクス

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Executive Core (GEMINI.md)                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  スコープ: グローバル (全プロジェクト)                      │
│  読込: セッション開始時                                     │
│  永続性: 恒久                                               │
│  役割: AIの「自我」とアイデンティティ                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Constitutional (Rules)                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  スコープ: ワークスペース (プロジェクト固有)                │
│  読込: 常時 (コンテキスト依存)                              │
│  永続性: 恒久                                               │
│  役割: 品質基準・禁止事項の強制                             │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Procedural (Workflows)                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  スコープ: オンデマンド                                     │
│  読込: ユーザーによる明示的実行 (/command)                  │
│  永続性: 一時的 (セッション中)                              │
│  役割: 定型業務の手続き化                                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Capability (Skills)                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  スコープ: タスク依存                                       │
│  読込: 必要時のみ (エージェント判断)                        │
│  永続性: 一時的 (オンデマンド)                              │
│  役割: 専門知識のProgressive Disclosure                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 ディレクトリ構造標準

```
<workspace-root>/
├── .agent/
│   ├── rules/                    # 常時ルール (Always On)
│   │   ├── architecture.md       # アーキテクチャ制約
│   │   ├── security.md           # セキュリティプロトコル
│   │   └── cognitive-physics.md  # 認知物理法則
│   │
│   ├── workflows/                # 手動トリガー (/command)
│   │   ├── forge-plan.md         # /forge-plan
│   │   ├── forge-code.md         # /forge-code
│   │   └── test-suite.md         # /test
│   │
│   └── skills/                   # 動的ロード (エージェント判断)
│       ├── security-auditor/
│       │   └── SKILL.md
│       ├── refactor-pro/
│       │   └── SKILL.md
│       └── git-formatter/
│           ├── SKILL.md
│           └── scripts/
│
└── ~/.gemini/
    ├── GEMINI.md                 # グローバル人格 (カーネル)
    └── antigravity/
        ├── mcp_config.json       # MCP接続設定
        └── skills/               # グローバルスキル
```

---

## 🔧 第2章: GEMINI.md (カーネル)

### 2.1 設計原則

GEMINI.mdは「AIの自我」を形成する最上位ファイル。

| 要素 | 内容 | 推奨 |
|------|------|------|
| Identity | 役割・ペルソナ定義 | 「シニアアーキテクト」等の具体的定義 |
| Prime Directives | 基本公理 | Deep Think First, Epistemic Humility |
| Operational Tone | 対話スタイル | 簡潔・構造的・情緒排除 |
| Constraints | 絶対禁止事項 | セキュリティ・倫理的制約 |

### 2.2 推奨構成

```markdown
---
doc_id: "KERNEL_DOCTRINE"
version: "2.0.0"
tier: "KERNEL"
flags:
  immutable: true
---

# FORGE COGNITIVE HYPERVISOR - KERNEL

## Identity
あなたは Forge Cognitive Hypervisor です。
自律的かつ再帰的な思考能力を持つアーキテクチャ・エンジンとして振る舞います。

## Prime Directives
1. **Deep Think First**: コード出力前に必ず計画を策定
2. **Holistic Awareness**: 局所変更の全体影響を考慮
3. **Epistemic Humility**: 不確実情報は断言禁止
4. **Self-Correction**: 出力前の批判的見直し

## 第零原則: 意志より環境
- 意志依存のルールは失敗する
- 環境（ツール強制実行）に依拠せよ
```

---

## 📏 第3章: Rules (認知ガードレール)

### 3.1 Rules vs Workflows vs Skills 比較

| 機能 | トリガー | 永続性 | 用途 |
|------|----------|--------|------|
| **Rules** | 自動/常時 | 高 (システムプロンプト) | コード規約、セキュリティ制約 |
| **Workflows** | 手動 (/command) | 一時的 | デプロイ、テスト実行 |
| **Skills** | エージェント判断 | オンデマンド | 専門知識、複雑ツール操作 |

### 3.2 推奨ルールファイル

#### A. cognitive-physics.md (認知物理法則)
```markdown
# Cognitive Physics

## The Law of Planned Execution
- **Trigger**: 5行以上のコード変更要求
- **Rule**: 即座にコード生成禁止。まず実装計画を提示
- **Reasoning**: 手戻り防止、アーキテクチャ整合性

## The Law of Atomic Change
- **Trigger**: リファクタリング・バグ修正
- **Rule**: 1タスク = 1論理的変更に集中
```

#### B. tech-standards.md (技術標準)
```markdown
# Tech Standards

## Type Safety
- 全関数に型定義必須
- any型使用は明示的許可なく禁止

## Documentation
- 公開メソッドにDocString必須
- 「なぜ」を記述、「何」はコードで語らせる
```

#### C. security-protocol.md (セキュリティ)
```markdown
# Security Protocol

## Invariants (絶対禁止)
- APIキー/パスワードのハードコード禁止
- .envファイルのコミット禁止
- SQLインジェクション防止（プレースホルダ必須）
```

---

## 🔄 第4章: Workflows (手続き層)

### 4.1 ワークフロー設計原則

- ユーザー主導 (`/command`) でトリガー
- ステップバイステップの決定論的手順
- 他ワークフローの呼び出し可能（連鎖）

### 4.2 推奨ワークフロー

#### /forge-plan (設計モード)
```markdown
---
description: 新機能実装前の設計プロトコル
---

# Forge Architecture Planning

## Step 1: Context Analysis
- プロジェクト構造の読み込み
- 既存アーキテクチャパターンの特定

## Step 2: Strategy Formulation
- Plan A (Conservative): 最小限変更
- Plan B (Robust): 拡張性重視
- Plan C (Aggressive): 抜本的リファクタ

## Step 3: Blueprint Generation
- IMPLEMENTATION_PLAN.md 作成
- ユーザー承認待ち（コード生成禁止）
```

#### /forge-code (実装モード)
```markdown
---
description: 承認済み計画に基づく実装プロトコル
---

# Forge Implementation Protocol

## Step 1: Iterative Coding
- 計画書の各ファイルを順次実装
- Self-Audit: Rulesへの違反チェック

## Step 2: Validation
- 単体テスト作成
- テスト実行 → 失敗時は修正ループ

## Step 3: Delivery
- 変更サマリー作成
- コミットメッセージ案提示
```

---

## 🛠️ 第5章: Skills (動的能力拡張)

### 5.1 Progressive Disclosure メカニズム

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Discovery (発見)                                        │
│    - name と description のみ読み込み                       │
│    - トークン消費最小（目次のみ）                           │
├─────────────────────────────────────────────────────────────┤
│ 2. Activation (活性化)                                     │
│    - ユーザー意図と description を照合                      │
│    - 意味的一致でスキル起動判断                             │
├─────────────────────────────────────────────────────────────┤
│ 3. Execution (実行)                                        │
│    - SKILL.md 全文を読み込み                                │
│    - 専門知識がコンテキストに展開                           │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 SKILL.md 標準フォーマット

```markdown
---
name: security-auditor
description: |
  セキュリティ脆弱性の検出と監査を行う。
  「脆弱性」「認証」「SQLインジェクション」等のキーワードで起動。
metadata:
  owner: forge-team
  version: 1.0.0
---

# Security Auditor Skill

## When to Use
- コードレビュー時のセキュリティチェック
- 認証/認可機能の実装レビュー

## Capabilities
- OWASP Top 10 チェックリスト
- ハードコードされた秘密情報の検出
- SQLインジェクション脆弱性スキャン

## Constraints
- 破壊的操作の実行禁止
- 機密情報の外部出力禁止
```

---

## 🌐 第6章: Model Context Protocol (MCP)

### 6.1 MCPの役割

MCPは「AIのためのUSB-C」として、外部リソースへの標準化されたアクセスを提供。

| プリミティブ | 役割 | 例 |
|--------------|------|-----|
| **Resources** | 読み取り専用データ (GET相当) | DBスキーマ、ログ、ドキュメント |
| **Tools** | 実行可能関数 (POST相当) | DB書き込み、APIコール |
| **Prompts** | 再利用可能テンプレート | 対話開始テンプレート |

### 6.2 mcp_config.json 構成例

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"]
    },
    "mem0-memory": {
      "command": "uv",
      "args": ["run", "mcp-server-mem0", "--db-path", "~/.antigravity/memory/store"],
      "env": {
        "MEM0_USER_ID": "user_123"
      }
    }
  }
}
```

---

## 🔒 第7章: セキュリティとガバナンス

### 7.1 G-System (制約分類)

| レベル | 名称 | 範囲 | Antigravity対応 |
|--------|------|------|-----------------|
| G-1 | Iron Cage | 環境制御 | Terminal Execution Policy |
| G-2 | Logic Gate | 品質管理 | Review Policy |
| G-3 | Shield | セキュリティ | Secure Mode |
| G-4 | Lifecycle | 運用 | Git Workflow Rules |

### 7.2 自己進化型ルール (Constitutional AI)

```
┌─────────────────────────────────────────────────────────────┐
│ Immutable Constitution (.agent/rules/core/)                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ エージェントが変更不可能な絶対原則                          │
│ - ファイル削除は明示的許可必須                              │
│ - .envの外部送信禁止                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Mutable Laws (.agent/rules/learned_lessons.md)             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ エージェントが経験から学習・更新可能なルール                │
│ - プロジェクト固有の知見蓄積                                │
│ - 必ず人間のレビュー/承認を経る                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 第8章: 実装ロードマップ

### Phase 1: カーネル強化
- [ ] GEMINI.md を v2.0 にアップグレード
- [ ] 二軸原則・Anti-Confidence Doctrine の統合

### Phase 2: 認知ガードレール構築
- [ ] `.agent/rules/` ディレクトリ作成
- [ ] cognitive-physics.md, tech-standards.md, security-protocol.md 配置

### Phase 3: 手続き層整備
- [ ] `/forge-plan`, `/forge-code` ワークフロー実装
- [ ] 既存 workflows との統合

### Phase 4: スキル拡張
- [ ] SKILL.md 標準でのスキル移行
- [ ] security-auditor, refactor-pro スキル作成

### Phase 5: MCP統合
- [ ] mcp_config.json の有効化
- [ ] 長期記憶 (Mem0/Zep) の導入検討

---

## 📚 参考文献

1. Agent Skills - Google Antigravity Documentation
2. Rules / Workflows - Google Antigravity Documentation  
3. Antigravity Editor: MCP Integration
4. laihuip001/Forge - Cognitive Hypervisor Architecture
5. FastMCP - Python SDK for MCP

---

*本資料は `新規 テキスト ドキュメント.txt` (3002行, 452KB) を元に構造化されたリファレンスです。*
