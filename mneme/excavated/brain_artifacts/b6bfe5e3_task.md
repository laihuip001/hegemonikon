# Task List: Forge MVP & FileMaker Advisor

## P0: Forge MVP完成 ✅
- [x] ディレクトリ構成の最終決定
- [x] `server/`, `start-server.ps1` 削除（既に存在しないことを確認）
- [x] `forge.ps1` 動作検証（Web依存排除確認）
- [x] ルートディレクトリ整理（.gitignore, README更新）
- [x] Git commit完了 (53b4798)

## P1: FileMaker相談役プロンプト作成 ✅
- [x] FileMaker技術要素の調査
- [x] MICKS業務内容の整理
- [x] システムプロンプト設計 → `library/filemaker-advisor.md`
- [x] Forgeライブラリへの統合

## P2: カテゴリ名変更「働きかける」→「動く」 ✅
- [x] `modules`廃止・ルート移動（フラット化）
- [x] プロンプトモジュール以外のファイルを`90_🛠️ 設定・開発`に隔離
- [x] `forge.ps1`等のスクリプトパス修正
- [x] `README.md`更新
- [x] ディレクトリ番号付与 (10, 20, 30, 40, 90) 並び順保証
- [x] 不要な重複ファイル (`⚡ 動く.md`) 削除

## P3: OMEGA統合 + FileMaker Advisor増強 ✅
- [x] GEMINI.md にOMEGAコア（M0-M5, M8）を統合 (`Documents/mine/.../Forge`にも適用)
- [x] FileMaker Advisor増強 (`Documents/mine/.../Forge/library`にも適用)
- [x] Git commit完了 (Forgeリポジトリ復旧後)

## P4: user_rules + AI Studio Prompt ✅
- [x] OMEGA user_rules軽量版作成 → `library/omega-user-rules.md`
- [x] AI Studio用FileMaker学習プロンプト → `library/filemaker-learning-coach.md`

## P5: Main Merge + 絵文字ディレクトリ ✅
- [x] phase3-complete → main force push (`7f3c5cc`)
- [x] 絵文字ディレクトリ構造を実装（modules配下）
- [x] v1.0.0タグ作成・push完了
- [x] **ディレクトリフラット化（modules廃止・ルート移動）** (`cf8a123`)
