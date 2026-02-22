# コード/コメント矛盾検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **軸の数の不一致 (High)**
    - コメント: `get_boot_context` の docstring に「12軸を統合して返す」とある。
    - コード: 実際には `boot_axes.py` から 14以上のローダー (A-N, plus others) を呼び出しており、`boot_axes.py` には 16 の軸が定義されている。コメントが実装に追従していない。
- **テンプレート生成のモード矛盾 (Medium)**
    - コメント: `generate_boot_template` の docstring に「モード別の穴埋めテンプレートを生成する」とある。
    - コード: `reqs = MODE_REQUIREMENTS.get("detailed", {})` とハードコードされており、引数 `result` の内容に関わらず常に `detailed` モードの要件を使用している。関数シグネチャにも `mode` 引数が存在しない。
- **THEOREM_REGISTRY の参照可能性 (Medium)**
    - コメント: `THEOREM_REGISTRY` に「Boot 時に明示的に参照可能にする」および `TheoremAttractor + THEOREM_REGISTRY 経由で Boot 時にアクセス可能` とある。
    - コード: `THEOREM_REGISTRY` は定義されているだけで、`get_boot_context` や `print_boot_summary` からは参照されておらず、外部へのエクスポートも明示されていない（`__all__` なし）。実質的にデッドコード状態であり、Boot 時にアクセス可能という記述と矛盾する。
- **ローダー関数の役割矛盾 (Low)**
    - コメント: `_load_projects`, `_load_skills` はローカルで定義され、docstring には Boot 時のロード処理を行う旨が記載されている。
    - コード: `get_boot_context` 内では `from mekhane.symploke.boot_axes import load_projects` のように外部モジュールからインポートして使用しており、ローカル定義の関数は直接使用されていない（`boot_axes` が逆にこれをインポートする循環構造になっている）。

## 重大度
High
