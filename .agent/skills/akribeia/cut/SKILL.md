---
description: ゼロベース削減。「何を残すか」ではなく「何が不可欠か」を問う。冗長性検出・シンプル化・本質抽出時に発動。
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "判断基準の誤適用による過信・過少評価"
fallbacks: []
---
# Cut Skill (Q-3 消化)

> **Origin**: Q-3 オッカムのカミソリ (Radical Essentialism Engine)
> **責務**: ゼロベース削減 — 「何を残すか」ではなく「何が不可欠か」

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/a` 内で冗長性検出時 | 自動発動 |
| 「削減したい」「シンプルにしたい」 | 自然言語トリガー |
| 「本質は？」「何が不可欠？」 | 自然言語トリガー |

## Process

```yaml
Step 1: The Singularity (唯一の存在意義)
  → このプロジェクト/機能の「たった一つのゴール」を定義
  → これ以外はノイズ

Step 2: Zero-Based Selection (ゼロベース選択)
  Triage Protocol:
    - Criticality: それが無いと物理的・論理的に達成不可能か？
    - Uniqueness: 代替可能な簡易手段が存在しないか？
  → 両方 Yes のみ KEEP、それ以外は PURGE

Step 3: Vital Check (術後検証)
  → 削減後の構成でシミュレーション
  → 機能不全が起きないか検証
```

## Output Format

```markdown
## 🎯 The Singularity
[このプロジェクトの唯一の存在意義]

## ✂️ Kill List
| Element | Action | Rationale |
|:--------|:-------|:----------|
| [Name] | PURGE | [維持コストのみ、価値なし] |
| [Name] | KEEP | [不可欠、これがないと機能停止] |
| [Name] | MERGE | [X と統合可能] |

## 💎 Essential Form (MVP)
[生存に必要な最小構成のみ]
```

## 連携

- `/a` から自動呼び出し（冗長性検出時）
- `/plan` Step 2 で推奨
