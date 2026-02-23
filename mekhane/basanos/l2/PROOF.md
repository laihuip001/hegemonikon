# l2/

> 評議会 — 多角的批評エンジンの「l2」サブモジュール

## 構成

- **__init__.py** — L2 問い生成機構 — 構造的差分検出によるズレの発見
- **cli.py** — Basanos L2 問い生成 CLI — deficit 検出→問い生成→優先度表示
- **deficit_factories.py** — 3種の deficit (η, ε, Δε/Δt) を検出するファクトリ群
- **g_semantic.py** — G_semantic — LLM で HGK 専門用語を一般学術用語に翻訳する
- **g_struct.py** — kernel/ MD ファイルから HGK 概念を機械的に抽出する構造パーサー
- **history.py** — Basanos L2 deficit 履歴の永続化 — JSONL 形式で時系列追跡
- **hom.py** — Hom 計算 — 3段階の関連性尺度で随伴条件の「破れ」を測定する
- **models.py** — L2 問い生成のコアデータモデル — deficit と question の型定義
- **resolver.py** — Basanos L3 自動解決ループ — deficit→問い→解決策の自動生成
- `tests/`
