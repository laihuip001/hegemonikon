# Phase 4 実装計画: 運用とprompt-lang実験

## ゴール説明
ForgeプロジェクトをPhase 3（基盤構築）からPhase 4（運用・実験）へ移行します。安定版である `phase3-complete` ブランチを `main` にマージし、`prompt-lang` の設計フェーズ（Phase A）を開始します。

## ユーザーレビュー事項
- **ブランチ戦略**: マージ後、`phase3-complete` をバックアップとして残すか削除するか。（デフォルト案: 参照用に残す）
- **新規ブランチ名**: 新規作業用に `feature/prompt-lang-design` を提案します。

## 提案する変更

### 1. マージとリポジトリ整備
- **Merge**: `phase3-complete` -> `main`
- **Tag**: ロールバック用に `main` 上でタグ `v1.0.0-phase3-complete` を作成。
- **Cleanup**: なし（デフォルト案に従いブランチは保持）。

### 2. Phase A: Prompt-Lang 構文設計
- **New Branch**: `main` から `feature/prompt-lang-design` を作成しスイッチ。
- **New Directory**: `design/prompt-lang/`
- **New File**: `design/prompt-lang/syntax_spec_v0.1.md`
    - `docs/brain_dump/prompt-lang-vision.md` に基づく構文の初期ドラフト。
    - 定義内容:
        - メタデータブロック (`@system`, `@archetype` 等)
        - 変数構文
        - 制御フロー（あれば）
        - example構造

#### [NEW] [syntax_spec_v0.1.md](file:///c:/Users/user/.gemini/Forge/design/prompt-lang/syntax_spec_v0.1.md)

## 検証計画

### 手動検証
- **Merge Check**: `git log --oneline --graph --all` でマージトポロジーを確認。
- **File Check**: マージ後、`main` 上に全ての `library/*` や `docs/*` ファイルが存在することを確認。
- **Design Review**: `syntax_spec_v0.1.md` のユーザーレビュー。
