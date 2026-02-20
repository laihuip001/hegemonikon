# eat_deep_research_tools — Deep Research ロールモデル消化

> 消化深度: /eat+ (L3 Deep)
> 消化日: 2026-02-19
> テーマ: 真の "Deep" Research を実現するための学術的基盤

---

## 消化候補 3 論文

### 1. STORM — Multi-Perspective Question Asking (Stanford)

- **論文**: "Assisting in Writing Wikipedia-like Articles From Scratch with LLMs"
- **著者**: Yijia Shao et al. (Stanford, 2024)
- **arXiv**: 2402.14207
- **被引用**: 120
- **核心**: Topic に対して**多様な視点を発見**し、異なる視点の Writer が Topic Expert に**質問を投げかけるシミュレーション**を行う。収集した情報からアウトラインを生成。
- **HGK 接点**: `/zet` (問いの探索) の外部実装例。多視点質問 = CCL の収束的発振 `~*`

### 2. DeepResearcher — RL で Deep Research を学習

- **論文**: "DeepResearcher: Scaling Deep Research via RL in Real-world Environments"
- **著者**: Yuxiang Zheng et al. (GAIR-NLP, 2025)
- **arXiv**: 2504.03160
- **被引用**: 152
- **核心**: RL で LLM に Deep Research を**エンドツーエンドで学習**させる。RAG ではなく実際の Web 検索環境で訓練。**計画策定、多ソース相互検証、自己反省、正直さ** が emergent behavior として発現。
- **HGK 接点**: BC-9 (メタ認知) の自然発生。第零原則「自分を信じない」の RL 的実装。
- **GitHub**: <https://github.com/GAIR-NLP/DeepResearcher>

### 3. SFR-DeepResearch — 自律的単一エージェント

- **論文**: "SFR-DeepResearch: Effective RL for Autonomously Reasoning Single Agents"
- **著者**: Xuan-Phi Nguyen et al. (Salesforce, 2025)
- **arXiv**: 2509.06283
- **被引用**: 18
- **核心**: マルチエージェントではなく**単一エージェント**が文脈に基づいて次のアクションを動的に決定。Humanity's Last Exam で 28.7%。Continual RL + reasoning-optimized models。
- **HGK 接点**: Periskopē が目指すべき方向。単一エージェント + RL = Hermēneus の CCL 実行と構造的類似。

---

## 消化方針

| 論文 | 消化目的 |
|:-----|:---------|
| STORM | **多視点質問生成**のアルゴリズムを Periskopē の /zet に統合 |
| DeepResearcher | **RL 訓練の emergent behaviors** を HGK の BC 体系と照合 |
| SFR-DeepResearch | **単一エージェント設計**の選択根拠を Periskopē のアーキテクチャに反映 |
