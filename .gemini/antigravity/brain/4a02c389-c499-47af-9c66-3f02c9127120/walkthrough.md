# Hermēneus Phase 1-7 完了 Walkthrough

## 概要

CCL (Cognitive Control Language) の **コンパイル→実行→検証→MCP 統合** により、**AI が自身で CCL を実行できる** システムが完成。

## テスト結果

```
================== 125 passed, 2 skipped, 2 warnings ==================
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Antigravity IDE                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   MCP Client                        │   │
│  └──────────────────────┬──────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────▼───────────────────────────────────┐
│              Hermēneus MCP Server (Phase 7)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  hermeneus_execute | hermeneus_compile | audit       │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────▼──────────────────────────────┐  │
│  │         Workflow Executor (Phase 6)                  │  │
│  │   compile → execute → verify → audit pipeline        │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────▼──────────────────────────────┐  │
│  │              LLM Backends                            │  │
│  │         (Claude, GPT-4, Gemini)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 主要ファイル

| Phase | ファイル | 役割 |
|:------|:---------|:-----|
| 1-3 | ast, parser, translator, runtime, graph | コアコンパイラ |
| 4 | verifier, audit, prover | 形式検証 |
| 5 | cli | CLI エントリー |
| 6 | registry, executor, synergeia_adapter | Workflow 実行 |
| 7 | [mcp_server.py](file:///home/makaron8426/oikos/hegemonikon/hermeneus/src/mcp_server.py) | MCP Server |

**合計: ~6,000行 | 18 モジュール**

## MCP ツール

| ツール | 機能 |
|:-------|:-----|
| `hermeneus_execute` | CCL ワークフロー実行 + 検証 |
| `hermeneus_compile` | CCL → LMQL コンパイル |
| `hermeneus_audit` | 監査レポート取得 |
| `hermeneus_list_workflows` | ワークフロー一覧 |

## 使用例

```python
# AI がツールを呼び出す
result = hermeneus_execute(
    ccl="/noe+",
    context="プロジェクト分析",
    verify=True
)
# → 検証済み結果が返却される
```

---

*Completed: 2026-02-01 | v0.7.0 MCP Server (AI 自己統合)*
