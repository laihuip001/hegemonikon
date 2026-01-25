# 🔥 Forge - 認知ハイパーバイザー・プロンプトシステム

> **思考のOS** - AIを単なるチャットボットではなく、43の専門的な思考モジュールを搭載した拡張知能OSとして機能させる

[![Version](https://img.shields.io/badge/Version-2.0-blue)]()
[![Modules](https://img.shields.io/badge/Modules-44-green)]()
[![Protocols](https://img.shields.io/badge/Protocols-25-orange)]()

---

## 📖 概要

Forgeは、LLM（大規模言語モデル）を**構造化された思考フレームワーク**で拡張するプロンプトシステムです。

### 主な特徴

- **🧠 Cognitive Hypervisor** - 3つの動作モード（EXPLORER/BUILDER/AUDITOR）で品質を自動制御
- **📦 44の思考モジュール** - 発見→思考→行動→振り返りの4フェーズをカバー
- **🛡️ 25のプロトコル** - TDD、セキュリティ、アクセシビリティ等の品質ガードレール
- **📚 200+のプロンプト技術** - 最新の研究に基づくコンポーネントライブラリ

---

## 🚀 クイックスタート

### 基本的な使い方

1. **システムプロンプトに設定**  
   `The Cognitive Hypervisor Architecture.md` をAIのシステムプロンプトとして設定

2. **モジュールを呼び出す**  
   自然言語またはコマンド形式でモジュールを起動
   ```
   /考える/絞る/決断を下す
   ```

3. **AIが自動でルーティング**  
   課題を伝えると、最適なモジュールを提案

### 動作モード

| モード | トリガー | 特徴 |
|--------|----------|------|
| **EXPLORER** | アイデア出し、プロトタイプ | 速度重視、テストは任意 |
| **BUILDER** | 実装、修正、リファクタリング | 品質重視、TDD必須 |
| **AUDITOR** | レビュー、セキュリティ監査 | 分析のみ、コード生成なし |

---

## 📁 ディレクトリ構成

```
Forge/
├── 📄 README.md                          # このファイル
├── 📄 The Cognitive Hypervisor Architecture.md  # メインアーキテクチャ
│
├── 🔎 見つける/ (Find)
│   ├── 🤯 脳内を吐き出す.md
│   ├── 📥 情報を集める.md
│   └── ...
│
├── 🧠 考える/ (Think)
│   ├── 📊 広げる/ (Expand)
│   │   ├── 🔍 状況を把握する.md
│   │   └── ...
│   └── 🎯 絞る/ (Focus)
│       ├── ✅ 決断を下す.md
│       └── ...
│
├── ⚡ 働きかける/ (Act)
│   ├── 🔧 固める/ (Prepare)
│   └── ✨ 生み出す/ (Create)
│
├── 🔄 振り返る/ (Reflect)
│
├── 📋 protocols/                          # 25のプロトコルモジュール
│   ├── Module 01 DMZ Protocol.md
│   ├── Module 04 TDD Protocol.md
│   └── ...
│
└── 📚 knowledge/                          # 知識ベース
    ├── Prompt Engineering Component Library.md
    └── ...
```

---

## 🛡️ プロトコル一覧

### 環境制御 (G-1: Iron Cage)
| ID | 名前 | 概要 |
|----|------|------|
| 01 | DMZ Protocol | 重要ファイルの読取専用保護 |
| 02 | Directory Topology Lock | ディレクトリ構造の変更制限 |
| 03 | Dependency Quarantine | 依存関係の隔離と承認 |
| 19 | Docker First | コンテナ化必須 |

### 品質管理 (G-2: Logic Gate)
| ID | 名前 | 概要 |
|----|------|------|
| 04 | TDD Protocol | テスト駆動開発の強制 |
| 05 | Domain Language | ユビキタス言語の徹底 |
| 06 | Complexity Budget | 複雑度の予算管理 |
| 15 | Atomic Design | UI コンポーネントの原子設計 |
| 16 | Accessibility Mandate | WCAG 2.1 AA 準拠 |

### セキュリティ (G-3: Shield)
| ID | 名前 | 概要 |
|----|------|------|
| 09 | Mutation Testing | 変異テストによる検証 |
| 11 | Red Teaming | 自動攻撃シミュレーション |
| 12 | Chaos Monkey | 障害耐性テスト |

### 運用 (G-4: Lifecycle)
| ID | 名前 | 概要 |
|----|------|------|
| 14 | Narrative Commit | コミットメッセージの物語化 |
| 17 | Structured Logging | 構造化ログの強制 |
| 18 | Feature Flags | フィーチャーフラグ管理 |
| 25 | Rollback Strategy | ロールバック戦略の必須化 |

---

## 🧠 思考モジュール

### /🔎 見つける (Find) - 5モジュール
情報収集と探索のフェーズ

### /🧠 考える (Think) - 20モジュール
- **📊 広げる (Expand)** - 発散思考（9モジュール）
- **🎯 絞る (Focus)** - 収束思考（11モジュール）

### /⚡ 働きかける (Act) - 14モジュール
- **🔧 固める (Prepare)** - 準備（6モジュール）
- **✨ 生み出す (Create)** - 創造（8モジュール）

### /🔄 振り返る (Reflect) - 5モジュール
評価と改善のフェーズ

---

## 📚 プロンプト技術ライブラリ

| カテゴリ | 技術数 | 用途 |
|----------|--------|------|
| Frameworks & Structures | 30+ | プロンプトの骨格設計 |
| Reasoning Engines | 28 | 推論能力の強化 |
| Safety & Guardrails | 14 | 安全性の担保 |
| Optimize & Efficiency | 12 | コスト・速度最適化 |
| Agents & Tools | 14 | 自律動作・ツール連携 |
| Evaluation & Refinement | 20+ | 品質評価・改善 |

詳細は `Prompt Engineering Component Library.md` を参照。

---

## 🛠️ 開発ロードマップ

- [x] 思考モジュール（44個）
- [x] プロトコルモジュール（25個）
- [x] Prompt Engineeringライブラリ
- [ ] CLI ツール
- [ ] Web インターフェース
- [ ] Google AI Studio 統合

---

## 📄 ライセンス

MIT License

---

## 🙏 謝辞

このプロジェクトは以下の研究・技術に基づいています：

- Chain-of-Thought Prompting (Wei et al., 2022)
- Self-Consistency (Wang et al., 2022)
- Tree of Thoughts (Yao et al., 2023)
- その他200+のプロンプトエンジニアリング研究