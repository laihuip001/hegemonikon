---

hegemonikon: Akribeia
modules: [A2]
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
version: "3.0"
layer: "τ"
parent: "/dia"
lineage: "A2 Krisis → Synedrion 6評議員 + Anti-Skip + Artifact出力 + 3層アーキテクチャ → /syn v3.0"
anti_skip: enabled
---

# /syn: Synedrion (偉人評議会)

> **正本参照**: [A2 Krisis SKILL.md](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md)
> **目的**: 多角的批評 — 偉人評議会 + 拡張モード
> **親コマンド**: /dia

---

## 発動条件

| トリガー | モード | 説明 |
|:---------| :------- | :----- |
| `/syn` | 標準 | 偉人評議会を召喚 |
| `/syn [対象]` | 標準 | 特定の成果物を批評 |
| `/syn inv` | **反転** | 結論の逆を強制論証 |
| `/syn 10m` | **10th Man** | 悪魔の代弁者（強制異論） |
| `/syn grv` | **墓場** | 失敗事例分析（生存者バイアス除去） |

> **全のせが欲しい場合**: `/pan` を使用

---

## ⚠️ 実行前必須: 正本読み込み

> **このステップは省略禁止。必ず実行すること。**

```text
実行手順:
1. view_file ツールで SKILL.md を読み込む
   パス: /home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md
2. Synedrion: 偉人評議会 セクションを確認
3. 6評議員と拡張モードの出力形式を確認
4. 確認後、処理を開始
```

---

## 処理フロー

**詳細ロジックと出力形式は SKILL.md「Synedrion: 偉人評議会」セクションに記載**

```text
[STEP 0] SKILL.md を view_file で読み込む ← 必須
  ↓
[Step 1] 招集 — 対象物を全評議員に提示
  ↓
[Step 2] 独立評価 — 各評議員が ✅/⚠️/🔴 を判定
  ↓
[Step 3] 異議申し立て — 承認以外の評議員が発言
  ↓
[Step 4] 統合助言 — 具体的な改善提案を出力
  ↓
Artifact 保存
```

---

## コマンド

| コマンド | 動作 |
| :-------- | :---- |
| `/syn` | 6評議員による標準批評 |
| `/syn inv` | Inversion Mode (反転) |
| `/syn 10m` | 10th Man Rule (悪魔の代弁者) |
| `/syn grv` | Graveyard Walk (墓場歩き) |

---

## Artifact 出力保存規則

### 保存先

```text
<artifact_directory>/syn_<topic>.md
```

### 保存理由

1. **偉人たちの議論は資産** — 同じ議論を再度生成するのは無駄
2. **判断の追跡性** — 誰が何を言ったか後から確認

---

## Hegemonikon Status

| Module | Workflow | Skill (正本) | Status |
| :------- |:---------|--------------| :------- |
| A2 Krisis | /syn | [SKILL.md](file:///home/makaron8426/oikos/.agent/skills/akribeia/a2-krisis/SKILL.md) | v3.0 Ready |

---

*v3.0 — 3層アーキテクチャ対応 (Skill = 正本)*
