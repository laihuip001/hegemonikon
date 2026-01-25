---
description: セッション開始時の統合ブートシーケンス。履歴同期とレビュー生成を実行。
hegemonikon: Aisthēsis-H, Praxis-H, Anamnēsis-H
modules: [T1, T8]
---

# /boot ワークフロー

> **Hegemonikón T-series**: T1 Aisthēsis (知覚) + T8 Anamnēsis (Load Phase)

Hegemonikón Phase 1 のブートシーケンス。

## 実行手順

// turbo-all

0. **設定ファイル同期**: M:\.gemini → C:\Users\{USER}\.gemini
   ```powershell
   & "m:\Hegemonikon\.agent\scripts\sync-config.ps1"
   ```
   > **目的**: Mドライブ（Git管理）を正本とし、Antigravityが読み込むCドライブに反映。

0.5. **前回Handoff読み込み**: 前回セッションの引き継ぎ情報を読み込み
   - 対象: `M:\Brain\.hegemonikon\sessions\handoff_*.md` の最新ファイル
   - 存在する場合: 内容を表示し、「前回の続きから開始」を提案
   - 存在しない場合: スキップ
   > **対応ワークフロー**: `/bye` で生成されたHandoff

1. **プロファイル読込**: `GEMINI.md` を確認し、Hegemonikón Doctrine が有効であることを確認

2. **コアモジュール有効化**:
   > この段階で以下のSkillを認識し、セッション中に使用する:
   > - **T1 Aisthēsis** for 初期分析・文脈認識・状況ラベリング
   > - **T2 Krisis** for 優先順位判定・目標整合性評価
   
   これらのSkillの詳細仕様が必要な場合は `view_file` で `.agent/skills/t-series/t1-aisthesis/SKILL.md` または `.agent/skills/t-series/t2-krisis/SKILL.md` を参照。

2.5. **利用可能ツール読み込み**: `.agent/tools.yaml` を読み込み、利用可能な機構を把握
   - 出力形式:
     ```
     [Hegemonikon] 利用可能ツール
       MCP: gnosis (search, stats, recommend_model)
       Scripts: chat-history-sync, gnosis-cli
       Workflows: /boot, /hist, /plan, /ask, /src, /think, /rev, /chk
     ```
   - **目的**: セッション中は tools.yaml に登録されたツールを積極的に活用する

2.6. **tools.yaml 整合性リマインド**:
   - 「最近追加したツール（MCP/スクリプト/ワークフロー）は tools.yaml に登録されていますか？」
   - 未登録の可能性がある場合: `view_file .agent/tools.yaml` で確認を促す
   - **目的**: 新ツール追加時の登録忘れを防止（習慣化）

3. **T8 長期記憶読込 (Load Phase)**:
   - `M:\Brain\.hegemonikon\` から以下を読み込み:
     - `patterns.yaml` → T3 Theōria へ提供（過去のパターン）
     - `values.json` → T4 Phronēsis へ提供（価値関数）
     - `trust_history.json` → T6 Praxis へ提供（信頼履歴）
   - 読み込み失敗時は警告を表示し、白紙状態で続行

4. **履歴同期判定**: 前回の同期から6時間以上経過している場合、`/hist` を実行
   - 同期状態は `.sync-state.json` で管理

5. **Gnōsis 知識更新チェック**: ローカル知識基盤の鮮度を確認
   - コマンド: `python m:/Hegemonikon/mekhane/anamnesis/cli.py check-freshness`
   - **自動収集**: Stale の場合、自動で収集実行:
     ```powershell
     & "m:/Hegemonikon/.agent/scripts/gnosis-auto-collect.ps1"
     ```

5.1. **未分類論文リマインド**: 未分類の論文があれば通知
   - 出力: `📚 Gnōsis: [N]件の未分類論文 → /tag で分類`

5.5. **Perplexity Inbox 読み込み**: パプ君リサーチの新着確認
   - 対象フォルダ: `M:\Hegemonikon\docs\research\perplexity\`
   - 新規ファイル（前回bootから追加されたもの）がある場合:
     ```
     📥 Perplexity新着: [N]件
     1. {filename} ({日時})
     2. {filename} ({日時})
     
     → 読み込んでタスク提案しますか？ [y/n]
     ```
   - **[y]の場合**: 各ファイルを読み込み、サマリ + タスク提案を生成
   - **[n]の場合**: スキップして次のステップへ
   - 読み込み後、ファイルを `docs/research/` に移動するか確認

6. **今日のレビュー生成**: `/rev` を実行し、タスク/リマインドを抽出

7. **ブート完了報告**: 以下の形式で報告
   ```
   [Hegemonikon] T1 Aisthesis
     入力: /boot 実行
     文脈: セッション開始
     プロファイル: Loaded
   
   [Hegemonikon] T8 Anamnesis
     Load Phase: 完了
     パターン: [N]件
     価値関数: [Loaded/Empty]
   
   🚀 HEGEMONIKON BOOT COMPLETE
   ✅ Profile: Loaded
   ✅ Memory: [Loaded / Empty]
   ✅ History Sync: [実行/スキップ]
   ✅ Perplexity Inbox: [N件処理 / 0件]
   ✅ Review: Generated
   ```

8. **Today's Review を表示**: `/rev` の出力内容を表示

## 出力形式

ブート完了後、以下を出力:
- ブート完了バナー
- 長期記憶ステータス（パターン数、価値関数状態）
- Perplexity新着処理結果
- Today's Review（優先タスク、フォローアップ、提案）
