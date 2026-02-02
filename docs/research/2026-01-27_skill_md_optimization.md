# AI/LLM向けSKILL.md最適構造設計レポート

> **Source**: Perplexity Pro Research (2026-01-27)
> **Theme**: Hegemonikón O-series発動判断精度最大化フレームワーク

---

## エグゼクティブサマリー

2025年後半から2026年1月の独立実証研究による主要な発見：

| 発見 | 効果 | 出典 |
| :--- | :--- | :--- |
| YAML frontmatter「スキャン層」限定 | 10-50 tokens/skill でマッチング | Reddit/Vertu |
| Primacy Effect（冒頭1/3が40%+影響） | +15-20% 発動精度 | ACL 2025 |
| 否定条件の脆弱性（87.5% Priming Failure） | 誤発動 -34% (正条件強調時) | ArXiv 2025 |
| 指令の呪い（10指示で成功率15%） | 階層化で 44-58% に改善 | OpenReview |
| Markdown > JSON（-34-38% トークン） | 効率 + 精度向上 | LinkedIn |

---

## 1. LLM SKILL解釈の二層スキャン機構

| フェーズ | 処理内容 | コスト | 精度 |
|---------|--------|-------|------|
| **Phase 1: Metadata Scan** | 全スキルのfrontmatterのみ読込 | 10-50 tokens/skill | 90-95% |
| **Phase 2: Matching** | スキル説明とクエリの意味類似度 | - | 85-92% |
| **Phase 3: Full Context Load** | マッチしたスキル本文を完全読込 | 600-1200 tokens | 88-96% |

---

## 2. トークン位置効果

- **Primacy Effect**: 冒頭1/3が40%+の判定に影響（73/104タスク）
- **Recency Effect**: 末尾の形式指定は高い遵守率
- **Middle Effect**: 中央への焦点は稀

**改善策**: When to Use を冒頭、Output Format を末尾に配置 → +23-32% 精度向上

---

## 3. 否定条件の限界

**Semantic Gravity Wells 論文（2025年9月）**:

- 成功時の抑圧強度: ΔP = 22.8%
- 失敗時の抑圧強度: ΔP = 5.2%
- **比率: 4.4倍の非対称性**

**失敗モード**:

- Priming Failure (87.5%): 「〜するな」が逆に活性化
- Override Failure (12.5%): 後層が抑圧信号を上書き

**対策**: 正の trigger を強調、否定条件は「参照」のみ

---

## 4. 複数指示による「指令の呪い」

```
成功率(n) ≈ P(individual)^n

例:
- 1指示: 92% → 10指示: 44%
- 改善（Self-Refinement後）: 58%
```

**軽減策: O/S/T階層による段階的開示**:

- Tier 0 (Critical): frontmatter（指示数5以下）
- Tier 1 (High): 本文（指示数5-8）
- Tier 2 (Medium): S-series（新規読込）
- Tier 3 (Low): T-series（on-demand）

---

## 5. フォーマット比較

| フォーマット | 精度 | トークン効率 | 推奨用途 |
|------------|------|------------|---------|
| YAML | 87-89% | 基準 | frontmatter |
| JSON | 68-71% | +18% | 非推奨 |
| Markdown | 82-84% | -34-38% | 本文 |

**結論**: YAML frontmatter + Markdown 本文の二層構造が最適

---

## 6. Claude vs Gemini 差異

| モデル | YAML理解度 | Markdown | 複数指示 | 推奨 |
|-------|-----------|----------|---------|------|
| Claude 3.7 | 94% | 87% | 58% | YAML + XML tags |
| Gemini 2.5 | 89% | 91% | 52% | Markdown中心 |

---

## 7. 10の設計原則

1. 二層構造: YAML(100-150 tokens) + Markdown(600-1000 tokens)
2. Primacy Effect: When to Use を本文冒頭へ
3. 否定条件参照化: when_not_to_use は最小化
4. 指示数制限: 単一スキル内5以下
5. 表形式活用: Core Function で -34-38% 効率
6. 処理ロジック差別化: O3/O4 は詳細、O1/O2 は簡潔
7. Edge Cases: O4 必須、O3 推奨、O1/O2 任意
8. Output Format末尾: Recency Effect 活用
9. モデル別最適化: Claude=XML, Gemini=詳細Markdown
10. 版管理必須: version フィールド

---

## 参考文献

- [ACL Findings 2025: Serial Position Effects](https://aclanthology.org/2025.findings-acl.52.pdf)
- [ArXiv: Semantic Gravity Wells](https://arxiv.org/html/2601.08070v1)
- [OpenReview: ManyIFEval Benchmark](https://openreview.net/forum?id=R6q67CDBCH)
- [LinkedIn: Prompt Formats Comparison](https://www.linkedin.com/pulse/understanding-prompt-formats-xml-markdown-yaml-made-simple-paluy-fgtkc)
- [Nurix AI: Gemini vs Claude Coding](https://www.nurix.ai/resources/gemini-pro-claude-sonnet-coding-comparison)

---

*Extracted from Perplexity Pro Research, 2026-01-27*
