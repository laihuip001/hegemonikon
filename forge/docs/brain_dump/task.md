# メタプロンプトSKILL統合タスク

## 目的
ClaudeのメタプロンプトSKILLシステムをForgeプロジェクトに統合し、軍事級メタプロンプトシステムを強化する。

---

## タスクリスト

### Phase 1: 分析 (完了)
- [x] SKILLファイル内容の確認（1212行、4コンポーネント）
- [x] Forgeプロジェクト構造の把握
- [x] 既存テストの確認（`test-forge.ps1`）

### Phase 2: 計画策定 (完了)
- [x] 統合アプローチの決定 → **案E: Hybrid Adaptive採用**
- [x] 実装計画書の作成 → `design-alternatives.md`
- [x] ユーザーレビュー依頼

### Phase 3: 実装 (完了)
- [x] GEMINI.md現状確認 → **空（0バイト）**
- [x] Antigravityアーキテクチャ理解 → ナレッジベース7ファイル確認
- [x] GEMINI.mdにCOOメタプロンプトSKILL設計・配置
- [x] Julesへの仮説検証（PE指示書でプロンプト生成できるか） → **成功**
- [x] library/配下のテンプレート充填 (16/16)

### Phase 4: 検証 (未着手)
- [ ] 既存テストの実行
- [ ] 新規機能のテスト
- [ ] ウォークスルー作成

---

## 分析結果

### SKILLファイル構成
| コンポーネント | 内容 |
|---|---|
| Meta-Prompt Generator v3.0 | 6フェーズワークフロー |
| Archetypes Reference | 5アーキタイプ定義（Precision/Speed/Autonomy/Creative/Safety） |
| Quality Checklist | Pre-Mortemチェックリスト |
| Templates | 3テンプレート（Code Reviewer, Project Producer, Ruthless Mirror） |
| Transformations | 曖昧語→具体化変換ルール |

### Forgeプロジェクト構成
```
Forge/
├── modules/         # 120モジュール
│   ├── act/         # 行動系（create/prepare）
│   ├── find/        # 発見系
│   ├── reflect/     # 振り返り系
│   └── think/       # 思考系（expand/focus）
├── protocols/       # プロトコル定義
├── knowledge/       # 知識ベース
└── The Cognitive Hypervisor Architecture.md  # XML版システムプロンプト
```
