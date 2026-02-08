# PROOF.md — 存在証明書

PURPOSE: 解釈エンジンの中核ソースコード
REASON: 認知解釈の具体実装が必要だった

> **∃ src/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `Hegemonikón プロジェクト` の一部として存在が要請される
2. **機能公理**: `解釈エンジンの中核ソースコード` を実現するファイル群がここに配置される

## ファイル構成

| ファイル | 役割 |
|:---------|:-----|
| `__init__.py` | Hermēneus — CCL 実行保証コンパイラ |
| `__main__.py` | Hermēneus __main__.py |
| `ast.py` | Hermēneus AST (Abstract Syntax Tree) Nodes |
| `audit.py` | Hermēneus Audit — 検証履歴の記録と追跡 |
| `checkpointer.py` | Hermēneus Checkpointer — 実行状態の永続化と復元 |
| `cli.py` | Hermēneus CLI — コマンドラインインターフェース |
| `constraints.py` | Hermēneus Constraints — 構造化出力の強制 |
| `executor.py` | Hermēneus Executor — ワークフロー実行エンジン |
| `expander.py` | Hermēneus Expander — CCL 省略形を正式形に展開 |
| `graph.py` | Hermēneus Graph — CCL AST を LangGraph StateGraph に変換 |
| `hitl.py` | Hermēneus HITL — Human-in-the-Loop 制御 |
| `macros.py` | Hermēneus Macro Loader — ccl/macros/ から標準マクロを読み込む |
| `mcp_server.py` | Hermēneus MCP Server — AI 自己統合 |
| `optimizer.py` | Hermēneus Optimizer — 自動プロンプト最適化 |
| `parser.py` | Hermēneus Parser — CCL 式を AST に変換 |
| `prover.py` | Hermēneus Prover — 形式的正確性検証 |
| `registry.py` | Hermēneus Registry — ワークフロー定義管理 |
| `runtime.py` | Hermēneus Runtime — LMQL プログラムを実行 |
| `synergeia_adapter.py` | Hermēneus Synergeia Adapter — Synergeia 統合 |
| `translator.py` | Hermēneus Translator — AST を LMQL プログラムに変換 |
| `verifier.py` | Hermēneus Verifier — Multi-Agent Debate による検証 |

---

*Generated: 2026-02-08 by generate_proofs.py*
