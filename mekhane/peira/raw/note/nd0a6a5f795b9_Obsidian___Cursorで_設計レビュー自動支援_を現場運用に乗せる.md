# Obsidian × Cursorで「設計レビュー自動支援」を現場運用に乗せる

> **Source**: https://note.com/tasty_dunlin998/n/nd0a6a5f795b9
> **Published**: 2025-12-22T18:34:32+09:00
> **Collected**: 2026-02-06T21:35:28.235446

---

Highリスクだけ個別ノート化して、Dataviewで常時監視し、監査証跡までつなぐ実装テンプレ

この記事で扱うこと設計書ドラフトを起点に、

リスク抽出（根拠付き）

トレーサビリティ（REQ↔DES↔TST）

テスト観点（リスク連動）

Highリスクの常時監視（Dataview）

監査向けの「対応証跡レポート」自動生成

までを、Obsidian Vault（= Git管理） と Cursor（AIエディタ） の組み合わせで実装する手順をまとめます。「AIが賢いか
