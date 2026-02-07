---
description: 出力モード。visual (画像生成), manual (マニュアル生成)。
hegemonikon: S2 Mekhanē
parent: ../mek.md
---

# 出力モード (Output Modes)

> S2 Mekhanē — 視覚的成果物とAI向けマニュアルの生成。

## Constraints

- visual モードはプロンプト構造を具体的に指定する
- manual モードは「補完の余地がない粒度」で記述する
- 出力はテーブル形式で構造化する

---

## visual — 視覚的成果物生成

**CCL**: `/mek.visual` = `/mek+{output=image}`
**目的**: 視覚的成果物（UI画像、インフォグラフィック）を生成する
**発動**: `/mek visual` または「画像」「モックアップ」「スクショ」「インフォグラフィック」

### プロンプト構造

ソフトウェアUI再現のテンプレート:

```text
A realistic screenshot of [ソフトウェア名] [バージョン] on [OS],
showing [画面の状態]. Japanese interface.

EXACT WINDOW STRUCTURE (top to bottom):
1. TITLE BAR: "[タイトル]" with [OS] buttons
2. MENU BAR: [メニュー項目...]
3. TOOLBAR: [ツールバー要素...]
4. MAIN CONTENT AREA:
   - LEFT SIDE (X%): [左側]
   - RIGHT SIDE (Y%): [右側]
5. FOOTER: [ステータスバー]

Style: Photorealistic [OS] screenshot. NOT a mockup.
```

### 精度向上原則

| 要因 | 低精度 | 高精度 |
|:-----|:-------|:-------|
| 抽象度 | 「UIを作って」 | 「FileMaker Pro 2024のWindows画面」 |
| 構造 | 「ボタンを配置」 | 「TITLE BAR → MENU BAR → CONTENT」 |
| スタイル | 「きれいに」 | 「photorealistic screenshot, NOT a mockup」 |

### 日本語テキスト対策

| 文字数 | 推奨アプローチ |
|:-------|:---------------|
| 5文字以下 | そのまま日本語で指示 |
| 6-15文字 | 英語で生成 → 後から画像編集 |
| 16文字以上 | テキストなしで生成 |

### 必須テクニック

1. **Critical Constraint Repetition**: 冒頭と末尾に制約を繰り返す
2. **Negative Prompts**: 「DO NOT include: device frames, watermarks...」
3. **Weighted Style Blending**: 「60% photorealistic, 30% minimalist」

### Output Format

**[S2 Mekhanē: Visual]**

| フィールド | 内容 |
|:-----------|:-----|
| 生成対象 | {何を生成するか} |
| プロンプト | {構造化プロンプト} |
| 出力 | {画像ファイルパス} |
| 品質確認 | {日本語精度 / 構造再現度} |

---

## manual — マニュアル生成

**CCL**: `/mek.manual` = `/mek+{output=procedure}`
**目的**: Gemini/Jules向けの作業マニュアルを生成する
**発動**: `/mek manual` または「マニュアル」「手順書」「作業指示」

### 粒度ルール — Gemini補完防止

Geminiは「言われていないこと」を補完する。マニュアルは補完の余地がない粒度で記述する。

| ルール | 不可 | 可 |
|:-------|:-----|:---|
| 行番号を指定 | 「表を更新」 | 「58行目〜64行目の表を更新」 |
| 完全コピー可能 | 「Taxis行を追加」 | 「以下を貼り付け: ...」 |
| before/after | 「表記を統一」 | 「Kairos → K-series に変更」 |
| 禁止事項明記 | （記載なし） | 「列順を変更しない」 |

### オプション

| オプション | 出力形式 | 用途 |
|:-----------|:---------|:-----|
| デフォルト | Markdown マニュアル | Gemini同期作業 |
| `--jules` | GitHub Issue形式 | Jules夜間バッチ |

### 各ファイル変更の記述形式

```markdown
### ファイル: [パス]
### 変更1: [変更内容]
**位置**: [行番号]  **操作**: [追加/更新/削除]
**追加コンテンツ（完全コピー）**: [コピペ可能なコンテンツ]
**変更後の完全形**: [変更後の全体像]
**禁止事項**: [具体的な禁止事項]
```

### Output Format

**[S2 Mekhanē: Manual]**

| フィールド | 内容 |
|:-----------|:-----|
| 入力 | {設計ドキュメントパス} |
| 生成 | docs/update_manual_{name}.md |
| 影響 | {N}ファイル |
| 対象 | Gemini / Jules |

---

## Reminder

- visual: プロンプト構造テンプレートに従い、具体性を最大化する
- manual: 補完の余地がない粒度で記述する

*Output Modes v2.0 — Functional Beauty Redesign*
