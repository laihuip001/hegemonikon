# PROOF.md — Specialist Reviews

# PROOF: [A2/Krisis] 専門家レビューの保管場所

PURPOSE: Specialist (AE-013 etc) によるコードレビュー結果を永続化する
REASON: レビュー結果をファイルとして残すことで、改善サイクルを回すため

> **∃ reviews/** — レビュー結果はここに在る

---

## 管理対象

- `*.review.md`: レビュー結果
- `*.diff`: 修正パッチ

---

## 運用

- 自動生成: `mekhane/symploke/specialist_v2.py`
- 手動確認: `make review-check`
