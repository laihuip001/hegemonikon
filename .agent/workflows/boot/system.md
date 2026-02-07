---
description: Phase 4 — システム更新。プロファイル, ツール, Gnōsis, 白血球。
parent: /boot
---

# システム更新 (System Update)

> 認知態勢(Hexis)の確立とツール状態の確認。
>
> **制約**: CCL パターン `*^` の意味を正確に把握すること(融合のメタ表示)。

---

## 4.1 プロファイル読込

`GEMINI.md` を確認し、Hegemonikón Doctrine が有効であることを確認。

---

## 4.2 コアモジュール有効化

| Skill | 用途 |
|-------|------|
| O1 Noēsis | 認識推論・深い理解・本質把握 |
| O2 Boulēsis | 意志推論・目標設定・優先順位決定 |

詳細仕様が必要な場合は `view_file` で SKILL.md を参照。

---

## 4.3 認知態勢の確立 (Hexis)

| 認知態勢 | 発動定理 | 発動条件 |
|:---------|:---------|:---------|
| Poiēsis（制作） | S2 Mekhanē `inve` | アイデア・プロトタイプ・実験 |
| Praxis（実践） | S4 Praxis `prax` | 実装・修正・リファクタ |
| Theōria（観照） | A2 Krisis | レビュー・検証・最適化 |

自動修正 (Diorthōsis): コード生成時に軽微な違反を検出 → 1回のみ自動修正を試行（再帰禁止）→ 修正内容を出力に含める

---

## 4.4 CCL コアパターン復習

| パターン | 意味 | 例 |
|:---------|:-----|:---|
| `*^` | 融合 + 思考過程のメタ表示 | `/noe*dia^` |
| `*` vs `~` | 結果のみ vs 過程を往復表示 | `/bou*zet` vs `/bou~zet` |
| `_` | シーケンス（A の後に B） | `/boot _/bou` |
| `+` / `-` | 深化 / 縮約 | `/noe+` / `/noe-` |
| `^` / `/` | 上昇 / 下降 | `/noe^` / `/noe/` |

> 頻出誤解: `*^` は「`*` と `^` の独立」ではなく「融合のメタ表示」

---

## 4.5 tools.yaml 読込

```bash
cat ~/oikos/hegemonikon/.agent/tools.yaml
```

---

## 4.6 Gnōsis 知識鮮度チェック

```bash
.venv/bin/python mekhane/anamnesis/cli.py check-freshness
```

Stale の場合:

```bash
.venv/bin/python mekhane/anamnesis/cli.py collect --auto
```

---

## 4.7 Mnēmē Synthesis インデックス更新

```bash
.venv/bin/python mekhane/anamnesis/mneme_cli.py ingest --all
```

---

## 4.8 白血球 — 統合消化サジェスト

> 白血球: 自主的に未消化コンテンツを捕食する

```bash
cd ~/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python -c "
import json
from pathlib import Path
from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
state_path = Path('mekhane/gnosis/state.json')
state = json.loads(state_path.read_text()) if state_path.exists() else {}
undigested = state.get('undigested', {'papers': [], 'jules_prs': []})
p = DigestorPipeline()
result = p.run(max_papers=15, max_candidates=3, dry_run=True)
print(f'論文: {len(result.candidates)} 消化候補')
for i, c in enumerate(result.candidates, 1):
    print(f'  {i}. [{c.score:.2f}] {c.paper.title[:45]}...')
if undigested.get('jules_prs'):
    print(f'Jules PR: {len(undigested[\"jules_prs\"])} 未審査')
" 2>&1 | grep -v Warning
```

---

> **制約リマインダ**: CCL `*^` は融合メタ表示。Diorthōsis は1回のみ(再帰禁止)。

*/boot サブモジュール — v2.0 FBR*
