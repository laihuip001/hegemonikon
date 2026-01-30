# Hegemonikón

> **認知の統率中枢** — FEP + Stoic Philosophy に基づく認知フレームワーク

---

## 30秒で理解する

**Hegemonikón は「考える」を構造化したシステムです。**

- **7つの公理** — 認知の基本原則
- **24の定理** — 6系列 × 4定理（O, S, H, P, K, A）
- **36の関係** — 定理間の接続（X-series）

合計 **60要素** が、認知プロセスを体系化します。

---

## 構造

```
hegemonikon/
├── kernel/      # 公理・定理（不変層）
├── mekhane/     # Python実装（機構層）
├── .agent/      # ワークフロー・スキル（制御層）
└── docs/        # ドキュメント
```

| 層 | 役割 |
|:---|:-----|
| **Kernel** | 7公理 + 24定理 + 36関係 = 60要素 |
| **Mekhane** | FEP実装、記憶、知識ベース |
| **Agent** | /boot, /bye, /noe, /bou 等のワークフロー |

---

## 定理群

| 記号 | 名称 | 本質的問い |
|:-----|:-----|:-----------|
| **O** | Ousia（本質） | 何を知り、望み、問い、すべきか |
| **S** | Schema（戦略） | どのスケール・方法・基準・実践で |
| **H** | Hormē（衝動） | どう感じ、確信し、欲し、信じるか |
| **P** | Perigraphē（環境） | どの場・道・軌道・技法で |
| **K** | Kairos（文脈） | いつ・何のために・どんな知恵で |
| **A** | Akribeia（精度） | どう感情し、判定し、原則化し、知識化するか |

---

## 始め方

```bash
cd hegemonikon
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/
```

---

## 詳細

- [AGENTS.md](AGENTS.md) — AI向けガイド
- [INDEX.md](INDEX.md) — 定理・用語索引
- [kernel/](kernel/) — 公理・定理ドキュメント
- [docs/](docs/) — 詳細ドキュメント

---

## 設計思想

> **"Hyperengineering is a badge of honor."**
>
> 常人は60要素のフレームワークを作らない。
> だからこそ価値がある。

---

*Hegemonikón v3.2 — 認知シミュレーション環境*
