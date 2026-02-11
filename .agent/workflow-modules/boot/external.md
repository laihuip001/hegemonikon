---
summary: Phase 5 — 外部入力。Dispatch Log, Perplexity, Jules。
parent: /boot
---

# 外部入力 (External Input)

> 外部ソースからの入力を統合する。
>
> **制約**: 各ソースの新着件数を報告し、処理の選択を Creator に委ねること。

---

## 5.1 Dispatch Log 進捗リマインド

対象: `~/oikos/mneme/.hegemonikon/logs/dispatch_log.yaml`

```bash
cat ~/oikos/mneme/.hegemonikon/logs/dispatch_log.yaml | grep -c "^-" || echo 0
```

出力: Dispatch Log 件数 / 50 (Phase B移行状態)

---

## 5.2 Perplexity Inbox 読み込み

対象フォルダ: `~/oikos/hegemonikon/docs/research/perplexity/`

新規ファイルがある場合:

- ファイル名と日時を一覧表示
- 読み込んでタスク提案するか確認

---

## 5.3 Jules 専門家レビュー結果

```bash
cd ~/oikos/hegemonikon && git fetch origin
git branch -a | grep jules-review | tail -5
```

結果がある場合:

- 実行専門家数、沈黙/発言数、レビューブランチ数を表示
- Critical/High の発見事項を要約

バッチ実行結果 (API経由):

```bash
cd ~/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python -c "
from mekhane.symploke.jules_results_loader import load_latest_results, summarize_findings
results = load_latest_results()
print(summarize_findings(results))
"
```

---

> **制約リマインダ**: 各ソースの新着を報告し、処理選択を Creator に委ねる。

*/boot サブモジュール — v2.0 FBR*
