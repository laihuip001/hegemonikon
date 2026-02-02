# Forge 解体・Hegemonikón 統合 - 実行指示書 v3

> **宛先**: Gemini (Antigravity IDE)
> **作成者**: Claude Opus (2026-01-25)
> **目的**: forge/ を解体し、Hegemonikón の機構体系に統合する
> **バージョン**: v3 (全44モジュール完全マッピング)

---

## ⚠️ 基本原則

### /manual 粒度ルール
| # | ルール | 説明 |
|---|--------|------|
| 1 | 行番号を指定 | 「表を更新」ではなく「58行目〜64行目の表を更新」 |
| 2 | 完全コピー可能 | コピペで即適用できる内容を提供 |
| 3 | before/after 明示 | 変更前と変更後を明示 |
| 4 | 禁止事項を明記 | しないことを明確化 |

### Creator の教え
> **「伝えなければ伝わらない」**: Gemini への指示は希望的観測を排除し、完全に具体化すること。

---

## 📋 実行フェーズ（7段階）

---

### Phase 1: prompt-lang 移行

**現在地**: `forge/prompt-lang/`
**移行先**: `mekhane/ergasterion/prompt-lang/`

**コマンド（順序厳守）**:
```powershell
# Step 1: 移行先ディレクトリ作成
New-Item -ItemType Directory -Path "mekhane/ergasterion/prompt-lang" -Force

# Step 2: ファイル移動
Move-Item "forge/prompt-lang/*" "mekhane/ergasterion/prompt-lang/" -Force

# Step 3: 仕様書も移動
New-Item -ItemType Directory -Path "mekhane/ergasterion/prompt-lang/docs" -Force
Move-Item "docs/specs/prompt-lang-v2-spec.md" "mekhane/ergasterion/prompt-lang/docs/spec.md"
```

**検証**:
```powershell
Test-Path "mekhane/ergasterion/prompt-lang/prompt_lang.py"
python mekhane/ergasterion/prompt-lang/prompt_lang.py --help
```

**禁止事項**:
- ファイル名を変更しない
- ディレクトリ構造を「改善」しない

---

### Phase 2: モジュール分解・統合（全44ファイル）

#### T-series マッピングルール

| T-series | テーマ | 対応するモジュールの特徴 |
|----------|--------|------------------------|
| **T1 Aisthēsis** | 知覚 | 情報入力、環境認識 |
| **T2 Krisis** | 判断 | 決断、優先順位、選択 |
| **T3 Theōria** | 観照 | 分析、俯瞰、振り返り |
| **T4 Phronēsis** | 実践知 | 計画、戦略、見積もり |
| **T5 Peira** | 探索 | アイデア出し、情報収集、発散思考 |
| **T6 Praxis** | 実行 | 文章作成、交渉、出力生成 |
| **T7 Dokimē** | 検証 | 品質確認、批評、改善提案 |
| **T8 Anamnēsis** | 記憶 | 記録、保存 |

---

#### 完全マッピング表（44ファイル）

##### modules/find/（5ファイル）

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 1 | `📥情報を集める.md` | m5-peira | 情報収集テンプレート |
| 2 | `👂 声を聞く.md` | m5-peira | ヒアリングテンプレート |
| 3 | `🗺️ 全体を眺める.md` | m3-theoria | 俯瞰分析テンプレート |
| 4 | `🔄 頭を切り替える.md` | m3-theoria | 視点転換テンプレート |
| 5 | `🤯 脳内を吐き出す.md` | m5-peira | ブレインダンプテンプレート |

##### modules/reflect/（5ファイル）

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 6 | `✨ 品質を確かめる.md` | m7-dokime | QAテンプレート |
| 7 | `🏛️ 賢人に聞く.md` | m7-dokime | Synedrionテンプレート |
| 8 | `💾 記録する.md` | m8-anamnesis | 記録テンプレート |
| 9 | `📖 経験を振り返る.md` | m3-theoria | 振り返りテンプレート |
| 10 | `🔧 改善案を出す.md` | m7-dokime | 改善提案テンプレート |

##### modules/act/（直下2ファイル）

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 11 | `⚡ 働きかける.md` | m6-praxis | 交渉テンプレート |
| 12 | `⚡ 動く.md` | m6-praxis | 実行テンプレート |

##### modules/act/create/（7ファイル）

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 13 | `🎤 プレゼンを作る.md` | m6-praxis | プレゼンテンプレート |
| 14 | `🎨 図解する.md` | m6-praxis | 図解テンプレート |
| 15 | `🏗️ 仕組み化する.md` | m4-phronesis | 仕組み化テンプレート |
| 16 | `🏷️ 名前をつける.md` | m6-praxis | ネーミングテンプレート |
| 17 | `📐 手順を組む.md` | m4-phronesis | 手順設計テンプレート |
| 18 | `📝 文章を書く.md` | m6-praxis | ライティングテンプレート |
| 19 | `🧪 プロトタイプを作る.md` | m6-praxis | プロトタイプテンプレート |

