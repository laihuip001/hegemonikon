# PROOF.md — 存在証明書

PURPOSE: aristos モジュールの実装
REASON: aristos の機能が必要だった

> **∃ aristos/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón プロジェクト` の一部として存在が要請される
2. **機能公理**: `aristos モジュールの実装` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | Aristos: ワークフロールーティング最適化 & 進化エンジン |
| `cost.py` | Aristos Cost — WF 実行コスト計算 |
| `evolve.py` | PROOF: [L2/進化基盤] このファイルは存在しなければならない |
| `evolve_cli.py` | Aristos Evolution CLI |
| `game_theory.py` | Aristos Game Theory — WF 間の Nash 均衡ベース配分 |
| `graph_builder.py` | Aristos Graph Builder — WF 依存関係グラフの自動構築 |
| `pt_optimizer.py` | Aristos PT Optimizer — CostVector.scalar() の重みを GA で最適化 |
| `route_feedback.py` | Aristos Route Feedback — ルーティングフィードバックの収集・永続化 |
| `router.py` | Aristos Router — WF 間の最適経路探索 |
| `status.py` | Aristos Status — 進化状態とフィードバック統計の集約 |
| `test_evolve.py` | Aristos L2 Evolution Engine Tests |
| `test_router.py` | Aristos Router Unit Tests |
| `visualize.py` | Aristos Visualize — ターミナルでのフィードバック統計可視化 |

---

*Generated: 2026-02-08 by generate_proofs.py*
