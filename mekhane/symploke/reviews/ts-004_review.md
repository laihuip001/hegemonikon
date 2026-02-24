# テスト速度の時計師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` 関数内の末尾（L538-549付近）で `urllib.request.urlopen` を使用して `http://localhost:5678` へ同期的なHTTPリクエストを行っている。タイムアウトが5秒に設定されており、n8nが起動していない環境（CIやローカルテスト）では、この関数を呼び出すテスト全てが毎回5秒遅延する原因となっている。（重大度: High）
- `get_boot_context` は `boot_axes.py` を経由して `load_attractor` を呼び出すが、これには30秒のタイムアウトが設定されたスレッドプールが含まれる。コンテキストが存在する場合、重いMLモデルのロードが発生し、テスト実行時間を大幅に超過させるリスクがある。（重大度: Medium）
- `_load_projects` や `_load_skills` がファイルシステム（`.agent/projects/registry.yaml` 等）に直接依存しており、ディスクI/Oによる遅延の要因となり得る。特に `TestBootIntegrationChain` などの統合テストで顕著。（重大度: Low）

## 重大度
Medium