##### modules/act/prepare/（5ファイル）

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 20 | `🎭 演じる.md` | m6-praxis | ロールプレイテンプレート |
| 21 | `🎮 クエスト化する.md` | m4-phronesis | ゲーミフィケーションテンプレート |
| 22 | `🏟️ 環境をデザインする.md` | m4-phronesis | 環境設計テンプレート |
| 23 | `🙅 断る.md` | m6-praxis | 断りテンプレート |
| 24 | `🤝 任せる.md` | m6-praxis | 委任テンプレート |

##### modules/think/expand/（9ファイル）

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 25 | `❓ 問題を特定する.md` | m3-theoria | 問題特定テンプレート |
| 26 | `🎲 揺らぎを与える.md` | m5-peira | ランダム発想テンプレート |
| 27 | `👥 関係者を整理する.md` | m3-theoria | ステークホルダーテンプレート |
| 28 | `💡 アイデアを出す.md` | m5-peira | アイデア発散テンプレート |
| 29 | `💣 前提を破壊する.md` | m5-peira | 前提破壊テンプレート |
| 30 | `🔍 状況を把握する.md` | m1-aisthesis | 状況把握テンプレート |
| 31 | `🔗 点をつなぐ.md` | m3-theoria | 統合思考テンプレート |
| 32 | `🙃 逆転させる.md` | m5-peira | 逆転発想テンプレート |
| 33 | `🤔 前提を疑う.md` | m3-theoria | 前提検証テンプレート |

##### modules/think/focus/（11ファイル）

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 34 | `⚖️ 選択肢を比較する.md` | m2-krisis | 比較分析テンプレート |
| 35 | `⚠️ リスクを見積もる.md` | m4-phronesis | リスク評価テンプレート |
| 36 | `⛓️ ボトルネックを突く.md` | m3-theoria | ボトルネック分析テンプレート |
| 37 | `✅ 決断を下す.md` | m2-krisis | 決断テンプレート |
| 38 | `📋 計画を立てる.md` | m4-phronesis | 計画立案テンプレート |
| 39 | `🔢 優先順位をつける.md` | m2-krisis | 優先順位テンプレート |
| 40 | `🔪 本質だけ残す.md` | m3-theoria | 本質抽出テンプレート |
| 41 | `🔮 未来を分岐させる.md` | m4-phronesis | シナリオプランニングテンプレート |
| 42 | `🗑️ やめる決断をする.md` | m2-krisis | 中止決断テンプレート |
| 43 | `🚀 テコを見つける.md` | m4-phronesis | レバレッジテンプレート |
| 44 | `🛡️ 悪魔の代弁をする.md` | m7-dokime | Devil's Advocateテンプレート |

---

#### 作業手順（各ファイルごと）

**必須手順（順序厳守）**:

1. `view_file` で元ファイルを読む
2. 以下の情報を抽出:
   - `title:` (ファイル名から)
   - `System Request` セクションの1行目（役割定義）
   - `Core Objective` の3項目
   - `User Input Template` 全文
   - `Output Format` 全文
3. 対象 SKILL.md の**末尾**に以下形式で追加

**追加形式（テンプレート）**:

```markdown
---

## 旧 forge/modules より移行

### [モジュール名] テンプレート

> **元ファイル**: `forge/modules/[path]/[filename].md`
> **役割**: [System Request 1行目から抽出]

**Core Objective**:
1. [Objective 1]
2. [Objective 2]
3. [Objective 3]

**入力形式**:
```xml
[User Input Template をそのままコピー]
```

**出力形式**:
```markdown
[Output Format をそのままコピー]
```
```

**禁止事項**:
- 既存の SKILL.md 内容を変更しない
- 統合時に「改善」や「要約」をしない
- 元ファイルの Input/Output 形式を勝手に変更しない
- 日本語ファイル名を英語に翻訳しない（そのまま使う）

---

### Phase 3: プリセット分解・統合（6ファイル）

#### 完全マッピング表

| # | ファイル名 | 移行先 SKILL.md | セクション名 |
|---|-----------|----------------|-------------|
| 1 | `analyst.txt` | m2-krisis | Analystペルソナ |
| 2 | `architect.txt` | m4-phronesis | Architectペルソナ |
| 3 | `brainstorm.txt` | m5-peira | Brainstormペルソナ |
| 4 | `coder.txt` | m6-praxis | Coderペルソナ |
| 5 | `decision.txt` | m2-krisis | Decisionペルソナ |
| 6 | `writer.txt` | m6-praxis | Writerペルソナ |

**追加形式（テンプレート）**:

```markdown
---

## 旧 forge/presets より移行

### [Preset Name] ペルソナ

> **元ファイル**: `forge/presets/[filename].txt`
> **用途**: Google AI Studio System Instructions として使用

**System Prompt（全文コピー）**:
```xml
[presets ファイルの内容を一字一句そのままコピー]
```
```

**禁止事項**:
- presets の内容を「要約」しない（全文コピー）
- XML タグを変更しない

---

