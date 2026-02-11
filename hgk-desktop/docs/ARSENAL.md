# 🔴 ARSENAL — HGK App 開発で使う既存 PJ 完全マップ

> **手作業でコードを書く前に、ここを確認しろ。**

---

## Tier 1: 開発タスク自動化 (CCL Pipeline)

| モジュール | パス | 能力 | CLI |
|:---|:---|:---|:---|
| **dispatch.py** | `hermeneus/src/dispatch.py` | CCL→AST→計画テンプレート | `python hermeneus/src/dispatch.py '/ene+'` |
| **Coordinator** | `synergeia/coordinator.py` | CCL→最適スレッド dispatch | `python synergeia/coordinator.py '/ene+'` |
| **JulesPool** | `synergeia/jules_api.py` | 6アカ/3並列/ラウンドロビン | `python synergeia/jules_api.py create "task"` |
| **jules_client** | `mekhane/symploke/jules_client.py` | 836L async API, セッション追跡 | import のみ |
| **Executor** | `hermeneus/src/executor.py` | compile→execute→verify→audit | import のみ |

## Tier 2: アプリ機能のバックエンド

| モジュール | パス | 能力 |
|:---|:---|:---|
| **WorkflowRegistry** | `hermeneus/src/registry.py` | WF 定義の正本 (YAML→dataclass) |
| **CCLGraphBuilder** | `hermeneus/src/graph.py` | CCL AST → StateGraph (ノード+エッジ) |
| **morphism_proposer** | `mekhane/taxis/morphism_proposer.py` | trigonon→射提案 |
| **Attractor** | `mekhane/fep/attractor_advisor.py` | Series/Theorem 推薦 |
| **doxa_promoter** | `mekhane/symploke/doxa_promoter.py` | beliefs 昇格 |
| **Anamnesis CLI** | `mekhane/anamnesis/cli.py` | Gnōsis ベクトル検索 |
| **Peira health** | `mekhane/peira/hgk_health.py` | ヘルスチェック |
| **Dendron EPT** | `mekhane/dendron/` | 存在証明検証 |

## Tier 3: インフラ・安全

| モジュール | パス | 能力 |
|:---|:---|:---|
| **gpu_guard** | `mekhane/symploke/gpu_guard.py` | GPU 競合防止 (RTX 2070 SUPER) |
| **EnergeiaCoreResolver** | `mekhane/poiema/flow/energeia_core.py` | Metron レベル→モデル選択 |
| **EpocheShield** | `mekhane/poiema/flow/epoche_shield.py` | PII マスキング |
| **synedrion_reviewer** | `mekhane/symploke/synedrion_reviewer.py` | 偉人評議会レビュー |
| **jules_results_loader** | `mekhane/symploke/jules_results_loader.py` | Jules 結果取り込み |
| **insight_miner** | `mekhane/symploke/insight_miner.py` | セッション成果抽出 |

## MCP サーバー

| サーバー | パス | 状態 |
|:---|:---|:---|
| gnosis | `mekhane/mcp/gnosis_mcp_server.py` | 設定済み・要接続確認 |
| typos | 外部 | 設定済み・要接続確認 |

---

*Created: 2026-02-09 /m+/jukudoku*
