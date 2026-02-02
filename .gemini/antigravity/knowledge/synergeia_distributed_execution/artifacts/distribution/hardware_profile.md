# Synergeia: Home PC Infrastructure Evaluation

## 1. 物理スペック (Primary Execution Node)

| コンポーネント | スペック |
|:---------------|:---------|
| **CPU** | AMD Ryzen 9 3900X (12 Cores / 24 Threads) |
| **RAM** | 32 GB DDR4 |
| **GPU** | NVIDIA GeForce RTX 2070 Super (8 GB VRAM) |
| **OS** | Linux (Dual Boot 検討中) / Docker 稼働中 |

## 2. 実行能力評価 (OpenManus 基準)

- **Coordinator/Agents**: CPU コア数が豊富なため、複数のコンテナを並列稼働させても余裕あり。
- **Browser/Coder Agent**: RAM 32GB は十分な作業領域を提供。
- **LLM Inference**:
  - **Local (Ollama等)**: 7B〜14B クラスのモデルは GPU 8GB 内で高速動作可能。
  - **Cloud API**: コスト効率と精度の観点から、メインの推論は API (Claude/Gemini) 経由を推奨し、GPU はローカルでの微細な補助タスクやデータ処理に充当する。

## 3. インフラ・ロードマップ

1. **Docker 環境の安定化**: OpenManus 用の安定した隔離環境を構築。
2. **API ブリッジの確立**: GCP (現在のセッション) と自宅 PC 間のセキュアな通信（n8n webhook 等）をテスト。
3. **OS 最適化**: リアルタイム性を重視する場合、Linux への完全移行またはリソース優先度の調整を行う。

---
*Consolidated: 2026-02-01 | Synergeia Hardware Profile v1.0*
