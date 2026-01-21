---
description: セッション開始時の統合ブートシーケンス。履歴同期とレビュー生成を実行。
hegemonikon: Aisthēsis-H, Praxis-H, Anamnēsis-H
modules: [M1, M8]
---

# /boot ワークフロー

> **Hegemonikón Module**: M1 Aisthēsis (知覚) + M8 Anamnēsis (Load Phase)

Hegemonikón Phase 1 のブートシーケンス。

## 実行手順

// turbo-all

1. **プロファイル読込**: `GEMINI.md` を確認し、Hegemonikón Doctrine が有効であることを確認

2. **コアモジュール有効化**:
   > この段階で以下のSkillを認識し、セッション中に使用する:
   > - **M1 Aisthēsis** for 初期分析・文脈認識・状況ラベリング
   > - **M2 Krisis** for 優先順位判定・目標整合性評価
   
   これらのSkillの詳細仕様が必要な場合は `view_file` で `.agent/skills/m1-aisthesis/SKILL.md` または `.agent/skills/m2-krisis/SKILL.md` を参照。

3. **M8 長期記憶読込 (Load Phase)**:
   - `M:\Brain\.hegemonikon\` から以下を読み込み:
     - `patterns.yaml` → M3 Theōria へ提供（過去のパターン）
     - `values.json` → M4 Phronēsis へ提供（価値関数）
     - `trust_history.json` → M6 Praxis へ提供（信頼履歴）
   - 読み込み失敗時は警告を表示し、白紙状態で続行

4. **履歴同期判定**: 前回の同期から6時間以上経過している場合、`/hist` を実行
   - 同期状態は `.sync-state.json` で管理

5. **Gnōsis 知識更新チェック**: ローカル知識基盤の鮮度を確認
   - コマンド: `python m:/Hegemonikon/forge/gnosis/cli.py check-freshness`
   - **分岐 (Interactive)**: 上記コマンドが `exit code 1` (Stale) を返した場合:
     - ユーザーに更新するか尋ねる ("Gnōsisデータが古いです。更新しますか？")
     - Yesの場合: `python m:/Hegemonikon/forge/gnosis/cli.py collect-all -q "LLM agent reasoning" -l 20` を実行

6. **今日のレビュー生成**: `/rev` を実行し、タスク/リマインドを抽出

7. **ブート完了報告**: 以下の形式で報告
   ```
   [Hegemonikon] M1 Aisthesis
     入力: /boot 実行
     文脈: セッション開始
     プロファイル: Loaded
   
   [Hegemonikon] M8 Anamnesis
     Load Phase: 完了
     パターン: [N]件
     価値関数: [Loaded/Empty]
   
   🚀 HEGEMONIKON BOOT COMPLETE
   ✅ Profile: Loaded
   ✅ Memory: [Loaded / Empty]
   ✅ History Sync: [実行/スキップ]
   ✅ Review: Generated
   ```

8. **Today's Review を表示**: `/rev` の出力内容を表示

## 出力形式

ブート完了後、以下を出力:
- ブート完了バナー
- 長期記憶ステータス（パターン数、価値関数状態）
- Today's Review（優先タスク、フォローアップ、提案）

