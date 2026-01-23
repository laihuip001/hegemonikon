# Forge モジュール検証テストフレームワーク

## 概要

このフレームワークは、Forgeのプロンプトモジュールが期待通りに動作するかを
検証するためのテストスイートです。

## テスト方法

### 1. 構文テスト (Syntax Test)
モジュールファイルが正しい形式で記述されているかを確認します。

```powershell
.\test-forge.ps1 syntax
```

チェック項目:
- ファイルが存在する
- UTF-8エンコーディング
- 必須セクションの存在（title, instruction等）

### 2. 完全性テスト (Completeness Test)
モジュールが必要な要素を全て含んでいるかを確認します。

```powershell
.\test-forge.ps1 completeness
```

チェック項目:
- メタデータの存在
- 説明文の存在
- 出力フォーマットの定義

### 3. 参照テスト (Reference Test)
モジュール間の参照が正しいかを確認します。

```powershell
.\test-forge.ps1 reference
```

チェック項目:
- 参照先モジュールの存在
- 循環参照の検出

## テスト結果

テスト結果は `test-results/` ディレクトリに出力されます。

```
test-results/
├── syntax-report.json
├── completeness-report.json
└── reference-report.json
```

## 実行例

```powershell
# 全テスト実行
.\test-forge.ps1 all

# 特定カテゴリのみ
.\test-forge.ps1 syntax -category protocols
```
