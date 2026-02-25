# LGTM拒否者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項

### Critical (重大)
1.  **Global Warning Suppression**: `main()` 関数冒頭の `warnings.filterwarnings("ignore")` は、問題を解決せず隠蔽する行為である。「臭いものに蓋」であり、将来的な非推奨エラーや重要な警告を見逃す原因となる。LGTMできない。
2.  **Dead Code / Test-Only Artifacts**: `THEOREM_REGISTRY` と `SERIES_INFO` は、このファイル内では未使用であり、検索結果によるとテストコード (`test_theorem_registry.py` 等) からしか参照されていない。プロダクションコードがテストのために存在する「尻尾が犬を振る」状態である。これらが外部 API として意図されているなら、専用の `registry.py` に移動すべきである。

### High (高)
3.  **Broad Exception Swallowing**: `extract_dispatch_info`, `_load_projects`, `_load_skills`, `get_boot_context`, `print_boot_summary` のすべてにおいて `except Exception: pass` が多用されている。エラーを握り潰すため、デバッグが困難であり、システムが不健全な状態でサイレントに稼働し続けるリスクがある。最低でもログ出力 (`logging.warning`) を行うべきである。
4.  **Fragile YAML Parsing**: `_load_skills` 内で `content.split("---", 2)` による手動パースが行われている。YAML frontmatter の解析はライブラリに任せるべきであり、改行コードやフォーマットの揺らぎで容易に破損する。`python-frontmatter` 等の利用を検討すべき。

### Medium (中)
5.  **Hardcoded Logic & Paths**:
    *   `http://localhost:5678/...`: n8n の URL がハードコードされており、環境変数 (`os.getenv`) による制御ができない。
    *   `/tmp/...`: Windows 環境での互換性が考慮されていない（Python の `tempfile` モジュールを使用すべき）。
    *   `extract_dispatch_info` 内の `gpu_ok` フラグが `force_cpu` に反転して渡されるロジックは、二重否定で認知負荷が高い。
6.  **Review Logic Reliability**: `postcheck_boot_report` における「Drift 計算」(`epsilon_precision`) のロジックがヒューリスティックな「魔法の数字」に依存しており、理論的根拠がコメント (`BS-3b fix`) のみでコード上の検証性が低い。

## 重大度
Critical
