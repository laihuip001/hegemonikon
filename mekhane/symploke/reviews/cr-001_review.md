# LGTM拒否者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Critical (Dead Code)**: `_load_projects` (60行) および `_load_skills` (50行) が定義されているが、`get_boot_context` 内で `mekhane.symploke.boot_axes` から同名の関数を import しているため、これらは完全にバイパスされており一度も実行されない。
- **Critical (Unused Global State)**: `THEOREM_REGISTRY` (30行超) および `SERIES_INFO` が定義されているが、コード内で一切参照されていない。認知負荷を増大させるだけの死蔵コードである。
- **High (Source of Truth Violation)**: `THEOREM_REGISTRY` 内の定義が `AGENTS.md` (v5.0) の定義と矛盾している（例: S1 Metron vs Hermēneia, K series 全体）。これは「信頼できる唯一の情報源」の原則に違反し、混乱を招く。
- **Medium (Hidden Side Effects)**: `get_boot_context` は名前からして「取得 (get)」を行う関数であるべきだが、内部で `localhost:5678` (n8n) への Webhook 送信を行っている。Getter は副作用を持つべきではない（Command-Query Separation 違反）。
- **Medium (Global Warning Suppression)**: `main` 関数内で `warnings.filterwarnings("ignore")` を実行しており、全警告を無差別に抑制している。これにより重要な DeprecationWarning や RuntimeWarning が隠蔽される恐れがある。

## 重大度
Critical