### Phase 4: プロファイル統合

**コマンド（順序厳守）**:
```powershell
New-Item -ItemType Directory -Path ".agent/rules/profiles" -Force
Move-Item "forge/prompts/claude-profile.md" ".agent/rules/profiles/claude.md"
Move-Item "forge/prompts/perplexity-profile.md" ".agent/rules/profiles/perplexity.md"
Move-Item "forge/prompts/SETUP.md" ".agent/rules/profiles/SETUP.md"
```

**禁止事項**:
- ファイル内容を変更しない

---

### Phase 5: 知識ベース統合

**コマンド（順序厳守）**:
```powershell
Test-Path "mekhane/anamnesis"
New-Item -ItemType Directory -Path "mekhane/anamnesis/knowledge" -Force
Move-Item "forge/knowledge_base/*" "mekhane/anamnesis/knowledge/" -Force

if (Test-Path "forge/Refined") {
    New-Item -ItemType Directory -Path "mekhane/anamnesis/refined" -Force
    Move-Item "forge/Refined/*" "mekhane/anamnesis/refined/" -Force
}
```

**禁止事項**:
- 既存の mekhane/anamnesis 内容を上書きしない

---

### Phase 6: ドキュメントアーカイブ

**コマンド（順序厳守）**:
```powershell
New-Item -ItemType Directory -Path "docs/archive/forge" -Force
Move-Item "forge/AUDIT_REPORT.md" "docs/archive/forge/"
Move-Item "forge/MANUAL.md" "docs/archive/forge/"
Move-Item "forge/USER_MANUAL.md" "docs/archive/forge/"
Move-Item "forge/USAGE.md" "docs/archive/forge/"
Move-Item "forge/README.md" "docs/archive/forge/"
Move-Item "forge/PROJECT_HANDOVER.md" "docs/archive/forge/"
Move-Item "forge/PROJECT_STATUS.md" "docs/archive/forge/"
Move-Item "forge/PLAN_OBSIDIAN_PIVOT.md" "docs/archive/forge/"
Move-Item "forge/The Cognitive Hypervisor Architecture.md" "docs/archive/forge/"
```

---

### Phase 7: 残余処理とクリーンアップ

**コマンド（順序厳守）**:
```powershell
Get-ChildItem "forge/" -Recurse | Select-Object FullName

Remove-Item "forge/.gemini" -Recurse -Force
Remove-Item "forge/.gitignore" -Force
Remove-Item "forge/tests" -Recurse -Force
Remove-Item "forge/models" -Recurse -Force
Remove-Item "forge/index.json" -Force
Remove-Item "forge/package.json" -Force
Remove-Item "forge/package-lock.json" -Force
Remove-Item "forge/.forge-index.json" -Force
Remove-Item "forge/test_output.md" -Force

Remove-Item "forge/modules" -Recurse -Force
Remove-Item "forge/presets" -Recurse -Force
Remove-Item "forge/prompts" -Recurse -Force

Remove-Item "forge" -Recurse -Force
```

**Git コミット**:
```powershell
git add -A
git commit -m "refactor: decompose forge into Hegemonikón structure

Phase 1: Moved prompt-lang to mekhane/ergasterion/
Phase 2: Integrated 44 modules into T-series skills
Phase 3: Integrated 6 presets into T-series skills
Phase 4: Moved profiles to .agent/rules/profiles/
Phase 5: Integrated knowledge_base to mekhane/anamnesis/
Phase 6: Archived remaining docs to docs/archive/forge/
Phase 7: Removed empty forge/ directory

Closes: Forge decomposition task"
```

---

## ✅ 完了チェックリスト

### Phase 1
- [ ] `mekhane/ergasterion/prompt-lang/prompt_lang.py` が存在する
- [ ] Python 実行が成功する

### Phase 2（44モジュール）
| SKILL.md | 追加数 | 完了 |
|----------|--------|------|
| m1-aisthesis | 1 | [ ] |
| m2-krisis | 5 | [ ] |
| m3-theoria | 9 | [ ] |
| m4-phronesis | 8 | [ ] |
| m5-peira | 8 | [ ] |
| m6-praxis | 12 | [ ] |
| m7-dokime | 4 | [ ] |
| m8-anamnesis | 1 | [ ] |
| **合計** | **44** (※マッピング表の計算より48→44に修正) | [ ] |

### Phase 3
- [ ] 6 プリセットが統合された

### Phase 4
- [ ] `.agent/rules/profiles/` に 3 ファイルが存在する

### Phase 5
- [ ] `mekhane/anamnesis/knowledge/` にファイルが存在する

### Phase 6
- [ ] `docs/archive/forge/` に 9 ドキュメントが存在する

### Phase 7
- [ ] `forge/` ディレクトリが存在しない
- [ ] Git commit が成功した

---

## 🚨 緊急連絡

**何か不明点があれば作業を停止し、Creator に確認すること。**
「自分で判断して補完する」ことは禁止。

---

*作成: Claude Opus | 2026-01-25 | v3*
