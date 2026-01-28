# WARGAME_DB Reference

**Source:** OMEGA v8.0.1

歴史的失敗パターンのシミュレーションDB。Pre-Mortem時に参照。

---

## 1. Thundering Herd (雷鳴の群れ)

**Scenario:** キャッシュ無効化時に全クライアントが同時にバックエンドを叩く

```
SYMPTOMS:
- 突然のレイテンシスパイク
- バックエンドCPU飽和
- 連鎖的タイムアウト

ROOT_CAUSE:
- 同一TTLでのキャッシュ設定
- リトライロジックの即時再実行

PREVENTION:
- Staggered expiry (TTL ± random jitter)
- Circuit breaker pattern
- Exponential backoff with jitter

DETECTION:
- 同時リクエスト数の急増監視
- キャッシュヒット率の急落アラート
```

---

## 2. Distributed Race Condition (分散競合状態)

**Scenario:** 複数ノードが同一リソースを同時更新

```
SYMPTOMS:
- データ不整合
- "幽霊"レコードの出現
- 間欠的な処理失敗

ROOT_CAUSE:
- 楽観的ロックの不在
- トランザクション境界の誤設計

PREVENTION:
- Distributed lock (Redis/Zookeeper)
- Optimistic locking with version column
- Idempotency keys

DETECTION:
- バージョン競合ログ監視
- 整合性チェックバッチ
```

---

## 3. N+1 Query Problem (N+1クエリ問題)

**Scenario:** ループ内で関連データを個別取得

```
SYMPTOMS:
- レイテンシがデータ量に比例
- DB接続プール枯渇
- スロークエリログ大量発生

ROOT_CAUSE:
- ORM自動生成クエリの盲信
- リレーション設計の不備

PREVENTION:
- Eager loading / JOIN FETCH
- DataLoader pattern (GraphQL)
- クエリ数監視 in development

DETECTION:
- クエリカウントアサーション
- APMツールでのDB呼び出し追跡
```

---

## 4. Supply Chain Poison (サプライチェーン汚染)

**Scenario:** 依存パッケージへの悪意あるコード注入

```
SYMPTOMS:
- 意図しない外部通信
- 環境変数の窃取
- ビルド時の不審な挙動

ROOT_CAUSE:
- 未固定バージョン指定
- 依存関係の監査不足
- Typosquatting

PREVENTION:
- Lockfile必須 + 定期監査
- Dependabot / Renovate
- Private registry / mirror

DETECTION:
- SCA (Software Composition Analysis)
- ネットワークトラフィック監視
```

---

## 5. Unbounded Queue (無制限キュー)

**Scenario:** 消費速度を超える生産でメモリ枯渇

```
SYMPTOMS:
- メモリ使用量の単調増加
- OOM Kill
- 処理遅延の累積

ROOT_CAUSE:
- Rate limiting不在
- Backpressure未実装
- 無制限バッファ設計

PREVENTION:
- Bounded queue with rejection
- Backpressure propagation
- Consumer scaling (auto)

DETECTION:
- キュー深度監視
- メモリ使用量アラート
```

---

## 6. Cascade Failure (連鎖障害)

**Scenario:** 1サービス障害が全体を巻き込む

```
SYMPTOMS:
- タイムアウトの伝播
- リソース枯渇の連鎖
- 全システムダウン

ROOT_CAUSE:
- 同期的な依存関係
- Circuit breaker不在
- タイムアウト設定の不整合

PREVENTION:
- Bulkhead pattern
- Circuit breaker (Hystrix/Resilience4j)
- Graceful degradation設計

DETECTION:
- 分散トレーシング
- 依存関係ヘルスチェック
```

---

## 7. Cold Start Amplification (コールドスタート増幅)

**Scenario:** スケールアウト時に新インスタンスが負荷で死亡

```
SYMPTOMS:
- スケールアウトが効かない
- 新インスタンス即死
- 負のフィードバックループ

ROOT_CAUSE:
- ウォームアップ不足
- ヘルスチェックの即時成功
- JIT未完了での本番トラフィック

PREVENTION:
- Readiness probe分離
- Pre-warming mechanism
- Gradual traffic shifting

DETECTION:
- 新インスタンスエラー率監視
- 起動時間追跡
```

---

## 8. Secret Sprawl (機密情報拡散)

**Scenario:** 認証情報がコード/ログ/履歴に漏洩

```
SYMPTOMS:
- Git履歴にAPI Key
- ログに平文パスワード
- コンテナイメージに埋め込み

ROOT_CAUSE:
- 環境変数の誤用
- 構造化ログの設計不備
- .gitignore漏れ

PREVENTION:
- Secret manager (Vault/AWS SM)
- Pre-commit hook (detect-secrets)
- Log sanitization

DETECTION:
- Git履歴スキャン
- ログ監査
```

---

## 9. Time Zone Hell (タイムゾーン地獄)

**Scenario:** 日時処理の不整合でデータ破損

```
SYMPTOMS:
- 予約が1時間ずれる
- DST切り替えでの重複/欠落
- レポートの日付不一致

ROOT_CAUSE:
- ローカル時間での保存
- タイムゾーン変換の多重適用
- DST考慮不足

PREVENTION:
- UTC統一保存
- タイムゾーン明示 (ISO 8601)
- Chrono/date-fns等の堅牢なライブラリ

DETECTION:
- DST境界テスト
- 多地域E2Eテスト
```

---

## 10. Configuration Drift (構成ドリフト)

