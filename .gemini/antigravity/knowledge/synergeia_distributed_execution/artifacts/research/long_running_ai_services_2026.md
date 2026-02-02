# 30分以上の長時間自律タスク処理AIサービス完全ガイド (2026-02-01)

## 1. クラウドAIモデル・API

### Anthropic Claude (最有力)

- **Claude Agent SDK**: セッション時間制限なし。Context compaction により理論的に無制限の実行が可能。
- **Extended Thinking**: 5分以上の複雑な推論に対応し、1時間のキャッシュ保持が可能。
- **Message Batches API**: 24時間以内の非同期処理（50%コスト削減）。

### Google Gemini / Vertex AI

- **Context Window Compression**: 15分〜10分の制限を回避し、事実上無制限に延長。
- **Memory Bank (Vertex AI)**: 自動長期メモリ管理。
- **Agent Engine**: 月額 180,000 vCPU-seconds の無料枠。

### Mistral AI

- **Temporal Integration**: Durable execution により、クラッシュ後の状態復旧が自動化。
- **Mistral AI Studio**: Temporal ベースのランタイム。

### OpenManus (Open Source Multi-Agent)

- **Coordinator & Specialists**: Coordinator がタスクをパースし、Research, Coder, Reporter などの専門家に分散。
- **Durable Docker Environment**: Docker コンテナ内での隔離実行と、長時間タスクの並行処理。
- **MVP (Colab)**: [OpenManus Colab MVP](/home/makaron8426/oikos/hegemonikon/experiments/openmanus_mvp.ipynb) にて動作確認。GPT-4o-mini ベースで Web 調査やコーディングを自律代行。
- **Hegemonikón 親和性**: `/bou` から `/ene` へのワークフローをエージェント群へマッピング（ Translator 開発により自動化可能）。

## 2. ワークフロー・プラットフォーム

- **n8n**: AI 統合（LangChain, Claude 等）が深く、自ホストによりタイムアウト制限を撤廃可能。
- **Make.com / Zapier**: シンプルな自動化に向くが、論理深度や時間制限に制約あり。

## 3. 実践的設計パターン

1. **マルチセッションハーネス**: 進捗を外部ファイル（Markdown/Git）に記録し、セッションを跨いで状態を維持。
2. **メモリ階層化 (HCC)**: エピソディックとセマンティックの分離によりトークン効率を 70% 改善。
3. **Context Compression**: Gemini 等で使用必須。70〜80% の閾値で自動圧縮を作動させる。

---
*Based on autonomous_ai_infrastructure research consolidated at 2026-02-01.*
