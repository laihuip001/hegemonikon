# Skill-WF Mode 連携ガイド

## 概要

Hegemonikón の WF (ワークフロー) と Skill は双方向でリンクされています。

## 使い方

### WF から Skill を参照

```bash
# WF frontmatter の skill_ref を確認
head -20 .agent/workflows/gno.md | grep skill_ref
```

### Skill から WF を参照

```bash
# Skill の Related Modes セクションを確認
tail -30 .agent/skills/akribeia/a3-gnome/SKILL.md
```

## 同期検証

```bash
# 同期状態を確認
.agent/scripts/wf_skill_sync_check.sh
```

## 構造

```
WF.md
├── frontmatter.skill_ref → SKILL.md
├── frontmatter.derivatives: [mode1, mode2, ...]
└── ## --mode=X (各派生の実装)

SKILL.md
├── ## Related Modes
└── | mode | CCL | 用途 | (テーブル)
```

## 注意

- 振動WF (`/a`, `/h`, `/k`, `/o`, `/p`, `/s`) は derivatives を持つが、実装は各子WFに委譲
- 新しい mode 追加時は WF と Skill 両方を更新
