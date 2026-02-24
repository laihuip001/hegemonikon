# LGTM拒否者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項

- **Dead Code (High)**: `THEOREM_REGISTRY` および `SERIES_INFO` は定義されていますが、モジュール内のロジックでは一切使用されていません（`test_theorem_registry.py` でのみ参照）。不要なグローバル状態が維持されています。
- **Source of Truth Violation (Critical)**: `THEOREM_REGISTRY` 内の定理定義がレガシー（v1/v3時代）のまま放置されています。
    - S1: `Metron` (Legacy) vs `Hermēneia` (v5.0 `AGENTS.md`)
    - S3: `Stathmos` (Legacy) vs `Chronos` (v5.0 `AGENTS.md`)
    - P2: `Hodos` (Legacy) vs `Telos` (v5.0 `AGENTS.md`)
    - P3: `Trokhia` (Legacy) vs `Eukairia` (v5.0 `AGENTS.md` — K1から移動)
    - K1: `Eukairia` (Legacy) vs `Taksis` (v5.0 `AGENTS.md`)
    この定義乖離は `AGENTS.md` を正とするプロジェクト規約に違反しています。
- **Circular Dependency / Architecture Flaw (Medium)**: `_load_projects` と `_load_skills` がこのファイルで定義されていますが、`boot_axes.py` にインポートされ、さらに `boot_axes.py` のラッパー関数を通してこのファイルに再インポートされています。リファクタリングが中途半端で、依存関係が循環しています。
- **Hidden Side Effects (High)**: `get_boot_context` 内で `urllib.request.urlopen` を使用して `localhost:5678` (n8n) へのネットワーク通信を行っています。Getter 関数に副作用（I/O）が隠蔽されており、テスト容易性と予測可能性を損なっています。
- **Global Warning Suppression (Medium)**: `main()` 関数内で `warnings.filterwarnings("ignore")` を使用しており、潜在的な問題を隠蔽しています。

## 重大度
Critical
