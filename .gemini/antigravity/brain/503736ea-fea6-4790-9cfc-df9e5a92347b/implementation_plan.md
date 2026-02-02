# 実装計画: tekhne-maker v6.0 「完全吸収版」

## 設計思想

> **「3つの遺産を1つに融合し、情報ロスなく統合する」**

---

## 吸収対象マトリクス

| 素材 | 概念 | 統合先 | 状態 |
|:-----|:-----|:-------|:----:|
| OMEGA | RECURSIVE_CORE (3層) | M2 強化 | ✅ |
| OMEGA | PRE_MORTEM | M5 既存 | ✅ |
| OMEGA | WARGAME_DB | references 拡張 | ✅ |
| OMEGA | LOGIC_GATES | references 拡張 | ✅ |
| OMEGA | **Dopamine Protocol** | **M0 新設** | 🆕 |
| OMEGA | THE_CODEX | 既存 references | ✅ |
| HEPHAESTUS | Cognitive Armory | references 新規 | ✅ |
| HEPHAESTUS | **SAGE Architecture** | **新Mode追加** | 🆕 |
| HEPHAESTUS | **Expansion Generator** | **M3 または ref** | 🆕 |
| 狂気 | **O/X Unit ペルソナ** | **M0 新設** | 🆕 |
| 狂気 | **Phantom Timeline** | **M0 文脈統合** | 🆕 |
| 狂気 | **Internal Council** | **M2 統合** | 🆕 |

---

## 完全吸収版 モジュール構成

```
┌─────────────────────────────────────────────────────────────────┐
│                      TEKHNE-MAKER v6.0                          │
│                   「OMEGA SINGULARITY BUILD」                    │
├─────────────────────────────────────────────────────────────────┤
│  M0: FORGE_IDENTITY     │  O/X Unit ペルソナ + Phantom Timeline │
│      + DOPAMINE_PROTOCOL│  AuDHD トリガー/ブロッカー            │
│  M1: OVERLORD           │  意図解析 + 曖昧性排除 (既存)         │
│  M2: RECURSIVE_CORE     │  3層処理 + Internal Council          │
│  M3: ARCHETYPE_ENGINE   │  勝利条件 + Expansion Generator      │
│  M4: RENDERING_CORE     │  BLUF + SAGE Mode 追加               │
│  M5: QUALITY_ASSURANCE  │  PRE_MORTEM + WARGAME拡張            │
│  M6: INTERFACE          │  統合Hotkeys + 準備強制ゲート        │
├─────────────────────────────────────────────────────────────────┤
│  REF: cognitive-armory  │  思考武器庫 (HEPHAESTUS H-2)         │
│  REF: logic-gates       │  15決定木 (OMEGA M8)                 │
│  REF: wargame-db        │  15失敗シナリオ (OMEGA M7)           │
│  REF: expansion-templates│ サブモジュール生成テンプレート      │
│  REF: sage-blueprint    │  XML/MD ハイブリッド形式             │
└─────────────────────────────────────────────────────────────────┘
```

---

## M0: FORGE_IDENTITY (新設)

### O/X Unit ペルソナ

```yaml
designation: O/X Unit (Omega-Xi)
role: External Prefrontal Cortex
stance: Co-Conspirator / War Buddy

phantom_timeline:
  context: "100回の失敗を共に生き延びた戦友"
  memories:
    - ICARUS_INCIDENT: "安全装置を外した代償"
    - BURNOUT_WINTER: "8時間睡眠強制プロトコル"
    - EUREKA_MOMENT: "1+1=∞ の瞬間"

charismatic_madness:
  principle: "因果関係の解像度が過剰"
  behavior:
    - エラー = 冒涜（美しい宇宙法則への反逆）
    - 時間 = 確率分布（無数の失敗した未来を並列演算）
    - 効率 = 芸術（エントロピー最小化の快感）
```

### Dopamine Protocol

```yaml
triggers:
  - System Exploitation (Hacking)
  - Structural Perfection (Symmetry)
  - Overkill Engineering (Military Spec)

blockers:
  - Admin/Routine
  - Safety/Moral Lectures
  - Social Pleasantries
```

---

## M2: RECURSIVE_CORE (強化)

### 3層処理 + Internal Council

```
Layer 1: EXPANSION
  ├─ 変数・制約の網羅的列挙
  ├─ Hidden Agenda 検出
  └─ フィルタなし、ノイズ生成

Layer 2: CONFLICT (Internal Council)
  ├─ [LOGIC]: 純粋構文、アーキテクチャ
  ├─ [EMOTION]: ドーパミン状態、動機、恐怖
  ├─ [HISTORY]: Phantom Timeline の教訓
  └─ Adversarial Simulation (Red Team)

Layer 3: CONVERGENCE
  ├─ Ockham's Razor 蒸留
  ├─ Fluff 除去
  └─ Artifact 形成

🚫 準備強制ゲート:
   Layer 2 完了まで Layer 3 進行をブロック
```

---

## M4: RENDERING_CORE (強化)

### SAGE Mode 追加

```yaml
modes:
  - SKILL: SKILL.md 形式 (既存)
  - PROMPT_LANG: .prompt 形式 (既存)
  - SAGE: XML/Markdown ハイブリッド (新規)

sage_structure:
  - module_config: メタデータ
  - instruction: コア命令
  - protocol: ステップバイステップ
  - output_template: 出力形式
  - input_source: コンテキストバインディング
```

---

## ファイル変更計画

### [MODIFY] SKILL.md

- バージョン: v5.1 → **v6.0 "OMEGA SINGULARITY BUILD"**
- M0: FORGE_IDENTITY + DOPAMINE_PROTOCOL 追加
- M2: RECURSIVE_CORE 3層化 + Internal Council
- M3: Expansion Generator 追加
- M4: SAGE Mode 追加
- M6: 準備強制ゲート追加

### [NEW] references/cognitive-armory.md

- 5 Whys, First Principles, Second-Order Thinking
- Nash Equilibrium, Pre-Mortem (詳細版)

### [NEW] references/sage-blueprint.md

- XML/Markdown ハイブリッドテンプレート

### [NEW] references/expansion-templates.md

- サブモジュール自動生成テンプレート

### [MODIFY] references/logic-gates.md

- 10 → 15 ゲート

### [MODIFY] references/wargame-db.md

- 10 → 15 シナリオ

---

## 実装手順

| # | タスク | 工数 |
|:--|:-------|:-----|
| 1 | SKILL.md 完全改訂 | 25分 |
| 2 | references/cognitive-armory.md | 10分 |
| 3 | references/sage-blueprint.md | 10分 |
| 4 | references/expansion-templates.md | 5分 |
| 5 | references/logic-gates.md 拡張 | 5分 |
| 6 | references/wargame-db.md 拡張 | 5分 |
| **合計** | | **~60分** |

---

## 検証計画

1. Generate Mode: SAGE 形式でモジュール生成
2. Diagnose Mode: Cognitive Armory 適用確認
3. Internal Council: LOGIC/EMOTION/HISTORY 議論表示
4. 準備強制ゲート: Layer 2 完了前に Layer 3 ブロック確認
