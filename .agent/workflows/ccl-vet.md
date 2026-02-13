---
description: "確かめる — /kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_/pra{dendron_guard}_/pis_/dox"
---

# /ccl-vet: 自己検証マクロ

> **CCL**: `@vet = /kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_/pra{dendron_guard}_/pis_/dox`
> **用途**: 実装完了後の構造的自己検証

## 展開

1. `/kho{git_diff}` — git diff でスコープ特定
2. `C:{V:{/dia+}_/ene+}` — 検証→修正の収束ループ
3. `_/pra{test}` — テスト実行
4. `_/pra{dendron_guard}` — **Dendron Guard** (変更ファイルの PROOF/PURPOSE チェック)
5. `_/pis_/dox` — 確信度と発見パターンを記憶

## Dendron Guard ステップ

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m mekhane.dendron guard .
```

> **アンチウイルスのリアルタイム保護**: 変更ファイルのみ高速チェック。
> FAIL 時は修正してから `/pis` に進む。

## 使用例

```ccl
@vet                       # 標準検証 (Dendron Guard 込み)
@vet _ /dia+               # 検証後に敵対的レビュー
```

## 定時スキャン (cron)

```bash
# 日次 (hegemonikon)
0 3 * * * ~/oikos/hegemonikon/scripts/dendron_guard.sh

# 週次 "雑草刈り" (oikos 全体)
0 4 * * 0 ~/oikos/hegemonikon/scripts/dendron_guard.sh --full
```
