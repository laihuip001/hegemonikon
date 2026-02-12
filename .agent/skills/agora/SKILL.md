---
name: Agora
description: HGK 収益化プロジェクト — ディープインパクト戦略
triggers:
  - "agora"
  - "agora"

# Safety Contract (v1.0)
# Anti-Confidence 原則: リスクを宣言しないスキルは信頼できない
risk_tier: L1             # L1(低) - 標準的な運用
reversible: true           # 出力が可逆か
requires_approval: false   # 実行前に Creator 承認が必要か
risks:                     # 想定リスクのリスト
  - "Execution of arbitrary code if import paths are incorrect"
fallbacks:                 # 失敗時の代替 Skill
  - ""
---

# Agora

> **目的**: HGK 収益化プロジェクト — ディープインパクト戦略

> [!CAUTION]
> このテンプレートは自動生成です。
> **以下の import パスを実際のコードと照合して検証してください。**
> 存在しないクラス名・関数名を書くと、Skill が機能しません。
> 検証コマンド: `PYTHONPATH=. .venv/bin/python -c "from .home.makaron8426.oikos.agora import YOUR_CLASS"`

## 発動条件

- TODO: トリガー条件を定義

## 手順

### Step 1: TODO — import パスを検証して書き換えること

// turbo

```bash
# FIXME: 以下は仮のコマンド。実際のモジュールに合わせて書き換えること
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
# TODO: import パスを実際のコードと照合
# from .home.makaron8426.oikos.agora import MAIN_CLASS
print('TODO: agora の実行コマンドを定義')
"
```

---

*v1.0 — 自動生成 (2026-02-12)*
