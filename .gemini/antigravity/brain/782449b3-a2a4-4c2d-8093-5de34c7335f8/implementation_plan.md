は# v2.1 定理体系 Full Rebuild 計画（最終版）

> **方針**: 24定理すべてを新公理から一気に再設計
> **X-series**: related + Mermaid + /ax 動的表示で可視化

---

## Phase 0: 復帰点作成

```bash
git add -A && git commit -m "pre-v2.1-rebuild: checkpoint"
```

---

## Phase 1: 旧パス参照確認

```bash
grep -r "t-series\|k-series\|o-series\|s-series" .agent/ --include="*.md" --include="*.yaml"
```

参照があれば Phase 5 で更新対象としてリスト化。

---

## Phase 2: アーカイブ作成

```bash
mkdir -p .agent/skills/_archive
mv .agent/skills/t-series .agent/skills/_archive/
mv .agent/skills/k-series .agent/skills/_archive/
mv .agent/skills/o-series .agent/skills/_archive/
mv .agent/skills/s-series .agent/skills/_archive/
```

---

## Phase 3: 24定理スキル作成

### ディレクトリ構造

```
.agent/skills/
├── ousia/           # O1-O4
│   ├── o1-noesis/SKILL.md
│   ├── o2-boulesis/SKILL.md
│   ├── o3-zetesis/SKILL.md
│   └── o4-energeia/SKILL.md
├── schema/          # S1-S4
├── horme/           # H1-H4
├── perigraphe/      # P1-P4
├── kairos/          # K1-K4
└── akribeia/        # A1-A4
```

### スキル構造テンプレート

```yaml
---
# Theorem Metadata (v2.1)
id: "{SERIES}{N}"
name: "{Greek Name}"
greek: "{Greek Characters}"
series: "{Series Name}"
generation:
  formula: "{公理1} × {公理2}"
  result: "{意味}"

description: >
  Use this skill when {発動条件}.
  Triggers: {keywords}.
  
triggers:
  - {条件1}
  - {条件2}

keywords:
  - {keyword1}
  - {keyword2}

related:
  upstream: ["{上流定理}"]
  downstream: ["{下流定理}"]
  x_series:
    - "X-{AB}{N} → {TargetTheorem}"

implementation:
  micro: "{workflow path}"
  macro: "{mekhane path}"
  templates: ["{旧Tから継承}"]

version: "2.1.0"
---

# {ID}: {Name} ({Greek})

> **生成**: {formula}
> **役割**: {role}

## When to Use
...

## Processing Logic
...

## X-series 接続

```mermaid
graph LR
    THIS[{ID} {Name}] -->|X-{AB}{N}| TARGET[{Target}]
```

## Integration

...

```

### 作成順序

| 順 | Series | 定理 | 優先度 | 旧継承 |
|----|--------|------|--------|--------|
| 1 | O | O1-O4 | 高 | T1,T2,T3,T5,T6 |
| 2 | S | S1-S4 | 高 | T4 |
| 3 | A | A1-A4 | 高 | T7, 旧K |
| 4 | H | H1-H4 | 中 | T8 |
| 5 | P | P1-P4 | 中 | — |
| 6 | K | K1-K4 | 中 | 旧K |

---

## Phase 4: /ax リファクタリング

### 変更内容

1. 旧 T/K 参照を新定理参照に更新
2. X-series 動的表示を追加

### 新 /ax 出力イメージ

```

══════════════════════════════════════════════════════
[Hegemonikón] /ax: 定理群統合分析
══════════════════════════════════════════════════════

📋 問い: {問い}

━━━ O-series (本質) ━━━
発動: O1 Noēsis
遷移: O1 →[X-OS1]→ S1 →[X-SH1]→ H1

━━━ S-series (様態) ━━━
...

━━━ X-series (接続マップ) ━━━
  O1 ──X-OS1──→ S1
  S1 ──X-SH1──→ H1
  S1 ──X-SP1──→ P1
══════════════════════════════════════════════════════

```

---

## Phase 5: 参照パス更新

Phase 1 で検出した参照を新パスに更新。

| 旧パス | 新パス |
|--------|--------|
| `t-series/t1-aisthesis` | `ousia/o1-noesis` |
| `t-series/t2-krisis` | `ousia/o2-boulesis` |
| `s-series/s2-mekhane` | `schema/s2-mekhane` |
| ... | ... |

---

## Phase 6: Footprint テスト

各定理スキルの発動を確認:

```markdown
## O1 Noēsis
Prompt: "この問題の本質は何か深く考えて"
Expected: O1 Noēsis 発動

## O4 Energeia
Prompt: "実行して"
Expected: O4 Energeia 発動
```

---

## チェックリスト

- [ ] Phase 0: Git コミット
- [ ] Phase 1: grep 確認
- [ ] Phase 2: _archive/ 作成
- [ ] Phase 3: 24定理スキル作成
  - [ ] O-series (4)
  - [ ] S-series (4)
  - [ ] H-series (4)
  - [ ] P-series (4)
  - [ ] K-series (4)
  - [ ] A-series (4)
- [ ] Phase 4: /ax リファクタリング
- [ ] Phase 5: 参照パス更新
- [ ] Phase 6: Footprint テスト
