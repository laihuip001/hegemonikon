# Project Autophōnos (αὐτόφωνος)

> **「自ら語る」— データが主体的に価値を提案する機構**

---

## ステータス

| フェーズ | 状態 |
|:---------|:-----|
| Phase 0: 立ち上げ | ✅ 完了 |
| Phase 1: PKS (Pull→Push 反転) | ✅ 完了 (v2.1) |
| Phase 2: SelfAdvocate (一人称語りかけ) | ✅ 完了 (v3) |
| Phase 3: Gateway 統合 | 🔄 進行中 |

---

## 概要

従来の知識ベースは **Pull 型** — ユーザーが問いかけない限り沈黙する。
Autophōnos は **Push 型** — データが自らの価値を認識し、一人称で語りかける。

```
従来:       User → Query → DB → Result
PKS:        DB → Context Detection → Benefit Proposal → User
Autophōnos: DB → Context Detection → 📄「私があなたを助けられます」 → User
```

---

## 思想的基盤

- **FEP (Active Inference)**: 認知システムは受動的に刺激を待つのでなく、能動的に環境をサンプリングする
- **Autophōnos の具現化**: 知識ベースが Active Inference エージェントとして振る舞う
- **文鎮問題の解決**: 762件の論文が「呼ばれるまで沈黙」→「必要なタイミングで語りかける」

詳細: [philosophy.md](docs/philosophy.md)

---

## アーキテクチャ

実装は `mekhane/pks/` に配置。16ファイル、4,100行超。

```
┌─────────────────── Autophōnos / PKS ───────────────────┐
│                                                         │
│  ┌─────────────────┐   ┌────────────────────────────┐  │
│  │  ContextTracker  │──▶│    RelevanceDetector       │  │
│  │  (文脈検出)       │   │    (関連度評価)             │  │
│  └─────────────────┘   └────────────┬───────────────┘  │
│                                      │                   │
│  ┌─────────────────┐   ┌────────────▼───────────────┐  │
│  │  GnosisIndex     │──▶│    PushController          │  │
│  │  (ベクトル検索)   │   │    (プッシュ制御)           │  │
│  └─────────────────┘   └────────────┬───────────────┘  │
│                                      │                   │
│  ┌─────────────────┐   ┌────────────▼───────────────┐  │
│  │  SelfAdvocate 🆕 │──▶│    PKSNarrator            │  │
│  │  (一人称語り)     │   │    (対話形式変換)           │  │
│  └─────────────────┘   └───────────────────────────┘  │
│                                                         │
│  補助: SerendipityScorer, FeedbackCollector,            │
│        LinkEngine, SyncWatcher, MatrixView               │
└─────────────────────────────────────────────────────────┘
```

### 主要ファイル

| ファイル | 行数 | 役割 |
|:---------|-----:|:-----|
| `pks_engine.py` | 900 | コアエンジン: Nugget/Context/Push |
| `narrator.py` | 585 | 多フォーマット対話生成 |
| `self_advocate.py` | 210 | 🆕 一人称メッセージ生成 |
| `pks_cli.py` | 380 | CLIインターフェース |
| `links/link_engine.py` | 318 | 引用グラフ |
| `sync_watcher.py` | 290 | ファイル変更監視 |
| `matrix_view.py` | 279 | マトリクスビュー |
| `llm_client.py` | 84 | Gemini共通クライアント |
| `feedback.py` | 138 | フィードバック学習 |

---

## 使い方

```bash
# 能動的プッシュ
cd ~/oikos/hegemonikon
.venv/bin/python mekhane/pks/pks_cli.py push --topics FEP,CCL

# 一人称モード (Autophōnos)
.venv/bin/python -c "
from mekhane.pks.pks_engine import PKSEngine
engine = PKSEngine()
engine.set_context(topics=['FEP'])
nuggets = engine.proactive_push()
print(engine.format_push_report(nuggets, use_advocacy=True))
"
```

---

## 関連

- [設計詳細](docs/design.md)
- [思想的背景](docs/philosophy.md)
- `mekhane/pks/` — 実装
- `mekhane/anamnesis/` — GnosisIndex (ベクトル検索基盤)
