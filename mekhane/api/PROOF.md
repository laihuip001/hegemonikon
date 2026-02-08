# PROOF.md — mekhane/api/

## 存在証明

- **Level**: L2/インフラ
- **Parent**: mekhane/
- **Axiom**: A0 → Hegemonikón の機能は外部から利用可能であるべき
- **Derivation**: A0 → 利用可能性 → REST API → FastAPI バックエンド

## PURPOSE

mekhane 配下の各モジュール（FEP, Gnōsis, Peira, Dendron, Postcheck）を
REST API として公開し、Tauri v2 デスクトップアプリから利用可能にする。

## REASON

「ツールは使われてこそ価値がある。見えないものは存在しないのと同じ」
（handoff_2026-02-08_1856 法則化 #1: 顔の法則）

## 構成

| ファイル | 役割 |
|:---|:---|
| `__init__.py` | パッケージ定義・定数 |
| `server.py` | FastAPI アプリ・CORS・ルーター登録 |
| `routes/status.py` | /api/status/* |
| `routes/fep.py` | /api/fep/* |
| `routes/gnosis.py` | /api/gnosis/* |
| `routes/postcheck.py` | /api/postcheck/* |
| `routes/dendron.py` | /api/dendron/* |
| `tests/test_api.py` | TestClient テスト |
