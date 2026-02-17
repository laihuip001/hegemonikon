---
description: "確かめる — /kho{git_diff}_/sta{quality}_C:{V:{/dia+}_/ene+}_/pra{test}_/pra{dendron_guard}_/tek{check}_/pis_/dox"
lcm_state: beta
version: "2.0"
---

# /ccl-vet: 自己検証マクロ

> **CCL**: `@vet = /kho{git_diff}_/sta{quality}_C:{V:{/dia+}_/ene+}_/pra{test}_/pra{dendron_guard}_/tek{check}_/pis_/dox`
> **用途**: 実装完了後の構造的自己検証
> **v2.0**: S3 Stathmos + P4 Tekhnē を統合 (24定理活用深化 Phase 2)

## 展開

| # | ステップ | 定理 | 意味 |
|:--|:---------|:-----|:-----|
| 1 | `/kho{git_diff}` | **P1 Khōra** | git diff でスコープ(空間)を特定 |
| 2 | `/sta{quality}` | **S3 Stathmos** | ⭐ **品質の計量**: 変更は何を改善/劣化させたか？ 測定可能か？ |
| 3 | `C:{V:{/dia+}_/ene+}` | **A2 Krisis + O4 Energeia** | 検証→修正の収束ループ |
| 4 | `_/pra{test}` | **S4 Praxis** | テスト実行 = 実践的検証 |
| 5 | `_/pra{dendron_guard}` | **S4 Praxis** | Dendron Guard (PROOF/PURPOSE チェック) |
| 6 | `_/tek{check}` | **P4 Tekhnē** | ⭐ **技術妥当性**: 選んだ技術/ライブラリは適切か？ |
| 7 | `_/pis_/dox` | **H2 Pistis + H4 Doxa** | 確信度と発見パターンを記憶 |

## S3 Stathmos 品質チェック (v2.0 追加)

> **問い**: 「この変更の品質をどう計量するか？」

| チェック項目 | 問い |
|:------------|:-----|
| テスト網羅率 | 新規コードにテストはあるか？ |
| エラー処理 | 失敗ケースは考慮されているか？ |
| パフォーマンス | 計測可能な劣化はないか？ |
| 可読性 | 6ヶ月後の自分が読めるか？ |

## P4 Tekhnē 技術チェック (v2.0 追加)

> **問い**: 「選んだ技術は問題に適しているか？」

| チェック項目 | 問い |
|:------------|:-----|
| 既存との整合 | プロジェクトの技術スタックと一致しているか？ |
| 過剰設計 | ライブラリを入れたが、標準機能で足りなかったか？ |
| 依存リスク | 外部依存を増やしていないか？ (Protocol D 適用) |

## Dendron Guard ステップ

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m mekhane.dendron guard .
```

> **アンチウイルスのリアルタイム保護**: 変更ファイルのみ高速チェック。
> FAIL 時は修正してから `/pis` に進む。

## 使用例

```ccl
@vet                       # 標準検証 (S3+P4 込み)
@vet _ /dia+               # 検証後に敵対的レビュー
```

## 定時スキャン (cron)

```bash
# 日次 (hegemonikon)
0 3 * * * ~/oikos/hegemonikon/scripts/dendron_guard.sh

# 週次 "雑草刈り" (oikos 全体)
0 4 * * 0 ~/oikos/hegemonikon/scripts/dendron_guard.sh --full
```