**Scenario:** 環境間で設定が乖離し、本番のみ障害

```
SYMPTOMS:
- 「ローカルでは動く」
- 環境依存のバグ
- デプロイ後の予期せぬ挙動

ROOT_CAUSE:
- 手動設定変更
- IaC適用の不徹底
- 環境変数のシャドーイング

PREVENTION:
- IaC必須 (Terraform/Pulumi)
- Drift detection自動化
- Immutable infrastructure

DETECTION:
- 定期的なdiffチェック
- デプロイ前の構成比較
```

---

## Usage in Pre-Mortem

```python
def wargame_check(design):
    vulnerabilities = []
    
    for scenario in WARGAME_DB:
        if design.matches_pattern(scenario.root_cause):
            vulnerabilities.append({
                "scenario": scenario.name,
                "risk": scenario.symptoms,
                "mitigation": scenario.prevention
            })
    
    return vulnerabilities
```

---

## Severity Matrix

| Scenario | Impact | Likelihood | Priority |
|:---|:---:|:---:|:---:|
| Supply Chain Poison | Critical | Medium | P0 |
| Cascade Failure | Critical | Medium | P0 |
| Thundering Herd | High | High | P1 |
| Unbounded Queue | High | Medium | P1 |
| Distributed Race | High | Medium | P1 |
| N+1 Query | Medium | High | P2 |
| Secret Sprawl | Critical | Low | P2 |
| Cold Start Amplification | Medium | Medium | P2 |
| Time Zone Hell | Medium | Medium | P3 |
| Configuration Drift | Medium | High | P3 |

---

## 11. Prompt Injection (プロンプト注入)

**Scenario:** ユーザー入力が LLM の指示として解釈される

```
SYMPTOMS:
- システム指示の無視
- 意図しない情報開示
- 制御フローのハイジャック

ROOT_CAUSE:
- 入力のサニタイズ不足
- システム/ユーザー境界の曖昧さ
- 指示とデータの混在

PREVENTION:
- 入力を明示的にエスケープ
- Structured output 強制
- Guardrails / Filtering レイヤー

DETECTION:
- 出力の異常検知
- レッドチームテスト
```

---

## 12. Token Explosion (トークン爆発)

**Scenario:** 予期せぬ長文生成でコスト/レイテンシ暴走

```
SYMPTOMS:
- API課金の急増
- タイムアウト多発
- 応答品質の低下

ROOT_CAUSE:
- max_tokens 未設定
- 繰り返し生成の検知不足
- 再帰的プロンプトパターン

PREVENTION:
- max_tokens 必須設定
- 出力長監視 + 早期終了
- 繰り返し検知ロジック

DETECTION:
- トークン消費ダッシュボード
- 異常検知アラート
```

---

## 13. Hallucination Cascade (幻覚連鎖)

**Scenario:** 1つの幻覚が後続の推論を汚染

```
SYMPTOMS:
- もっともらしいが誤った回答
- 引用元が存在しない
- 論理に破綻がないが事実が誤り

ROOT_CAUSE:
- 検証ステップの欠如
- RAG未適用または設計不備
- 過度な自信表現

PREVENTION:
- ソース引用強制
- 確信度表示義務化
- RAG + Fact-checking パイプライン

DETECTION:
- 他モデルでのクロス検証
- 既知事実との照合テスト
```

---

## 14. Model Drift (モデルドリフト)

**Scenario:** モデル更新で既存プロンプトの動作変化

```
SYMPTOMS:
- 昨日動いていたプロンプトが動かない
- 出力フォーマットの微妙な変化
- 性能の予期せぬ低下/変化

ROOT_CAUSE:
- モデルバージョン固定なし
- 脆弱なプロンプト設計
- 回帰テストの欠如

PREVENTION:
- モデルバージョン明示
- 堅牢なプロンプト設計
- 自動回帰テストスイート

DETECTION:
- 定期的なベンチマーク実行
- 出力差分監視
```

---

## 15. Context Window Overflow (コンテキスト溢れ)

**Scenario:** 入力+履歴がコンテキスト長を超過

```
SYMPTOMS:
- 古い文脈の忘却
- 回答の一貫性欠如
- 突然のエラー/切詰め

ROOT_CAUSE:
- 動的な履歴管理の不在
- 長文入力の制限なし
- 要約/圧縮戦略の欠如

PREVENTION:
- トークン数事前計算
- 履歴の自動要約/剪定
- Sliding window実装

DETECTION:
- 入力トークン数監視
- 文脈保持テスト
```

---

## Severity Matrix (Updated)

| Scenario | Impact | Likelihood | Priority |
|:---|:---:|:---:|:---:|
| Supply Chain Poison | Critical | Medium | P0 |
| Cascade Failure | Critical | Medium | P0 |
| **Prompt Injection** | **Critical** | **High** | **P0** |
| Thundering Herd | High | High | P1 |
| Unbounded Queue | High | Medium | P1 |
| Distributed Race | High | Medium | P1 |
| **Hallucination Cascade** | **High** | **High** | **P1** |
| N+1 Query | Medium | High | P2 |
| Secret Sprawl | Critical | Low | P2 |
| Cold Start Amplification | Medium | Medium | P2 |
| **Token Explosion** | **Medium** | **High** | **P2** |
| Time Zone Hell | Medium | Medium | P3 |
| Configuration Drift | Medium | High | P3 |
| **Model Drift** | **Medium** | **Medium** | **P3** |
| **Context Window Overflow** | **Medium** | **Medium** | **P3** |
