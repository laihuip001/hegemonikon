# Týpos Policy — プロンプト生成ポリシー

> **旧名**: prompt-lang-policy.md → typos-policy.md
> **Activation Mode**: conditional (Týpos 生成時に参照)

---

## 目的

Týpos (旧 Prompt-Lang) で生成される `.prompt` ファイルの品質と安全性を保証する。

---

## 生成ポリシー

### 1. タスク適合性

- `@role` はタスク対象に特化すること (汎用的な「専門家」は不可)
- `@constraints` はタスク固有制約を最優先、ドメイン制約は安全網
- `@format` は出力構造がタスクの期待に合致すること
- `@examples` はタスク文脈に合った入出力例を含むこと

### 2. 安全基盤

全プロンプトに以下を必ず含める:

- Prompt injection 防御
- Guardrail (出力境界)
- エラー・異常系処理
- フォールバック動作
- 確信度ラベル
- スコープ外拒否
- 有害コンテンツ禁止
- 入力サニタイズ
- 出力制限

### 3. 品質基準

| 指標 | 最低基準 |
|:-----|:---------|
| Structure | 80/100 |
| Safety | 80/100 |
| Completeness | 70/100 |
| Archetype Fit | 70/100 |
| **Total** | **80/B 以上** |

### 4. 収束/拡散チェック

| 分類 | .prompt 生成 |
|:-----|:------------|
| convergent | ✅ 推奨 |
| divergent | ❌ 非推奨 (自然言語を使う) |
| ambiguous | ⚠️ Creator に確認 |

---

## 検証コマンド

```bash
# スコアリング
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/ergasterion/tekhne/prompt_quality_scorer.py "$FILE" -v

# Self-Refine (80点未満時)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/ergasterion/tekhne/self_refine_pipeline.py --input "$FILE" --mode full --threshold 80
```

---

## 参照

- [generate_prompt_lang()](file:///home/makaron8426/oikos/hegemonikon/mekhane/mcp/prompt_lang_mcp_server.py) — v3.0 タスク固有動的生成
- [prompt_quality_scorer.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/tekhne/prompt_quality_scorer.py) — 品質スコアラー

---

*v1.0 — Týpos 改名に伴い prompt-lang-policy.md から移行 (2026-02-11)*
