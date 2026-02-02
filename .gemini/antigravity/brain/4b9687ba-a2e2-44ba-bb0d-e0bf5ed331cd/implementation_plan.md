# Flow AI → Hegemonikón Recast

> **目標**: Flow AI を Hegemonikón の語彙で 0 から再構築する
> **哲学**: 「既存コードを消化し、Hegemonikón の系で再生成する」

---

## 背景

Flow AI は「テキスト下処理ツール」として開発された具体的ソフトウェア。
本計画は、Flow AI の全コンポーネントを Hegemonikón の定理・語彙で再定義し、
**「最初から Hegemonikón で設計されていたら」** という形に再構築する。

---

## コンポーネントマッピング

> **定理 → コード** の対応表

| Flow AI (現行) | Hegemonikón (新) | 定理基盤 | 説明 |
|:---------------|:-----------------|:---------|:-----|
| `SeasoningManager` | `MetronResolver` | **S1 Metron** | 連続値→離散段階への尺度解決 |
| `PrivacyHandler` | `EpocheShield` | **A2 Krisis (Epochē)** | 判断保留状態での外部通信 |
| `CoreProcessor` | `EnergeiaCoreResolver` | **O4 Energeia** | 意志→現実化の統一行動層 |
| `CostRouter` | `EukairiaRouter` | **K1 Eukairia** | 「今が好機か」のモデル選択 |
| `CacheManager` | `DoxaCache` | **H4 Doxa** | 信念（結果）の永続化 |
| `AuditLogger` | `TealsAnamnesis` | **H3 Orexis + H4** | 欲求の記録と永続化 |
| `SyncJob` | `ChronosPendingTask` | **K2 Chronos** | 時間制約への対応 |

---

## 名前変換表（詳細）

### ファイル名

| 現行 | 新規 |
|:-----|:-----|
| `src/core/seasoning.py` | `src/mekhane/metron_resolver.py` |
| `src/core/privacy.py` | `src/mekhane/epoche_shield.py` |
| `src/core/processor.py` | `src/mekhane/energeia_core.py` |
| `src/core/cache.py` | `src/mneme/doxa_cache.py` |
| `src/core/audit_logger.py` | `src/mneme/teals_anamnesis.py` |
| `src/core/sync.py` | `src/mekhane/chronos_sync.py` |
| `src/core/config.py` | `src/config/settings.py` |
| `src/core/gemini.py` | `src/api/gemini_client.py` |

### クラス名

| 現行 | 新規 | 定理 |
|:-----|:-----|:-----|
| `SeasoningManager` | `MetronResolver` | S1 |
| `PrivacyScanner` | `EpocheScanner` | A2 |
| `PrivacyHandler` | `EpocheShield` | A2 |
| `CoreProcessor` | `EnergeiaCoreResolver` | O4 |
| `CacheManager` | `DoxaCache` | H4 |
| `AuditLogger` | `AnamnesisTEALS` | H3/H4 |
| `SyncJob` | `ChronosPendingTask` | K2 |
| `GeminiClient` | `NousisClient` | O1 |

### 定数名

| 現行 | 新規 | 理由 |
|:-----|:-----|:-----|
| `UMAMI_THRESHOLD` | `METRON_DEEP_THRESHOLD` | Seasoning終了 |
| `LONG_TEXT_THRESHOLD` | `NOUS_COMPLEXITY_THRESHOLD` | O1関連 |
| `LIGHT_MAX` | `METRON_LIGHT` | S1関連 |
| `MEDIUM_MAX` | `METRON_MEDIUM` | S1関連 |
| `RICH_MAX` | `METRON_RICH` | S1関連 |

---

## ディレクトリ構造

> **原則**: 既存の Hegemonikón 構造に統合。別リポジトリは作らない。

```text
hegemonikon/mekhane/ergasterion/
├── digestor/         # 既存
├── factory/          # 既存
├── helpers/          # 既存
├── prompt-lang/      # 既存
├── protocols/        # 既存
├── synedrion/        # 既存
├── tekhne/           # 既存
│
└── flow/             # 🆕 Flow AI 統合モジュール
    ├── __init__.py
    ├── energeia_core.py     # O4: 中枢ロジック
    ├── metron_resolver.py   # S1: 尺度解決
    ├── epoche_shield.py     # A2: PII保護
    ├── chronos_sync.py      # K2: 遅延同期
    ├── eukairia_router.py   # K1: モデル選択
    ├── doxa_cache.py        # H4: キャッシュ
    ├── anamnesis_teals.py   # H3/H4: 監査ログ
    ├── noesis_client.py     # O1: Gemini接続
    └── tests/
        └── ...
```

### 統合のメリット

1. **「美しさ」の維持**: Hegemonikón の一部として自然に存在
2. **共有リソース**: 既存の FEP、anamnesis、symploke と連携可能
3. **単一リポジトリ**: oikos 配下で一元管理

---

## 段階的実装計画

### Phase 1: 設計ドキュメント（今セッション）

| # | タスク | 方法 |
|:--|:-------|:-----|
| 1.1 | マッピング表の確定 | 本計画書 |
| 1.2 | ARCHITECTURE_HEGEMONIKON.md 作成 | 手動 |
| 1.3 | ユーザーレビュー | `/notify_user` |

### Phase 2: コア変換（Jules API）

| # | タスク | 方法 |
|:--|:-------|:-----|
| 2.1 | `seasoning.py` → `metron_resolver.py` | Jules |
| 2.2 | `privacy.py` → `epoche_shield.py` | Jules |
| 2.3 | `processor.py` → `energeia_core.py` | Jules |

### Phase 3: 記憶層変換

| # | タスク | 方法 |
|:--|:-------|:-----|
| 3.1 | `cache.py` → `doxa_cache.py` | Jules |
| 3.2 | `audit_logger.py` → `anamnesis_teals.py` | Jules |

### Phase 4: 検証

| # | タスク | 方法 |
|:--|:-------|:-----|
| 4.1 | 既存テストの変換・実行 | pytest |
| 4.2 | `/vet` で Jules Review | Jules API |

---

## 検証計画

### 既存テスト

```bash
# Flow AI の既存テストを確認
ls -la /tmp/flow-recast/tests/
# テスト実行（変換後）
cd /tmp/flow-recast && python -m pytest tests/ -v
```

### 変換後の検証ポイント

1. **機能等価性**: 変換前後で同一入力に対し同一出力
2. **命名一貫性**: 全ファイル/クラス/関数が Hegemonikón 語彙
3. **哲学的整合性**: 各コンポーネントが対応定理の責務を果たす

### 手動検証

1. `MetronResolver.resolve_level(50)` → `60` (MEDIUM) を確認
2. `EpocheShield.mask("test@example.com")` → `[PII_0]` を確認
3. `EnergeiaCoreResolver.process(...)` → 正常な出力を確認

---

## User Review Required

> [!IMPORTANT]
> この計画は Flow AI の既存コードを **破壊的に変更** します。
> 変換後は「Flow AI」ではなく「**Flow Hegemonikón**」として再生成されます。

**確認事項**:

1. ✅ マッピング表は適切か？
2. ✅ 名前変換は直感的か？
3. ✅ ディレクトリ構造は Hegemonikón と整合しているか？
4. ✅ 段階的実装の順序は妥当か？

---

*Created: 2026-01-29 13:10*
