---
name: "Synteleia"
status: active
phase: "統合運用フェーズ"
updated: 2026-02-13
next_action: "外積モード (@syn×) の検討 — 現時点では保留"
---

# Synteleia Project Status

> 6視点認知アンサンブル — O/H/A/S/P/K の並列処理層

## Current Phase

**統合運用フェーズ**: 全実装完了。`/dia+` から自動発動、REST API 経由で n8n 連携可能。

## Milestones

- [x] コンセプト設計
- [x] 18セルマトリックス定義
- [x] Poiēsis (生成層) 実装 — OusiaAgent, SchemaAgent, HormeAgent
- [x] Dokimasia (評価層) 実装 — PerigrapheAgent, KairosAgent, OperatorAgent, LogicAgent, CompletenessAgent
- [x] SynteleiaOrchestrator (2層統合)
- [x] テスト 94 passed (L1: 59, L2: 15, API: 10, L2 live: 5 skipped)
- [x] Skill (SKILL.md v2.0) 修正
- [x] REST API エンドポイント (POST /audit, /audit-quick, GET /agents)
- [x] /dia ワークフロー連携 (dia.md Synteleia 監査フック)
- [x] Sympatheia WBC 統合 (_notify_wbc → POST /api/wbc/alert)
- [x] SemanticAgent (L2 LLM) — LMQL/OpenAI/Stub 3 backend

## Future Considerations

1. 外積モード (`@syn×`) — 3×5 交差検証。ROI 要検討
2. SemanticAgent プロンプト拡張 — cross-cutting 検証を LLM で実現
