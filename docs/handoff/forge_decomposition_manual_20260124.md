# Forge 解体・Hegemonikón 統合 - 実行指示書 v2

> **宛先**: Gemini (Antigravity IDE)
> **作成者**: Claude Opus (2026-01-24)
> **目的**: forge/ を解体し、Hegemonikón の機構体系に統合する
> **バージョン**: v2 (/manual 粒度ルール準拠)

---

## ⚠️ /manual 粒度ルール

以下のルールを厳守すること：

| # | ルール | 説明 |
|---|--------|------|
| 1 | 行番号を指定 | 「表を更新」ではなく「58行目〜64行目の表を更新」 |
| 2 | 完全コピー可能 | コピペで即適用できる内容を提供 |
| 3 | before/after 明示 | 変更前と変更後を明示 |
| 4 | 禁止事項を明記 | しないことを明確化 |

---

## 📋 実行フェーズ（7段階）

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
# ファイル存在確認
Test-Path "mekhane/ergasterion/prompt-lang/prompt_lang.py"
# Python 実行確認
python mekhane/ergasterion/prompt-lang/prompt_lang.py --help
```

**禁止事項**:
- ファイル名を変更しない
- ディレクトリ構造を「改善」しない

---

### Phase 2: モジュール分解・統合

**マッピング表**:

| 元ファイル | 移行先 | 追加セクション |
|-----------|--------|---------------|
| `forge/modules/find/📥情報を集める.md` | `.agent/skills/t-series/m5-peira/SKILL.md` | 「情報収集テンプレート」 |
| `forge/modules/find/👂 声を聞く.md` | `.agent/skills/t-series/m5-peira/SKILL.md` | 「ヒアリングテンプレート」 |
| `forge/modules/find/🗺️ 全体を眺める.md` | `.agent/skills/t-series/m3-theoria/SKILL.md` | 「俯瞰分析テンプレート」 |
| `forge/modules/find/🔄 頭を切り替える.md` | `.agent/skills/t-series/m3-theoria/SKILL.md` | 「視点転換テンプレート」 |
| `forge/modules/find/🤯 脳内を吐き出す.md` | `.agent/skills/t-series/m5-peira/SKILL.md` | 「ブレインダンプテンプレート」 |
| `forge/modules/reflect/✨ 品質を確かめる.md` | `.agent/skills/t-series/m7-dokime/SKILL.md` | 「QA テンプレート」 |
| `forge/modules/reflect/🏛️ 賢人に聞く.md` | `.agent/skills/t-series/m7-dokime/SKILL.md` | 「Synedrion テンプレート」 |
| `forge/modules/reflect/💾 記録する.md` | `.agent/skills/t-series/m8-anamnesis/SKILL.md` | 「記録テンプレート」 |
| `forge/modules/reflect/📖 経験を振り返る.md` | `.agent/skills/t-series/m3-theoria/SKILL.md` | 「振り返りテンプレート」 |
| `forge/modules/reflect/🔧 改善案を出す.md` | `.agent/skills/t-series/m7-dokime/SKILL.md` | 「改善提案テンプレート」 |
| `forge/modules/act/⚡ 働きかける.md` (交渉) | `.agent/skills/t-series/m6-praxis/SKILL.md` | 「交渉テンプレート」 |
| `forge/modules/act/⚡ 動く.md` | `.agent/skills/t-series/m6-praxis/SKILL.md` | 「実行テンプレート」 |

**作業手順（各ファイルごと）**:

1. 元ファイルを `view_file` で読む
2. `System Request` セクションの本質を抽出
3. `Output Format` セクションを 1:3 ピラミッド形式に変換
4. 対象 SKILL.md の末尾に追加

**追加形式（テンプレート）**:

```markdown
---

## 旧 forge/modules より移行

### [モジュール名] テンプレート

> **元ファイル**: `forge/modules/[category]/[filename].md`
> **用途**: [System Request から抽出した目的]

**入力形式**:
```xml
[User Input Template から抜粋]
```

**出力形式**:
[Output Format から抜粋]

