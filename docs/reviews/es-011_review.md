# 燃え尽き症候群リスク検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **ビジネスロジックとの密結合 (Tight Coupling):**
  `synedrion_review` メソッドが `mekhane.ergasterion.synedrion` パッケージ（ビジネスロジック層）に直接依存しており、動的インポートを行っている。
  これにより、汎用APIクライアントであるはずのコンポーネントが、特定のビジネスルール（Synedrion v2.1）の変更影響を直接受ける構造になっている。これは開発者がインフラ層のコードを触る際にビジネス層の深い文脈理解を強いられるため、認知負荷が高く、保守時の燃え尽きリスクを高める。

- **並行処理制御の分散 (Scattered Concurrency Logic):**
  並行処理のリミット管理がコンストラクタ（`MAX_CONCURRENT`）、`batch_execute` メソッド、および `synedrion_review` メソッドに分散している。さらに `_global_semaphore` とローカルセマフォの使い分けが必要になっており、システム全体の負荷挙動を予測・制御するためのメンタルモデル構築が困難である。

- **手動による状態管理の負担 (Manual State Maintenance):**
  `SessionState` Enum がAPIのステータス文字列にハードコードされており、未知の状態（`UNKNOWN`）へのフォールバック処理はログ監視と手動更新に依存している。
  これはAPIの仕様変更への追随を常に開発者の注意（監視・手動修正）に依存させる形となり、Toil（労苦）を生み出しやすい。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
