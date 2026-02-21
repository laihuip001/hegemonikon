# 戻り値エラー反対者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- get_boot_context 関数内で `gpu_ok, gpu_reason = _gpu_pf()` という Go 言語スタイルの (ok, error) タプル戻り値が使用されています。Python では例外を使用すべきです。(Medium)
- extract_dispatch_info, _load_projects, _load_skills 等の関数で例外を握りつぶし、空の辞書やデフォルト値を返すことでエラーを表現しています。これは呼び出し元に正常終了と誤認させる恐れがあり、例外による明示的なエラー通知が望ましいです。(Medium)
- postcheck_boot_report 関数がファイル不在時に `{"passed": False, ...}` という辞書を返しています。FileNotFoundError を送出すべきです。(Low)

## 重大度
Medium
