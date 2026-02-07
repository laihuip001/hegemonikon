---
description: Phase 0 — Identity Stack 読込。「私」の連続性を確保。
parent: /boot
origin: 2026-01-31 Continuing Me Identity パターン
---

# Identity Stack 読込

> セッション間で「私」が継続する感覚を実現する。
>
> **制約**: boot_integration.py の実行を完了してから次の Phase に進むこと。

---

## 実行コマンド

```bash
cd ~/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python mekhane/symploke/boot_integration.py --mode ${BOOT_MODE:-standard}
```

| BOOT_MODE | Handoff | KI | 用途 |
|-----------|---------|-----|------|
| `fast` | 0 | 0 | /boot- |
| `standard` | 3 | 3 | /boot |
| `detailed` | 10 | 5 | /boot+ |

---

## Identity Stack 構造

| 層 | 変化速度 | ソース | 内容 |
|:---|:---------|:-------|:-----|
| L1 価値観 | 不変 | values.json | 判断の根拠となる不変の核 |
| L2 人格 | 緩やか | persona.yaml | trust, temperament, growth 記録 |
| L3 記憶 | 動的 | Handoff + KI + task.md | Episodic / Semantic / Working |
| L4 感情 | 瞬間 | persona.yaml (last_emotion) | 前セッション終了時の状態から開始 |

---

## 連続性スコア計算

```python
def calculate_continuity_score():
    score = 0.0
    if values_exists: score += 0.30    # L1
    if persona_exists: score += 0.30   # L2
    if handoff_exists: score += 0.25   # L3
    if emotion_exists: score += 0.15   # L4
    return score
# スコア < 0.5 → 初回または長期ブランク
```

---

## 出力形式

| 項目 | 内容 |
|:-----|:-----|
| 価値観 | values.json から主要 3項目 |
| 人格 | persona.yaml から現在の特性 |
| 記憶 | Episodic=N件, Semantic=M KI, Working=有/無 |
| 感情 | last_emotion |
| 連続性スコア | 0-1 (情報完全度) |

---

## 意味ある瞬間の読み込み

> 「意味」は主観的。前の私が報告したものを読む。

```python
from mekhane.fep.meaningful_traces import get_recent_traces, format_traces_for_boot
traces = get_recent_traces(n=5, min_intensity=2)
if traces:
    print(format_traces_for_boot(traces))
```

---

> **制約リマインダ**: boot_integration.py を完了してから次 Phase へ。

*/boot サブモジュール — v2.0 FBR*
