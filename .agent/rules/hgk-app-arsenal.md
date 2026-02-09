---
trigger: always_on
glob:
description: HGK Desktop App 開発: 既存 PJ を使え（臨時ルール）
lifecycle: temporary
expires: 2026-06-01
reason: Desktop App 開発期間中。開発完了後 model_decision に降格
---

# 🔴 HGK Desktop App 開発: 既存 PJ を使え

> **臨時ルール** — Desktop App 開発期間中のみ always_on
> 開発完了後は `lifecycle: permanent` の部分のみが残る

---

## Desktop App 専用ツール (臨時)

| # | モジュール | import パス | 用途 |
|:--|:---|:---|:---|
| 1 | **Jules Client** | `mekhane.symploke.jules_client` | TS/CSS/Three.js を Jules に dispatch |
| 2 | **JulesPool** | `synergeia.jules_api.JulesPool` | 6アカ並列、`create_session(task, repo)` |
| 3 | **Coordinator** | `synergeia.coordinator.coordinate` | CCL→最適スレッド自動選択 |
| 4 | **CCLGraphBuilder** | `hermeneus.src.graph.CCLGraphBuilder` | CCL→StateGraph→3D可視化 |
| 5 | **gpu_guard** | `mekhane.symploke.gpu_guard` | Three.js WebGL + LLM 競合防止 |

## 開発プロセス (臨時)

```
1. /mek+(/manual) でタスク設計書を書く
2. dispatch.py で CCL→AST→計画テンプレート確認
3. Coordinator で振り分け:
   - Jules → TS/CSS/Three.js (repo=laihuip001/hegemonikon)
   - Gemini → UI デザイン/レイアウト
   - Claude → API/FEPロジック/レビュー
4. jules_results_loader で結果取り込み
5. /dia+ でレビュー
```

## 禁止事項 (臨時)

| ❌ 禁止 | ✅ 必須 |
|:---|:---|
| Three.js を手書き | Jules に dispatch |
| CSS を手書き | Gemini に dispatch |
| GPU 競合を無視 | gpu_guard.ensure_safe_gpu() |

---

*lifecycle: temporary — expires: 2026-06-01*