**1:3 ピラミッド（適用例）**:
- [用途1]
- [用途2]
- [用途3]
```

**禁止事項**:
- 既存の SKILL.md 内容を変更しない
- 統合時に「改善」や「要約」をしない
- 元ファイルの Input/Output 形式を勝手に変更しない

---

### Phase 3: プリセット分解・統合

**マッピング表**:

| 元ファイル | 移行先 | 追加セクション |
|-----------|--------|---------------|
| `forge/presets/analyst.txt` | `.agent/skills/t-series/m2-krisis/SKILL.md` | 「Analyst ペルソナ」 |
| `forge/presets/architect.txt` | `.agent/skills/t-series/m4-phronesis/SKILL.md` | 「Architect ペルソナ」 |
| `forge/presets/brainstorm.txt` | `.agent/skills/t-series/m5-peira/SKILL.md` | 「Brainstorm ペルソナ」 |
| `forge/presets/coder.txt` | `.agent/skills/t-series/m6-praxis/SKILL.md` | 「Coder ペルソナ」 |
| `forge/presets/decision.txt` | `.agent/skills/t-series/m2-krisis/SKILL.md` | 「Decision ペルソナ」 |
| `forge/presets/writer.txt` | `.agent/skills/t-series/m6-praxis/SKILL.md` | 「Writer ペルソナ」 |

**追加形式（テンプレート）**:

```markdown
---

## 旧 forge/presets より移行

### [Preset Name] ペルソナ

> **元ファイル**: `forge/presets/[filename].txt`
> **用途**: Google AI Studio System Instructions として使用

**System Prompt**:
```xml
[presets ファイルの内容をそのままコピー]
```
```

**禁止事項**:
- presets の内容を「要約」しない（全文コピー）
- XML タグを変更しない

---

### Phase 4: プロファイル統合

**コマンド（順序厳守）**:
```powershell
# Step 1: ディレクトリ作成
New-Item -ItemType Directory -Path ".agent/rules/profiles" -Force

# Step 2: ファイル移動
Move-Item "forge/prompts/claude-profile.md" ".agent/rules/profiles/claude.md"
Move-Item "forge/prompts/perplexity-profile.md" ".agent/rules/profiles/perplexity.md"
Move-Item "forge/prompts/SETUP.md" ".agent/rules/profiles/SETUP.md"
```

**禁止事項**:
- ファイル内容を変更しない
- ファイル名以外を変更しない

---

### Phase 5: 知識ベース統合

**コマンド（順序厳守）**:
```powershell
# Step 1: 移行先ディレクトリ確認
Test-Path "mekhane/anamnesis"

# Step 2: knowledge_base 移動
New-Item -ItemType Directory -Path "mekhane/anamnesis/knowledge" -Force
Move-Item "forge/knowledge_base/*" "mekhane/anamnesis/knowledge/" -Force

# Step 3: Refined データ移動（存在する場合）
if (Test-Path "forge/Refined") {
    Move-Item "forge/Refined/*" "mekhane/anamnesis/refined/" -Force
}
```

**禁止事項**:
- 既存の mekhane/anamnesis 内容を上書きしない

---

### Phase 6: ドキュメントアーカイブ

**コマンド（順序厳守）**:
```powershell
# Step 1: アーカイブディレクトリ作成
New-Item -ItemType Directory -Path "docs/archive/forge" -Force

# Step 2: ドキュメント移動
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
# Step 1: 残りのファイルを確認
Get-ChildItem "forge/" -Recurse | Select-Object FullName

# Step 2: .gemini, .gitignore, tests 等は削除
Remove-Item "forge/.gemini" -Recurse -Force
Remove-Item "forge/.gitignore" -Force
Remove-Item "forge/tests" -Recurse -Force
Remove-Item "forge/models" -Recurse -Force

# Step 3: index.json, package.json 等は削除
Remove-Item "forge/index.json" -Force
Remove-Item "forge/package.json" -Force
Remove-Item "forge/package-lock.json" -Force
Remove-Item "forge/.forge-index.json" -Force
Remove-Item "forge/test_output.md" -Force

# Step 4: 空ディレクトリ削除
Remove-Item "forge/modules" -Recurse -Force
Remove-Item "forge/presets" -Recurse -Force
Remove-Item "forge/prompts" -Recurse -Force

# Step 5: forge ディレクトリ削除
Remove-Item "forge" -Recurse -Force
```

**Git コミット**:
```powershell
git add -A
git commit -m "refactor: decompose forge into Hegemonikón structure

Phase 1: Moved prompt-lang to mekhane/ergasterion/
Phase 2: Integrated 12 modules into T-series skills
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

### Phase 2
- [ ] 各 SKILL.md に「旧 forge/modules より移行」セクションが追加された
- [ ] 12 モジュールが統合された

### Phase 3
- [ ] 各 SKILL.md に「旧 forge/presets より移行」セクションが追加された
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

Phase 2-3 で「統合」の判断に迷った場合は作業を停止し、Creator に確認すること。

---

*作成: Claude Opus | 2026-01-24 | v2*
