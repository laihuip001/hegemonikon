# Boulēsis 優先タスク (2026-01-28)

> **Origin**: `/bou` PHASE 0 → Creator 確認済み

## 現在のセッション目標

1. [x] **Mnēmē Synthesis CLI 実装** ✅
2. [x] **Dispatch Log 運用開始** ✅
3. [x] **3-Layer Architecture リファクタリング** ✅ (全26 workflow)

---

## タスク 1: Mnēmē Synthesis CLI 実装

- [x] 既存インフラ調査 (`sophia_ingest.py`, `kairos_ingest.py`)
- [x] テスト構造確認 (`test_ingest.py`)
- [x] 実装計画作成 + /noe 分析
- [x] `/boot` 対応パスに `mneme_cli.py` 作成
- [x] `ingest --all` コマンド実装 (Sophia + Kairos + Chronos 統合)
- [x] 動作確認テスト (Sophia: 65件, Kairos: 19件)

---

## タスク 2: Dispatch Log 運用開始

- [x] 現セッションのワークフロー実行を記録 (4件: /boot, /bou, /noe, /ene)
- [x] Phase B 進捗更新 (4/50)
- [x] 記録フォーマット確認済み

---

## タスク 3: 3-Layer Architecture リファクタリング

- [x] /noe.md 確認 (v3.0 対応済み)
- [x] /plan.md に skill_ref 追加 → v2.5
- [x] /why.md に skill_ref 追加 → v2.2
- [x] 主要 τ-workflow に skill_ref 追加: boot v2.6, bye v2.6, dev v1.1
- [x] Δ-layer workflow に skill_ref 追加: a v2.3, o v2.3, h v2.3, s v2.3, k v2.3, p v2.3
- [x] 補助 workflow に skill_ref 追加: ax v2.2, x v2.2, u v1.1
- [x] **完了: 全26 workflow に skill_ref 実装済み** ✅

---

## タスク 4: Sophia MCP サーバー (18:04 /bou)

- [x] sophia_mcp_server.py コード確認 (281行、完成済み)
- [x] バックエンド検証: Sophia 65件、Kairos 19件
- [x] 依存関係: `mcp>=1.20.0` は requirements.txt に記載済み
- [x] venv 再構築: .venv/ に mcp 1.26.0, sentence-transformers 5.2.2 インストール完了
- [x] **動作確認成功**: stdio_server connected, 検索機能 OK ✅

---

## タスク 5: Markdown Lint 一括修正 (18:04 /bou)

- [x] boot.md: 9箇所の言語指定なしコードブロック修正
- [x] Δ-layer workflow (a, h, s, k, p, o): 一括修正
- [x] 統合 workflow (ax, x): 一括修正
- [x] その他 (dia, epo, fit, pan, syn, zet, dev): 一括修正
- [x] **完了: 全 workflow で MD040 空言語エラー解消** ✅
