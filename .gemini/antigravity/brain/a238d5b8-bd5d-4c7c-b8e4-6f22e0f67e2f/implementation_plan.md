# 実装計画: tekhne-maker 統合 + 定時実行ワークフロー

## 概要

866人の Jules 専門家プロンプトを `tekhne-maker` v5.0 のアーキタイプ駆動設計で生成し、GitHub Actions で定時実行する。

---

## Phase 1: プロンプトテンプレート作成

### 1.1 専門家アーキタイプマッピング

| カテゴリ | アーキタイプ | 理由 |
|----------|-------------|------|
| 認知負荷 (CL) | 🎯 Precision | 誤検知を許容しない |
| AI固有リスク (AI) | 🎯 Precision + 🛡 Safety | セキュリティ重視 |
| 非同期 (AS) | 🎯 Precision | バグ検出が目的 |
| 理論整合性 (TH) | 🎨 Creative | FEP解釈に柔軟性必要 |
| 美学 (AE) | 🎨 Creative | スタイル判断 |

### 1.2 成果物

#### [NEW] `mekhane/symploke/specialist_prompts.py`

```python
from dataclasses import dataclass
from enum import Enum

class Archetype(Enum):
    PRECISION = "precision"
    SPEED = "speed"
    AUTONOMY = "autonomy"
    CREATIVE = "creative"
    SAFETY = "safety"

@dataclass
class SpecialistPrompt:
    id: str
    name: str
    archetype: Archetype
    focus: str
    quality_standards: list[str]
    output_format: str
    edge_cases: list[str]
    fallback: str

def generate_prompt(spec: SpecialistPrompt, target_file: str) -> str:
    """tekhne-maker 形式のプロンプトを生成"""
    ...
```

---

## Phase 2: 定時実行スクリプト

#### [MODIFY] `mekhane/symploke/run_specialists.py`

- `specialist_prompts.py` からプロンプト生成
- バッチ実行ロジックをリファクタリング
- 結果収集とブランチチェック統合

---

## Phase 3: GitHub Actions ワークフロー

#### [MODIFY] `.github/workflows/jules-scheduled-tasks.yml`

```yaml
on:
  schedule:
    - cron: "0 0 * * 1"  # 毎週月曜 00:00 UTC (09:00 JST)
  workflow_dispatch:

jobs:
  specialist-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install aiohttp
      - run: python mekhane/symploke/run_specialists.py
        env:
          JULIUS_API_KEY_7: ${{ secrets.JULIUS_API_KEY_7 }}
          JULIUS_API_KEY_8: ${{ secrets.JULIUS_API_KEY_8 }}
          JULIUS_API_KEY_9: ${{ secrets.JULIUS_API_KEY_9 }}
```

---

## 必要アクション（ユーザー）

1. **GitHub Secrets 設定**: `JULIUS_API_KEY_7`, `8`, `9` をリポジトリに追加

---

## スケジュール

| Phase | 内容 | 所要時間 |
|-------|------|----------|
| 1 | プロンプトテンプレート作成 | 10分 |
| 2 | 定時実行スクリプト更新 | 5分 |
| 3 | GitHub Actions 更新 + push | 5分 |
