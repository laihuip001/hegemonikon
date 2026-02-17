---
name: Periskopē
description: HGK Deep Research Engine — multi-source parallel search + multi-model synthesis + TAINT verification
triggers:
  - "periskope"
  - "periskopē"

version: "1.0.0"
depends_on:
- doc_id: AXIOM_HIERARCHY
  min_version: 7.0.0

risk_tier: "L2"
risks:
  - "外部検索 API (SearXNG, Exa) への過剰リクエスト"
  - "自動生成テンプレート — import パスの検証が必要"
reversible: true
requires_approval: false
fallbacks: ["search_web / read_url_content で個別検索"]
---

# Periskopē

> **目的**: HGK Deep Research Engine — multi-source parallel search + multi-model synthesis + TAINT verification

> [!CAUTION]
> このテンプレートは自動生成です。
> **以下の import パスを実際のコードと照合して検証してください。**
> 存在しないクラス名・関数名を書くと、Skill が機能しません。
> 検証コマンド: `PYTHONPATH=. .venv/bin/python -c "from mekhane.periskope import YOUR_CLASS"`

## 発動条件

- TODO: トリガー条件を定義

## 手順

### Step 1: TODO — import パスを検証して書き換えること

// turbo

```bash
# FIXME: 以下は仮のコマンド。実際のモジュールに合わせて書き換えること
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
# TODO: import パスを実際のコードと照合
# from mekhane.periskope import MAIN_CLASS
print('TODO: periskope の実行コマンドを定義')
"
```

---

*v1.0 — 自動生成 (2026-02-15)*
