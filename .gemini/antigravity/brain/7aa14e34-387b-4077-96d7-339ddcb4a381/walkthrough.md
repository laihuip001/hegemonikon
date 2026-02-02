# Walkthrough: エピソード記憶機構の復旧と自動化

## 調査結果

| データソース | 読み取り | 内容 |
|:-------------|:--------:|:-----|
| `conversations/*.pb` | ❌ | **暗号化済み** (直接パース不可) |
| `brain/*/walkthrough.md` | ✅ | セッションログ (329件) |
| `knowledge/` | ✅ | KI artifacts (163件) |

**結論**: 会話の完全なテキスト復旧は不可。但し Walkthrough/KI から主要情報は回収可能。

---

## 実装完了

### 1. `episodic_backup.sh`

- **機能**: brain/ と knowledge/ を mneme にバックアップ
- **自動化**: cron で 1時間ごとに実行
- **初回実行**: 492 ファイル、5MB をバックアップ完了

### 2. `walkthrough_export.py`

- **機能**: /bye 時に最新の walkthrough を mneme にコピー
- **テスト結果**: 3ファイル (walkthrough, task, implementation_plan) をエクスポート

---

## 新アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│ L1: Episodic (Handoff + Walkthrough)                    │
│ L2: Semantic (KI + Doxa)                                │
│ L3: Working (task.md + implementation_plan.md)          │
└─────────────────────────────────────────────────────────┘
```

---

## 残課題

- [ ] bye.md に walkthrough_export.py の呼び出しを追加
- [ ] Git diff 記録の自動化
- [ ] Kairos インデックス統合
