---
doc_id: "WORKSPACE_RESTRUCTURE"
version: "2.0.0"
tier: "PLANNING"
status: "APPROVED_A"
---

# Hegemonikón ワークスペース再構成計画

> **決定事項**: Option A採用 + Forge従属モデル

---

## 1. アーキテクチャ: Hegemonikón > Forge

```
Hegemonikón (認知フレームワーク)
├── Forge (プロンプトエンジニアリング・プラットフォーム)
├── Skills (M-Series認知モジュール)
└── [将来: 他のサブプロジェクト]
```

**原則**: ForgeはHegemonikónの**一部**であり、独立プロジェクトではない。

---

## 2. 新ディレクトリ構造

```
C:\Users\raikh\Hegemonikon\           ← メインリポジトリ
├── .git/
├── README.md
├── GEMINI.md                         ← Option依存
│
├── kernel/                           ← 核心層
│   ├── doctrine.md                   ← Kernel Doctrine (現GEMINI.md)
│   └── axioms/                       ← 公理定義
│
├── skills/                           ← M-Series Skills
│   ├── m1-aisthesis/
│   ├── m2-krisis/
│   ... (M3-M8)
│
├── forge/                            ← Forge従属プロジェクト
│   ├── library/
│   ├── scripts/
│   └── ...
│
├── docs/                             ← 設計ドキュメント
│   ├── design/
│   └── audit/
│
└── .agent/                           ← Antigravity連携用
    ├── rules/
    └── workflows/
```

---

## 3. GEMINI.md 配置オプション

| Option | 配置場所 | 特徴 |
|--------|----------|------|
| **K1** | `~/Hegemonikon/kernel/doctrine.md` | ✅ 最も論理的。Kernel層として明示 |
| **K2** | `~/Hegemonikon/GEMINI.md` (ルート) | ✅ 発見しやすい。従来互換性高い |
| **K3** | `~/.gemini/GEMINI.md` (現状維持) + シンボリックリンク | ⚠️ Antigravity依存を残す |

### 比較表

| 観点 | K1 (kernel/) | K2 (ルート) | K3 (現状維持) |
|------|--------------|-------------|---------------|
| **論理的整合性** | ✅✅ 完璧 | ✅ 良好 | ⚠️ 不整合 |
| **発見性** | ⚠️ 深い | ✅✅ 即座に発見 | ✅ 既知の場所 |
| **Antigravity連携** | 要設定 | 要設定 | ✅ 変更不要 |
| **移行コスト** | 中 | 低 | なし |

### 推奨: K2 (ルート配置)

```
~/Hegemonikon/GEMINI.md
```

**理由**:
- リポジトリルートに配置 = 最初に目に入る
- `kernel/`は内部詳細として保持可能
- Antigravity側で読込パスを変更すれば連携可能

---

## 4. Antigravity連携

`.gemini`への連携方法:

```
C:\Users\raikh\.gemini\
├── GEMINI.md          ← シンボリックリンク → ~/Hegemonikon/GEMINI.md
└── .agent/
    └── skills/        ← シンボリックリンク → ~/Hegemonikon/skills/
```

または、`user_settings`で読込パスを設定（if supported）。

---

## 5. 実装手順

### Phase 1: リポジトリ作成
```powershell
mkdir C:\Users\raikh\Hegemonikon
cd C:\Users\raikh\Hegemonikon
git init
```

### Phase 2: 構造作成
```
mkdir kernel, skills, forge, docs, docs\design, docs\audit, .agent, .agent\rules, .agent\workflows
```

### Phase 3: ファイル移動
1. `.gemini/.agent/skills/m*` → `Hegemonikon/skills/`
2. `.gemini/GEMINI.md` → `Hegemonikon/GEMINI.md`
3. `~/Forge/*` → `Hegemonikon/forge/`
4. 設計ドキュメント → `Hegemonikon/docs/`

### Phase 4: シンボリックリンク作成
```powershell
# 管理者権限PowerShell
New-Item -ItemType SymbolicLink -Path "$HOME\.gemini\GEMINI.md" -Target "$HOME\Hegemonikon\GEMINI.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.gemini\.agent\skills" -Target "$HOME\Hegemonikon\skills"
```

### Phase 5: 検証
1. Antigravityでスキル読み込み確認
2. GEMINI.md読み込み確認

---

## 6. 新設計原則: 論理的美の追求

> **"Form follows logic. Logic follows beauty."**

| 原則 | 意味 |
|------|------|
| **Structural Elegance** | 構造が論理を反映し、論理が美しさを生む |
| **Semantic Hierarchy** | 命名と配置が意味階層を正確に表現 |
| **Zero Entropy** | 曖昧さの排除 = 構造の純粋化 |

この原則により、K1 (`kernel/doctrine.md`) を選択:
- `kernel/` = 核心層であることを構造で表現
- `doctrine.md` = 教義・憲法であることを命名で表現
- 階層が意味を持つ = **自己文書化する構造**

---

## 7. 決定事項

> [!IMPORTANT]
> **✅ 承認済み**: Option A (専用リポジトリ)
> **✅ 承認済み**: Forge従属モデル
> **✅ 承認済み**: K1 (`kernel/doctrine.md`) - 論理的美の追求
> **✅ 新原則**: "Pursuit of Logical Beauty" を哲学として組み込み

---

## 8. 最終ディレクトリ構造

```
C:\Users\raikh\Hegemonikon\
├── .git/
├── README.md
│
├── kernel/                           ← 核心層 (Kernel)
│   ├── doctrine.md                   ← Kernel Doctrine (旧GEMINI.md)
│   ├── axioms/                       ← 公理定義
│   │   ├── core-axioms.md           ← Flow, Value
│   │   └── choice-axioms.md         ← Tempo, Stratum, Agency, Valence
│   └── philosophy/                   ← 設計哲学
│       └── aesthetic-principles.md   ← 論理的美の追求
│
├── skills/                           ← M-Series Skills
│   ├── m1-aisthesis/
│   ├── m2-krisis/
│   ├── m3-theoria/
│   ├── m4-phronesis/
│   ├── m5-peira/
│   ├── m6-praxis/
│   ├── m7-dokime/
│   └── m8-anamnesis/
│
├── forge/                            ← Forge従属プロジェクト
│   ├── library/
│   ├── scripts/
│   └── ...
│
├── docs/                             ← 設計ドキュメント
│   ├── design/
│   └── audit/
│
└── .agent/                           ← Antigravity連携用
    ├── rules/
    └── workflows/
```

---

## 9. 次のステップ

1. **リポジトリ作成・初期化**
2. **ディレクトリ構造作成**
3. **ファイル移動**: Skills, Doctrine, Forge
4. **シンボリックリンク設定**
5. **検証**

