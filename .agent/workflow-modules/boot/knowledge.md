---
summary: Phase 3 — 知識読込。Sophia, KI, FEP A行列。
parent: /boot
---

# 知識読込 (Knowledge Loading)

> H4 長期記憶 + Sophia + FEP + KI を統合読み込みする。
>
> **制約**: 読み込み失敗時は警告を表示し白紙状態で続行。FEP A行列のデフォルト値を使って良い。

---

## 3.1 H4 長期記憶読込

対象: `~/oikos/mneme/.hegemonikon/`

| ファイル | 用途 |
|:---------|:-----|
| `patterns.yaml` | O1 Noēsis へ提供（過去のパターン） |
| `values.json` | O2 Boulēsis へ提供（価値関数） |
| `trust_history.json` | O4 Energeia へ提供（信頼履歴） |

読み込み失敗時は警告を表示し、白紙状態で続行。

---

## 3.2 Sophia 知識サマリー

> Sophia = 正本、Antigravity KI = 吸収済み

```bash
cd ~/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python -c "
from mekhane.symploke.sophia_ingest import load_sophia_index, search_loaded_index
from pathlib import Path
pkl = Path('~/oikos/mneme/.hegemonikon/indices/sophia.pkl').expanduser()
if pkl.exists():
    adapter = load_sophia_index(str(pkl))
    results = search_loaded_index(adapter, 'implementation design pattern', top_k=5)
    for r in results:
        print(f'  {r.metadata.get(\"ki_name\", \"N/A\")}: {r.metadata.get(\"artifact\", \"N/A\")}')
else:
    print('Sophia: 未初期化 (/bye 実行で蓄積開始)')
"
```

---

## 3.3 FEP A行列読込

> Origin: arXiv:2412.10425 Multi-LLM Active Inference パターン

前回セッションで学習した観察モデル（A行列）を読み込む。

```python
from mekhane.fep import HegemonikónFEPAgent
from pathlib import Path
agent = HegemonikónFEPAgent(use_defaults=True)
learned_a_path = Path('~/oikos/mneme/.hegemonikon/learned_A.npy').expanduser()
if learned_a_path.exists() and agent.load_learned_A():
    print("FEP A行列: 学習済みモデル読込")
else:
    print("FEP A行列: デフォルト使用（未学習）")
```

---

## 3.4 派生選択学習復元

> Cycle: /bye で Doxa 永続化 → /boot で A-matrix プライア更新

```python
from mekhane.fep.doxa_persistence import get_store
store = get_store()
beliefs = store.list_all()
derivative_beliefs = [b for b in beliefs if ":" in b.content and "=" in b.content]
if derivative_beliefs:
    print(f"派生学習: {len(derivative_beliefs)} パターン読込")
    for b in derivative_beliefs[:3]:
        print(f"  {b.content[:40]}... (conf: {b.confidence:.0%})")
else:
    print("派生学習: パターンなし（初回セッション）")
```

---

## 3.5 KI ランダム想起

> 知識は循環しなければ死ぬ。ランダム想起で全KIが生きる。

```python
from pathlib import Path
import random
ki_dir = Path('~/.gemini/antigravity/knowledge').expanduser()
ki_folders = [d for d in ki_dir.iterdir() if d.is_dir() and d.name != 'knowledge.lock']
selected = random.sample(ki_folders, min(3, len(ki_folders)))
for ki in selected:
    overview = ki / 'artifacts' / 'overview.md'
    if overview.exists():
        lines = overview.read_text().split('\n')
        summary = next((l for l in lines if l.strip() and not l.startswith('#')), 'N/A')
        print(f"  [{ki.name}] {summary[:60]}...")
```

---

## 3.6 関連 KI サマリ参照

1. Antigravity が提供する KI サマリを確認
2. 関連性の高い KI を特定
3. 必要に応じて `view_file` で artifact を参照

---

> **制約リマインダ**: 読み込み失敗は白紙で続行。FEP A行列デフォルト可。

*/boot サブモジュール — v2.0 FBR*
