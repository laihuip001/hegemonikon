---
description: デスクトップ操作マクロ。AT-SPI (構造化) → Bytebot VLM (視覚) の自動ルーティング
lcm_state: beta
version: 1.0.0
---

# @desktop: デスクトップ操作マクロ

> **CCL**: `@desktop = /pro_/kho{desktop}_/ene{desktop_action}_V:{/dia-}_/dox-`
> **用途**: デスクトップアプリの操作（クリック、テキスト入力、要素探索）
> **ルーティング**: AT-SPI2 (A パス) 優先 → Bytebot VLM (B パス) フォールバック

## 展開

1. `/pro` — 操作目的の初期傾向を評価
2. `/kho{desktop}` — デスクトップの現在状態を把握 (`list_desktop`)
3. `/ene{desktop_action}` — 操作を実行
4. `V:{/dia-}` — 結果を軽量検証
5. `/dox-` — 操作結果を記録

## Tauri コマンド対応

| 操作 | CCL 記法 | Tauri コマンド |
|:-----|:---------|:--------------|
| 要素一覧 | `@desktop{list}` | `list_desktop` |
| ツリー取得 | `@desktop{tree, app="appname"}` | `get_element_tree` |
| クリック | `@desktop{click, x=100, y=200}` | `desktop_click` |
| テキスト入力 | `@desktop{type, text="hello"}` | `desktop_type` |
| スクリーンショット | `@desktop{screenshot}` | `desktop_screenshot` |

## 使用例

```ccl
@desktop{list}                           # デスクトップ要素一覧
@desktop{tree, app="firefox"}            # Firefox のツリー取得
@desktop{click, x=500, y=300}            # 座標クリック
@desktop{type, text="search query"}      # テキスト入力
@desktop{screenshot}                     # スクリーンショット取得
```

## ルーティング判定

```
操作リクエスト
  ├─ AT-SPI bus_name あり → A パス (構造化操作, 無料, 高速)
  ├─ AT-SPI bus_name なし + 座標あり → B パス (Bytebot VLM)
  └─ screenshot → 常時 B パス
```
