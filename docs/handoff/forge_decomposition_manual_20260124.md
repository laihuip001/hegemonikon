# Forge 解体・Hegemonikón 統合 - 実行指示書

> **宛先**: Gemini (Antigravity IDE)
> **作成者**: Claude Opus (2026-01-24)
> **目的**: forge/ を解体し、Hegemonikón の機構体系に統合する

---

## 🎯 ミッション

`forge/` ディレクトリを「単純移動」ではなく「内容分解→統合」する。
過去の遺産を Hegemonikón の美しい構造に溶け込ませる。

---

## ⚠️ 重要な注意

1. **削除は最後**: 必ず archive コピーを作成してから削除
2. **検証を挟む**: 各フェーズ完了後に動作確認
3. **判断に迷ったら停止**: 不明点があれば Creator に確認

---

## 📁 現在の構造

```
M:\Hegemonikon\
├── forge/              ← 解体対象
├── mekhane/            ← 統合先（T-series マクロ実装）
│   ├── anamnesis/      ← T8 記憶
│   ├── ergasterion/    ← T6 製造（ここに prompt-lang を追加）
│   ├── peira/          ← T5 探索
│   └── exagoge/        ← 出力
├── .agent/
│   ├── skills/t-series/ ← ここにモジュール統合
│   └── rules/           ← ここにプロファイル統合
└── docs/archive/        ← ここに残余をアーカイブ
```

---

## 📋 実行フェーズ

### Phase 1: prompt-lang 移行

**コマンド**:
```powershell
# 1. 移行先ディレクトリ作成
New-Item -ItemType Directory -Path "mekhane/ergasterion/prompt-lang" -Force

# 2. ファイル移動
Move-Item "forge/prompt-lang/*" "mekhane/ergasterion/prompt-lang/" -Force

# 3. 仕様書も移動
Move-Item "docs/specs/prompt-lang-v2-spec.md" "mekhane/ergasterion/prompt-lang/spec.md"
```

**検証**:
```powershell
python mekhane/ergasterion/prompt-lang/prompt_lang.py --help
```

---

### Phase 2: モジュール分解・統合

**作業**:
1. `forge/modules/act/` の各 .md を読む
2. 内容を `.agent/skills/t-series/m6-praxis/SKILL.md` の「1:3 ピラミッド」セクションに追加
3. 同様に:
   - `modules/find/` → `m5-peira/SKILL.md`
   - `modules/reflect/` → `m3-theoria/SKILL.md`, `m7-dokime/SKILL.md`
   - `modules/think/` → `m4-phronesis/SKILL.md`

**形式**:
```markdown
### 代表例（旧 forge/modules より）

> **[モジュール名]**
> - 用途1
> - 用途2
> - 用途3
```

---

### Phase 3: プリセット分解・統合

**マッピング**:
| ファイル | 統合先 SKILL.md |
|----------|----------------|
| analyst.txt | m3-theoria |
| architect.txt | m4-phronesis |
| brainstorm.txt | m5-peira |
| coder.txt | m6-praxis |
| decision.txt | m2-krisis |
| writer.txt | m6-praxis |

**作業**: 各 .txt の本質を抽出し、SKILL.md に「ペルソナ例」として追加

---

### Phase 4: プロファイル統合

**コマンド**:
```powershell
# プロファイルディレクトリ作成
New-Item -ItemType Directory -Path ".agent/rules/profiles" -Force

# 移動
Move-Item "forge/prompts/claude-profile.md" ".agent/rules/profiles/claude.md"
Move-Item "forge/prompts/perplexity-profile.md" ".agent/rules/profiles/perplexity.md"
```

---

### Phase 5: 知識ベース統合

**確認**: `mekhane/anamnesis/` に既に gnosis が存在するか確認
**作業**: `forge/knowledge_base/` の内容を `mekhane/anamnesis/knowledge/` に移動

```powershell
Move-Item "forge/knowledge_base/*" "mekhane/anamnesis/knowledge/" -Force
```

---

### Phase 6: ドキュメントアーカイブ

**コマンド**:
```powershell
# アーカイブディレクトリ作成
New-Item -ItemType Directory -Path "docs/archive/forge" -Force

# ドキュメント移動
Move-Item "forge/*.md" "docs/archive/forge/"
Move-Item "forge/README.md" "docs/archive/forge/"
```

---

### Phase 7: クリーンアップ

**コマンド**:
```powershell
# forge に残っているファイルを確認
Get-ChildItem "forge/" -Recurse

# 空になっていれば削除
Remove-Item "forge" -Recurse -Force
```

**Git コミット**:
```powershell
git add -A
git commit -m "refactor: decompose forge into Hegemonikón structure

- Phase 1: Moved prompt-lang to mekhane/ergasterion/
- Phase 2-3: Integrated modules/presets into T-series skills
- Phase 4: Moved profiles to .agent/rules/profiles/
- Phase 5: Integrated knowledge_base to mekhane/anamnesis/
- Phase 6: Archived remaining docs to docs/archive/forge/
- Phase 7: Removed empty forge/ directory"
```

---

## ✅ 完了チェックリスト

- [ ] Phase 1: prompt-lang が mekhane/ergasterion/ で動作する
- [ ] Phase 2: modules の内容が T-series SKILL.md に統合された
- [ ] Phase 3: presets の内容が T-series SKILL.md に統合された
- [ ] Phase 4: プロファイルが .agent/rules/profiles/ に存在する
- [ ] Phase 5: knowledge_base が mekhane/anamnesis/ に統合された
- [ ] Phase 6: ドキュメントが docs/archive/forge/ にアーカイブされた
- [ ] Phase 7: forge/ ディレクトリが存在しない
- [ ] Git commit 完了

---

## 🚨 緊急連絡

問題が発生した場合、作業を停止し Creator に報告すること。

---

*作成: Claude Opus | 2026-01-24*
