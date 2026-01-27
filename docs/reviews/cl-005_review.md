# 専門家レビュー: 事前知識査定 (cl-005)

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 概要
本ファイルは Google Jules API と対話するための非同期クライアントライブラリです。セッションの作成、ポーリングによる状態監視、および並行実行制御を実装しています。本コードを正確に理解・保守するために必要な事前知識を以下に定義します。

## 必須となる事前知識

### 1. Python 言語仕様 (Modern Python)
*   **型ヒント (Type Hints):** `typing.Optional`, `list[dict]` (Generic Alias), `dataclasses.dataclass` の理解。
*   **列挙型 (Enum):** `enum.Enum` を使用したステート管理 (`SessionState`) の理解。
*   **例外処理:** カスタム例外 (`RateLimitError`) の定義と送出、`try-except` ブロックによる制御。

### 2. 非同期プログラミング (Asynchronous Programming)
*   **asyncio:** イベントループ、コルーチン (`async def`), `await` 構文の基礎。
*   **並行処理制御:** `asyncio.gather` によるタスクの並列実行。
*   **同期プリミティブ:** `asyncio.Semaphore` を使用した同時実行数の制限 (Throttling) の仕組み。
*   **ノンブロッキングI/O:** `asyncio.sleep` を用いた待機処理 (ブロッキングな `time.sleep` との違い)。

### 3. Web API / HTTP プロトコル
*   **RESTful API の概念:** リソース指向アーキテクチャ、HTTPメソッド (GET, POST)。
*   **HTTP ステータスコード:** `429 Too Many Requests` (レートリミット), `200 OK` 等の意味。
*   **HTTP ヘッダー:** 認証 (`X-Goog-Api-Key`) や Content-Type の役割。
*   **JSON:** ペイロードの構築とレスポンスのパース。

### 4. 使用ライブラリ: aiohttp
*   **ClientSession:** 非同期 HTTP クライアントのライフサイクル管理 (コンテキストマネージャ `async with`)。
*   **レスポンス処理:** `resp.json()`, `resp.raise_for_status()` の挙動。

### 5. 設計パターン・アルゴリズム
*   **ポーリング (Polling):** `poll_session` メソッドに見られる、完了まで定期的リクエストを送るパターン。
*   **Exponential Backoff (指数バックオフ):** レートリミット発生時に待機時間を指数関数的に増加させるアルゴリズム (`backoff * 2`)。
*   **DTO (Data Transfer Object):** `dataclass` を用いたデータ構造の定義。

## 推奨されるドメイン知識
*   **CI/CD & Git:** ペイロードに含まれる `branch`, `pullRequest` などの概念理解。
*   **Google Cloud API (General):** 一般的な Google API の認証スキームやエラーレスポンス形式への慣れ。

---
作成者: Jules (AI Agent)
日付: 2025-05-21
