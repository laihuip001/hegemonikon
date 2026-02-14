# PROOF.md — Hegemonikón Desktop App

## 存在目的 (EPT)

**なぜこのアプリが存在するか**: Hegemonikón フレームワークの知識・分析・監視機能を
Creator が日常的にアクセスできる GUI として提供する。CLI / IDE 依存を脱却し、
認知ハイパーバイザーの全機能を統合的に操作可能にする。

## 必要性の証明

| 代替手段 | 不足点 |
|:---------|:-------|
| CLI のみ | 視覚化不可、3D グラフ不可、同時操作困難 |
| Web ブラウザ | ネイティブ a11y 不可、AT-SPI 統合不可 |
| IDE 内表示 | IDE 依存、IDE なしで使用不可 |

## 依存する PJ

| PJ | 用途 | 必須度 |
|:---|:-----|:-------|
| mekhane/api/ | 全データ取得 (FastAPI UDS) | 必須 |
| mekhane/synteleia/ | 認知アンサンブル監査 | View 依存 |
| mekhane/anamnesis/ | ベクトル検索 | View 依存 |
| mekhane/mcp/ | Gnōsis MCP | View 依存 |

## 依存される PJ

なし (末端の消費者)

## テスト戦略

| 種類 | 方法 |
|:-----|:-----|
| 起動テスト | `npm run tauri dev` で起動確認 |
| API 接続 | `/api/status` エンドポイント確認 |
| View 描画 | ブラウザ / Tauri WebView で各 view の描画確認 |
| a11y | AT-SPI ツリー取得コマンドの動作確認 |

## 変更履歴

| 日付 | 変更 |
|:-----|:-----|
| 2026-02-14 | 初版作成 (17 views, Rust a11y backend) |
