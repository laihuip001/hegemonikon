---
trigger: always_on
glob: 
description: HGK Desktop App 開発: 既存 PJ を使え
---

# 🔴 HGK Desktop App 開発: 既存 PJ を使え

> **このファイルは always_on ルール。読み飛ばしたら第零原則違反。**
> **手作業でコードを書く前に、ここに載っている PJ を使えないか必ず確認しろ。**

---

## 絶対使うもの (MUST)

| # | モジュール | import パス | 用途 |
|:--|:---|:---|:---|
| 1 | **Jules Client** | `mekhane.symploke.jules_client` | TS/CSS/Three.js を Jules に dispatch |
| 2 | **JulesPool** | `synergeia.jules_api.JulesPool` | 6アカ並列、`create_session(task, repo)` |
| 3 | **Coordinator** | `synergeia.coordinator.coordinate` | CCL→最適スレッド自動選択 |
| 4 | **dispatch.py** | `hermeneus.src.dispatch.dispatch` | CCL→AST→実行計画テンプレート |
| 5 | **WorkflowRegistry** | `hermeneus.src.registry.WorkflowRegistry` | WF定義の正本 |
| 6 | **CCLGraphBuilder** | `hermeneus.src.graph.CCLGraphBuilder` | CCL→StateGraph→3D可視化 |
| 7 | **Executor** | `hermeneus.src.executor.WorkflowExecutor` | compile→execute→verify→audit |
| 8 | **morphism_proposer** | `mekhane.taxis.morphism_proposer` | 射提案エンジン |
| 9 | **gpu_guard** | `mekhane.symploke.gpu_guard` | Three.js WebGL + LLM 競合防止 |
| 10 | **Attractor** | `mekhane.fep.attractor_advisor` | Series/Theorem 推薦 |

## 開発プロセス (MUST)

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

## 禁止事項

| ❌ 禁止 | ✅ 必須 |
|:---|:---|
| Three.js を手書き | Jules に dispatch |
| CSS を手書き | Gemini に dispatch |
| WF 定義を手動で JSON 化 | WorkflowRegistry を使う |
| CCL を手動で解析 | dispatch.py を叩く |
| GPU 競合を無視 | gpu_guard.ensure_safe_gpu() |

## チェック: 「手作業をしようとしていないか？」

コードを書く前に自問:

1. この作業は Jules/Gemini に振れないか？
2. 既存モジュールに同じ機能がないか？
3. dispatch.py を先に叩いたか？

**3つ全て NO なら手作業 OK。1つでも YES なら既存 PJ を使え。**

---

*Created: 2026-02-09 /m+/jukudoku の結果として*
