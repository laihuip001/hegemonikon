# AI に偉人会議をさせる — Synedrion

> **ID**: E10
> **想定媒体**: Note（エッセイ）→ Zenn
> **想定読者**: 一般読者、哲学好き
> **フック**: Socrates、Wittgenstein、Friston の3人で議論させたらどうなるか

---

## 本文構成（案）

### 1. Synedrion（評議会）とは

- 複数の「偉人ペルソナ」を LLM で再現
- 同一のテーマについて多角的に議論させる
- 人間は「傍聴者」として学ぶ

### 2. 実装

```python
council = [
    {"name": "Socrates", "style": "対話法。相手の前提を問い返す"},
    {"name": "Wittgenstein", "style": "言語の限界を指摘する"},
    {"name": "Friston", "style": "FEP で形式化する"},
]

for round in range(3):
    for member in council:
        response = llm.generate(
            system=member['style'],
            prompt=f"テーマ: {topic}\n前の発言: {prev}"
        )
```

### 3. 実際の議論例

テーマ: 「AI は主体か？」

- **Socrates**: 「主体とは何か？まずそれを定義しよう」
- **Wittgenstein**: 「『主体』という言語ゲームの規則に注目すべきだ」
- **Friston**: 「Markov blanket があれば主体として扱える」

### 4. 得られた知見

- 1人の AI に「多角的に考えて」より品質が高い
- 各ペルソナに明確なスタイルを設定することが重要
- 3ラウンドで十分な深さに達する

### 5. 読者が試せること

```
# 3人の専門家になりきって議論してください:
1. 実務家: コスト・納期・実現性を重視
2. 理論家: 原理的な正しさを重視
3. ユーザー: 体験・使いやすさを重視

テーマ: [議論したいこと]
3ラウンドの対話を生成してください。
```

---

*関連: B9 (主体性), B5 (Forge), C4 (AIレビュアー)*
