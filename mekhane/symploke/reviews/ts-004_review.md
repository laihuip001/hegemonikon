# テスト速度の時計師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- 同期的なネットワーク呼び出し (Medium): `get_boot_context` 内で `urllib.request.urlopen` を使用して `http://localhost:5678` へ接続しており、タイムアウトが5秒に設定されている。これはテスト実行時に最大5秒の遅延を引き起こす可能性があり、外部環境への依存を生んでいる。
- 重い処理への依存 (Medium): `boot_axes` 経由で呼び出される処理 (`load_attractor` 等) には最大30秒のタイムアウトが設定されており、これらを統合する `boot_integration.py` のテストは30秒を超えるリスクが高い。
- ホームディレクトリへのファイルI/O (Low): `get_boot_context` から呼び出される処理が `Path.home()` を参照しており、環境依存と速度低下の原因となる。

## 重大度
Medium
