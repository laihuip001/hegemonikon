# Walkthrough: ワークフロー階層命名規則と A2 Krisis 統合

## 完了した作業

### 1. ワークフロー階層命名規則の確定

| 層 | 文字数 | ワークフロー |
|:---|:-------|:-------------|
| **Ω** | 1-2 | `/o`, `/s`, `/h`, `/p`, `/k`, `/a`, `/x`, `/ax` |
| **Δ** | 3 | `/noe`, `/dia`, `/chk`, `/bou`, `/ene`, `/zet` |
| **τ** | 3-4 | `/bye`, `/now`, `/dev`, `/exp`, `/rev`, `/src`, `/pri`, `/rec`, `/why`, `/vet`, `/sop`, `/boot`, `/plan`, `/hist` |
| **特殊** | 1 | `/u` |

### 2. リネーム実行

| 旧 | 新 | 理由 |
|:---|:---|:-----|
| `/audit` | `/dia` | Δ層は3文字ギリシャ語 |
| `/manual` | `/sop` | `/vet` とペアで動作、3文字統一 |

### 3. A2 Krisis 共通基盤の統合

各ワークフローのフロントマターに `skill_ref` と `pair` を追加:

```yaml
# /vet
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
pair: "/sop"

# /sop  
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
pair: "/vet"

# /dia
skill_ref:
  - ".agent/skills/ousia/o1-noesis/SKILL.md"
  - ".agent/skills/akribeia/a2-krisis/SKILL.md"
```

### 4. 文書化

命名規則を [hegemonikon.md](file:///home/makaron8426/oikos/.agent/rules/hegemonikon.md) のセクション6に追加。

## 設計決定

| 決定 | 理由 | 却下案 |
|:-----|:-----|:-------|
| τ層を3-4文字に | 直感的命名を優先 | 4文字強制 (不自然) |
| `/sop` (SOP) | `/vet` とのペアで意味が通じる | `/inst`, `/man` |
| `/dia` と `/vet` を統合しない | 責務が異なる (概念品質 vs 作業品質) | 統合 |

## コミット履歴

```
9934dd09 feat: ワークフローに skill_ref と pair を追加
a9e74cee rename: /manual → /sop (Standard Operating Procedure)
5a39cd9e revert: τ層ワークフローを3文字に戻す
ca15003a refactor: /audit → /dia (διάγνωσις) リネーム
```
