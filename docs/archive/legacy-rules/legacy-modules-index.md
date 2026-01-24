# Legacy Modules Index

> **目的**: 旧資産へのクイックリファレンス。PE開発時に参照可能。
> **更新日**: 2026-01-24
> **ソース**: `M:\Brain\99_🗃️_保管庫｜Archive\プロンプト ライブラリー\モジュール（開発用）\個別のモジュール\`

---

## 蒸留方針

- **そのままインポートしない**: Hegemonikon形式と互換性がないため
- **参照用**: XMLテンプレートとして必要時に参照
- **車輪の再開発防止**: 類似機能を実装する際の参考資料

---

## Module 一覧（25個）

| # | 名称 | 目的 | Hegemonikon対応 |
|:---:|:---|:---|:---:|
| 01 | DMZ Protocol | 設定ファイルの保護（Read-Only） | M1 Aisthēsis 連携可 |
| 02 | Directory Topology Lock | ディレクトリ構造の固定 | Rules で対応済み |
| 03 | Dependency Quarantine | 依存関係の隔離 | 要検討 |
| 04 | TDD Enforcement | テスト駆動開発の強制 | M7 Dokimē 連携可 |
| 05 | Ubiquitous Language | ドメイン言語の統一 | - |
| 06 | Complexity Budget | 複雑度の上限管理 | M6 Praxis 連携可 |
| 07 | Devil's Advocate | 多視点批評 | M7 Dokimē 実装済み |
| 08 | Cognitive Checkpoint | ドリフト防止 | M8 Anamnēsis 連携可 |
| 09 | Mutation Testing | サボトゥール型テスト | - |
| 10 | Ripple Effect Analysis | 影響範囲予測 | M4 Phronēsis 連携可 |
| 11 | Automated Red Teaming | 自動攻撃テスト | M7 Dokimē 連携可 |
| 12 | Chaos Monkey | 耐障害性テスト | 上級用途 |
| 13 | Code Archaeology | Chesterton's Fence | M3 Theōria 連携可 |
| 14 | Narrative Commit | コミットメッセージの物語化 | Rules で対応済み |
| 15 | Atomic Design | UIコンポーネント分割 | - |
| 16 | Accessibility | a11y準拠 | - |
| 17 | Structured Logging | ログ構造化 | - |
| 18 | Feature Flag | トグルアーキテクチャ | - |
| 19 | Docker First | コンテナ化必須 | - |
| 20 | Dead Code Reaper | 死コード削除 | - |
| 21 | TODO Expiration | 技術負債管理 | - |
| 22 | Auto-Documentation | ドキュメント同期 | - |
| 23 | Mock First | インターフェース駆動 | - |
| 24 | Performance Budget | パフォーマンス上限 | - |
| 25 | Rollback Strategy | ロールバック戦略 | - |

---

## 参照方法

必要なモジュールを参照する場合:

```
view_file M:\Brain\99_🗃️_保管庫｜Archive\プロンプト ライブラリー\モジュール（開発用）\個別のモジュール\Module XX ....md
```

---

## Hegemonikon 連携推奨（Top 5）

1. **Module 04 TDD** → M7 Dokimē の検証フェーズに統合
2. **Module 07 Devil's Advocate** → M7 Dokimē の Synedrion に既存
3. **Module 14 Narrative Commit** → `/rev` ワークフローに統合済み
4. **Module 01 DMZ** → `.agent/rules/` に蒸留版を作成推奨
5. **Module 10 Ripple Effect** → M4 Phronēsis の予測機能に統合

---

## 関連ソース

- **Hypervisor Architecture**: `ハイパーバイザー（Hypervisor）/The Cognitive Hypervisor Architecture.md`
- **dev-rules**: `G:\その他のパソコン\太郎\dev\dev-rules\`
- **太郎 .gemini**: `G:\その他のパソコン\太郎\.gemini\`
