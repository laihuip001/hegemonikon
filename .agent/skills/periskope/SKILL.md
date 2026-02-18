---
name: Periskopē
description: HGK Deep Research Engine — multi-source parallel search + multi-model synthesis + TAINT verification
triggers:
  - "periskope"
  - "periskopē"
  - "deep research"
  - "調査"

risk_tier: "L2"
risks:
  - "外部検索 API (SearXNG, Exa) への過剰リクエスト"
  - "Cortex API 呼び出し (翻訳, refinement query 生成)"
reversible: true
requires_approval: false
fallbacks: ["search_web / read_url_content で個別検索"]
---

# Periskopē

> **目的**: Multi-source parallel search + multi-model synthesis + citation verification

## パイプライン

```
Query → [W3: 日英翻訳展開] → [W1/W2: 並列カテゴリ検索]
  → Dedup → [W4: BGE-M3 Rerank] → Synthesis
  → [W6: Multi-pass (optional)] → Citation Verification → Report
```

## 発動条件

- `/sop` ワークフロー実行時
- `periskope` / `調査` キーワード検出時
- 外部論文・技術情報の深層調査が必要な場合

## 手順

### Step 1: CLI から実行

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m mekhane.periskope.cli \
  "検索クエリ" \
  --output report.md
```

### Step 2: オプション

| フラグ | 説明 | デフォルト |
|:-------|:-----|:----------|
| `--sources` | 検索ソース (searxng exa gnosis sophia kairos) | all |
| `--max-results` | ソースあたりの最大件数 | 10 |
| `--no-verify` | Citation verification をスキップ | false |
| `--no-expand` | 日英翻訳展開 (W3) を無効化 | false (展開する) |
| `--multipass` | 2パス反復検索 (W6) を有効化 | false |
| `--digest` | 結果を /eat incoming に自動出力 | false |
| `--digest-depth` | Digest テンプレート深度 (quick/standard/deep) | quick |
| `-o, --output` | レポート出力先ファイル | stdout |
| `-v, --verbose` | デバッグログ | false |

### Step 3: Python API から実行

```python
from mekhane.periskope.engine import PeriskopeEngine

engine = PeriskopeEngine(
    max_results_per_source=10,
    verify_citations=True,
)
report = await engine.research(
    query="free energy principle",
    expand_query=True,    # W3: bilingual expansion
    multipass=False,      # W6: 2-pass refinement
)
print(report.markdown())
```

### Step 4: 推奨パターン

| ユースケース | コマンド |
|:------------|:--------|
| 通常調査 | `--output report.md` |
| 深掘り調査 | `--multipass --output report.md` |
| 速度優先 | `--no-expand --no-verify` |
| 論文のみ | `--sources gnosis sophia` |
| 消化連携 | `--digest --digest-depth standard` |

---

*v2.0 — P5 パラメータ公開 (2026-02-18)*
