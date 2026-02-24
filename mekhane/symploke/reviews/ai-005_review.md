# コード/コメント矛盾検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- **軸数の不一致 (High)**
  - ファイル先頭の docstring は「13軸」と記述されている。
  - `get_boot_context` の docstring は「12軸」と記述されている。
  - 実装は A-N の14項目以上 (Handoff, Sophia, Persona, PKS, Safety, EPT, Digestor, Attractor, Projects, Skills, Doxa, Feedback, Proactive Push, Ideas) をロードしており、コメントとコードが乖離している。

- **`generate_boot_template` の機能過大広告 (High)**
  - docstring は「モード別の穴埋めテンプレートを生成する」と謳っているが、実装は `detailed` モードの要件をハードコードしており (`MODE_REQUIREMENTS.get("detailed", {})`)、引数でモードを受け取る設計にもなっていない。

- **`THEOREM_REGISTRY` の定義矛盾と未使用 (High)**
  - `# PURPOSE` に「Boot 時に明示的に参照可能にする」とあるが、コード内で一切参照されていない（デッドコード）。
  - 定義内容が古い (v1/v3 名称: Metron, Stathmos, Hodos, Trokhia) ままになっており、現在の `AGENTS.md` v5.0 (Hermēneia, Chronos, Telos, Eukairia) と矛盾している。

- **ローカル関数とインポートの競合 (High)**
  - `_load_projects` および `_load_skills` が定義され、docstring で動作を説明しているが、`get_boot_context` 内では `mekhane.symploke.boot_axes` から同名関数 (`load_projects`, `load_skills`) をインポートして使用している。
  - ローカル関数は実行されず、コメントの説明（「全文プリロード済み」など）が実際の実装と一致しているか保証がない。

## 重大度
High
