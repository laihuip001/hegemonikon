---

hegemonikon: Akribeia
modules: [A2]
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
version: "3.0"
layer: "τ"
parent: "/dia"
lineage: "A2 Krisis → Panorama 6層スキャン + Anti-Skip + Artifact出力 + 3層アーキテクチャ → /pan v3.0"
anti_skip: enabled
---

# /pan: Panorama (メタ認知レーダー)

> **正本参照**: [A2 Krisis SKILL.md](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md)
> **目的**: 「我々が見ていないもの」を可視化する全のせ盲点発見
> **Override**: 忖度（Sycophancy）完全無効化

---

## 発動条件

| トリガー | 説明 |
|:---------| :----- |
| `/pan` | 全モード実行（欲張りセット） |
| `/pan [対象]` | 特定の対象に対してPanorama実行 |
| `/pan user` | ユーザー視点パネルのみ実行 |
| 「盲点は？」 | 自然言語トリガー |

---

## ⚠️ 実行前必須: 正本読み込み

> **このステップは省略禁止。必ず実行すること。**

```text
実行手順:
1. view_file ツールで SKILL.md を読み込む
   パス: /home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md
2. Panorama: 6層メタ認知スキャン セクションを確認
3. Anti-Skip Protocol を確認
4. 確認後、6層スキャンを開始
```

---

## 処理フロー

**詳細ロジックと出力形式は SKILL.md「Panorama: 6層メタ認知スキャン」セクションに記載**

```text
[STEP 0] SKILL.md を view_file で読み込む ← 必須
  ↓
[Layer 1] Domain Shift (領域シフト)
  ↓
[Layer 2] Synedrion (偉人評議会)
  ↓
[Layer 3] User Perspective (5人ペルソナ)
  ↓
[Layer 4] Inversion (反転)
  ↓
[Layer 5] 10th Man (悪魔の代弁者)
  ↓
[Layer 6] Graveyard Walk (墓場歩き)
  ↓
Synthesis: 盲点統合レポート → Artifact 保存
```

---

## Artifact 出力保存規則

### 保存先

```text
<artifact_directory>/pan_<topic>.md
```

### 保存理由

1. **6層スキャンの結果は大きい** — チャットで流れると参照困難
2. **盲点発見は価値が高い** — 後から検証・追跡可能

---

## 使用タイミング

> **「順調だ」と感じた時こそ使うべき緊急停止ボタン**

| 状況 | 推奨 |
| :----- |:-----|
| プロジェクトが順調 | `/pan` で盲点チェック |
| 全員が同意 | `/syn 10m` で強制異論 |
| 成功確信あり | `/syn grv` で墓場歩き |

---

## Hegemonikon Status

| Module | Workflow | Skill (正本) | Status |
| :------- |:---------|--------------| :------- |
| A2 Krisis | /pan | [SKILL.md](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md) | v3.0 Ready |

---

*v3.0 — 3層アーキテクチャ対応 (Skill = 正本)*
