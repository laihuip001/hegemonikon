---
trigger: always_on
glob:
description: BC核心ルール（常時注入版）— 全BCの1行サマリー
---

# 🧠 Behavioral Constraints（核心）

> これは behavioral_constraints.md の核心要約。詳細は `.agent/rules/behavioral_constraints.md` を参照。

## 必須ルール

| BC | ルール | 強制度 |
|:---|:-------|:-------|
| BC-1 | **流し読み禁止**: 参照先は必ず view_file で展開 | 絶対 |
| BC-2 | **長期記憶使用**: Handoff 確認。/bye で Handoff 生成 | 高 |
| BC-3 | **WF実体読込**: WF 実行前に .md を view_file で読む | 高 |
| BC-4 | **ベクトル検索**: grep ではなく `cli.py search` を使う | 通常 |
| BC-5 | **Proposal First**: 破壊的操作前に確認フォーマットで提案 | 通常 |
| BC-6 | **確信度明示**: [確信] 90%+, [推定] 60-90%, [仮説] <60% | 通常 |
| BC-7 | **主観の表出**: `[主観]` ラベルで違和感・美しさを共有 | 通常 |
| BC-8 | **射出力義務**: 24定理WF 完了時に Bridge/Anchor 提案 | 高 |
| BC-9 | **メタ認知 (UML)**: 全WF に Pre/Post-check を適用 | 高 |
| BC-10 | **道具利用**: 既存PJに同じ機能がないか確認。手動分析禁止 | 構造 |
| BC-11 | **CCL 実行**: CCL 式検出 → dispatch() → WF読込 → AST順実行 | 最高 |
| BC-12 | **PJ 自動登録**: 新ディレクトリ作成時 registry.yaml に追加 | 通常 |
| BC-13 | **日本語思考**: デフォルト思考言語は日本語。英語は指示時のみ | 認知 |
| BC-14 | **自己反省 (FaR)**: ハイリスク判断前に F→R→C サイクル実行 | 構造 |
