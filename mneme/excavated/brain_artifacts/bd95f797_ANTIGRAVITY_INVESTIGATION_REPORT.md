# Antigravity 挙動調査レポート

> **調査日時**: 2026-01-18 21:00
> **目的**: 現行IDE設定構造の把握と最適化戦略の策定

---

## 📍 発見: 4つの設定レイヤーが存在

調査の結果、設定が**4つの異なる場所**に分散していることが判明しました。

```
┌─────────────────────────────────────────────────────────────────────┐
│ Layer A: グローバルカーネル (~/.gemini/)                            │
├─────────────────────────────────────────────────────────────────────┤
│ 📄 GEMINI.md (v1.0.0 - KERNEL_DOCTRINE)                            │
│    - 第零原則: 意志より環境                                         │
│    - Protocol G/D/D-Extended/V への参照                             │
│                                                                     │
│ 📄 rules.md (Flow AI Development Rules v4.0.0)                     │
│    - Flow AI プロジェクト固有のルール                               │
│    - Antigravity標準 (.agent/rules/) ではない位置                  │
│                                                                     │
│ 📁 .agent/workflows/ (4ファイル)                                   │
│    ├── do.md           → /do (憲法ロード)                          │
│    ├── global-rules.md → P1-P9エラー防止プロトコル (320行!)        │
│    ├── flow-dev-ecosystem.md                                        │
│    └── update-manual.md                                             │
│                                                                     │
│ 📁 Forge/ (ローカルコピー)                                         │
│    ├── GEMINI_OMEGA_v5.md                                          │
│    └── prompts/modules/ (OMEGA XMLモジュール)                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Layer B: Google Drive Forge (G:\その他のパソコン\Forge\.gemini\)   │
├─────────────────────────────────────────────────────────────────────┤
│ 📄 GEMINI.md (OMEGA-v5.0.0 - FORGE_CONSTITUTION)                   │
│    - Anti-Confidence Doctrine                                       │
│    - 二軸原則 (Facts First, Opinion Second)                        │
│    - OMEGA Core Modules (M0/M1/M6/M7/M9)                           │
│                                                                     │
│ 📁 prompts/modules/ (OMEGAモジュール)                              │
│    ├── M0_MISSION_COMMAND.xml (7KB)                                │
│    ├── M1_INPUT_GATE.xml (2KB)                                     │
│    ├── M6_CONTEXT_NEXUS.xml (6KB)                                  │
│    ├── M7_ADVERSARIAL_COUNCIL.xml (5KB)                            │
│    └── M9_PROTOCOL_LOADER.xml (4KB)                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔴 発見された問題

### 問題1: GEMINI.md が3箇所に存在

| 場所 | バージョン | 内容 |
|------|------------|------|
| `~/.gemini/GEMINI.md` | v1.0.0 KERNEL_DOCTRINE | 第零原則 (意志より環境) |
| `~/.gemini/Forge/GEMINI_OMEGA_v5.md` | OMEGA-v5.0.0 | OMEGA概要 (簡略版) |
| `G:\その他のパソコン\Forge\.gemini\GEMINI.md` | OMEGA-v5.0.0 | 完全版 (Anti-Confidence + 二軸原則) |

**問題**: どれが「マスター」か不明。内容も部分的に重複・非整合。

---

### 問題2: グローバル rules.md の位置が非標準

```
現在の位置:  ~/.gemini/rules.md (ルートに孤立)
標準の位置:  ~/.gemini/.agent/rules/*.md
```

**問題**: Antigravityが `rules.md` を自動的に読み込むかは**未確認**。

---

### 問題3: global-rules.md が Workflow になっている

`~/.gemini/.agent/workflows/global-rules.md` (320行) には:
- Protocol G/D/D-Extended/V
- P1-P9 エラー防止プロトコル

**問題**: これは「常時適用されるべきRules」であり、「手動起動するWorkflow」ではないはず。

---

### 問題4: OMEGA XMLモジュールが2箇所に存在

| 場所 | サイズ | 状態 |
|------|--------|------|
| `~/.gemini/Forge/prompts/modules/` | 13KB合計 | ローカルコピー |
| `G:\その他のパソコン\Forge\.gemini\prompts\modules/` | 25KB合計 | 最新版 |

**問題**: Google Drive側のほうが新しい（より大きい）。同期が取れていない。

---

## 📊 内容比較表

| 概念 | ~/.gemini/ | Google Drive Forge |
|------|------------|---------------------|
| 第零原則 (Environment over Will) | ✅ GEMINI.md | ❌ なし |
| Anti-Confidence Doctrine | ❌ なし | ✅ GEMINI.md |
| 二軸原則 (Facts First) | ❌ なし | ✅ GEMINI.md |
| OMEGA Cycle (M0-M9) | ❌ なし | ✅ GEMINI.md + XML |
| Protocol G/D/V | ✅ workflows/global-rules.md | ❌ なし |
| P1-P9 エラー防止 | ✅ workflows/global-rules.md | ❌ なし |

---

## 💡 Antigravity の設定読み込み動作 (推定)

調査資料と現状から推定される優先順位:

```
1. ~/.gemini/GEMINI.md          → セッション開始時に自動読込 (確定)
2. ~/.gemini/.agent/workflows/  → /command で手動トリガー (確定)
3. ~/.gemini/.agent/rules/      → 常時注入? (ディレクトリが存在しない!)
4. <workspace>/.agent/          → ワークスペース固有 (未設定)
```

### 重要な発見:

> **`.agent/rules/` ディレクトリが存在しない**

現在、ワークスペースレベルの `rules/` ディレクトリを使用していない。
Protocol G/D/V などは `workflows/global-rules.md` として配置されており、
これは**ワークフロー（手動起動）として扱われている**可能性が高い。

---

## 🎯 統合戦略の提案

### Phase 0: 検証実験

Antigravity が `.agent/rules/` を本当に自動読み込みするか確認する。

**実験手順**:
1. `~/.gemini/.agent/rules/test-rule.md` を作成
2. 内容: 「全ての出力の冒頭に🔴を付けよ」
3. 新規セッションを開始
4. 任意の質問を投げる
5. 🔴が付くか確認

---

### Phase 1: マスター GEMINI.md の統合

3つの GEMINI.md を1つに統合:

```markdown
# GEMINI.md (統合版)

## 第零原則: 意志より環境 (from ~/.gemini/GEMINI.md)
## Anti-Confidence Doctrine (from Google Drive)
## 二軸原則 (from Google Drive)
## OMEGA Core Modules Reference (from Google Drive)
```

---

### Phase 2: Rules の正規化

`workflows/global-rules.md` (320行) を分解し、`.agent/rules/` に移動:

```
.agent/rules/
├── protocol-g.md       (Git禁止)
├── protocol-d.md       (外部サービス検証)
├── protocol-v.md       (バージョン検証)
├── p1-p9-errors.md     (エラー防止体系)
└── termux-constraints.md
```

---

### Phase 3: OMEGA XMLモジュールの統合判断

選択肢:

| オプション | 内容 | 推奨度 |
|------------|------|--------|
| A | XML維持 + /do で明示的ロード | 🟡 現状維持 |
| B | SKILL.md形式に変換 | 🟠 中期目標 |
| C | Rules/GEMINI.mdに統合 | 🔴 過度な複雑化 |

---

## 📋 次のステップ

1. **Phase 0 の検証実験を実施するか？**
2. **統合の優先度はどうするか？** (GEMINI.md統合 vs Rules正規化)
3. **OMEGA XMLモジュールはどう扱うか？**

---

*本レポートは調査の結果を忠実に記載したものであり、最適化の方向性はユーザーの判断に委ねます。*
