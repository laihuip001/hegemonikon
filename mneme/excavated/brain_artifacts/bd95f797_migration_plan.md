# OMEGA Skills Migration Plan

## 概要
「軍事級メタプロンプト機構」として設計されたOMEGAモジュール群を、Antigravityの `.agent/skills/` アーキテクチャに適合する形（Agent Skills）で再実装する。

## 現状のモジュール構成 (v5.0.0)

| ID | 名称 (Ver) | 役割 | 移行方針 |
|---|---|---|---|
| M0 | Mission Command | 人格・基本行動 | `GEMINI.md` に吸収済み（Kernel化） |
| M1 | Input Gate | 入力分析・リスク評価 | Skill化: `/skill m1` (リスク分析実行) |
| M6 | Context Nexus | 文脈維持・緊急停止 | Skill化: `/skill m6` (コンテキスト監査) |
| M7 | Adversarial Council | 多角的批評 | Skill化: `/skill m7` (評議会招集) |
| M9 | Protocol Loader | プロトコル提案 | `rules` に移行済みだが、高度な提案機能のみSkill化 |

## 欠番モジュール (M2-M5, M8) の行方

これらは以前のバージョン（v3/v4系）で存在したが、v5.0.0の「Deep-Think Archtecture」への移行時に**廃止または統合**された。

| ID | 名称 (旧) | 廃止理由 |
|---|---|---|
| M2 | Token Economizer | M9 (Protocol) と M0 (Kernel) に分散統合 |
| M3 | Memory Vault | Forgeのファイルシステムベース管理に移行 |
| M4 | Tool Arsenal | AntigravityのTool定義に標準化 |
| M5 | Output Formatter | 各モジュールの責務に分散 |
| M8 | Self-Evolution | 実験的機能のためコアから除外 (Skill化の候補) |

## 移行戦略

### A. Skill構造の標準化

各Skillは以下の構造を持つ:
- `SKILL.md`: マニュアル、プロンプトテンプレート
- `scripts/`: 必要に応じた補助スクリプト（Python/JS）

### B. 実装詳細

#### 1. M1: Input Gate (Humble Gatekeeper)
- **機能**: ユーザー入力のリスク分析、意図解釈、オプション提示
- **コマンド**: `/skill m1`
- **内容**: XMLプロンプトをMarkdown化し、思考プロセスを誘導

#### 2. M6: Context Nexus (The Watcher)
- **機能**: セッションの「意味論的漂流」を検知
- **コマンド**: `/skill m6`
- **内容**: `task.md` と `GEMINI.md` の乖離チェック

#### 3. M7: Adversarial Council (The Critics)
- **機能**: 6人の評議員による批判的レビュー
- **コマンド**: `/skill m7`
- **内容**: XML定義のペルソナをロードし、議論を展開させる

#### 4. M9: Protocol Strategist
- **機能**: 高度な状況におけるプロトコル適用の提案
- **コマンド**: `/skill m9`
- **補足**: `rules` ディレクトリとは別に、動的な戦略を提案

## 実行フェーズ

1. **ディレクトリ作成**: `.agent/skills/m1-input-gate` 等
2. **SKILL.md 作成**: 各XMLの内容をMarkdownに移植
3. **検証**: `/open m7` (または相当するコマンド) で動作確認

## 備考
「軍事級」の強度は、Skill化することで**On-Demand（必要な時だけ強力な支援を呼ぶ）**形式になり、常時ロードの負担を減らしつつ、必要な場面では最大限の能力を発揮できる。これはAntigravityの哲学と合致する。
