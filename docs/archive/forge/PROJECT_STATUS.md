# 📊 Project Status Report (2026-01-21)

> **Time**: 2026-01-21 14:30
> **Context**: Post-Gnōsis Integration / prompt-lang Release

## 🚀 Active Products

### 1. Gnōsis (Knowledge Foundation)
- **Status**: **v0.2 (Active / Offensive)**
- **Role**: AIの長期記憶・知識基盤。Local First + Agent-Driven.
- **Recent Progress**:
  - ✅ **Integration**: M5 Peira への "Local First" ロジック実装完了。
  - ✅ **Automation**: `/boot` ワークフローへのインタラクティブ更新チェック導入。
  - ✅ **Offensive**: ArXiv/OpenAlex からの能動的知識収集 (200+ papers)。
- **Relation to AIDB**: 旧 AIDB プロジェクト (Phase 6) を吸収・統合。

### 2. prompt-lang (AI Communication Language)
- **Status**: **v1.0 (Released)**
- **Role**: AI間通信のための構造化言語プロトコル。
- **Recent Progress**:
  - ✅ **Spec**: v0.1 仕様策定完了 (`experimental/prompt-lang/SPEC.md`).
  - ✅ **Impl**: Parser, Validator, SkillAdapter 実装完了。
  - ✅ **Test**: 統合テストパス。運用フェーズへ移行。

### 3. Forge (Platform Core)
- **Status**: **v1.0 (Stable)**
- **Role**: プロンプトエンジニアリング・ツール群 (CLI/Web)。
- **Status**:
  - 安定稼働中。`cli.ps1`, `start-server.ps1` 等のコア機能は完備。
  - 課題: Obsidian/GitHub 連携の設計思想見直し (Pending)。

---

## 💤 Legacy / Merged Products

### 4. AIDB (Artificial Intelligence Data Base)
- **Status**: **Migrated to Gnōsis**
- **Note**:
  - 過去の収集データ (Phase 1-5) は Gnōsis の資産として継承。
  - 自動収集タスク (Phase 6) は Gnōsis CLI に実装済み。
  - 自動収集タスク (Phase 6) は Gnōsis CLI に実装済み。
  - 今後は "Gnōsis" として一元管理される。

### 5. Chat History DB (Memory)
- **Status**: **v2.0 (Active / Auto-Synced)**
- **Role**: AI長期記憶の永続化。
- **Recent Progress**:
  - ✅ **Backend**: LanceDB への完全移行。
  - ✅ **Automation**: Windows Task Scheduler によるバッチ同期(10分毎)の確立。
  - `/hist` コマンドはメンテナンス用として残存するが、日常使用は不要化。

---

## 📅 Next Milestones

1. **Gnōsis v1.0**:
   - Semantic Scholar API 完全統合。
   - 知識を活用した推論精度の向上（実績作り）。

2. **prompt-lang v1.1**:
   - 実務での使用実績に基づく仕様改定。
   - VSCode Extension (Optional).

3. **Hegemonikon**:
   - システム全体の「賢さ」の向上。道具作りから、実問題解決へのシフト。
