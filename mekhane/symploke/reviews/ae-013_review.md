# シンプリシティの門番 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **未使用の定数定義**: `THEOREM_REGISTRY` (L38-L76) および `SERIES_INFO` (L79-L82) はファイル内で一切使用されておらず、外部からの参照もテストコードのみです。YAGNI原則により削除すべきです。 (Medium)
- **循環依存と責務の錯綜**: `_load_projects` / `_load_skills` は本ファイルで定義されていますが、呼び出しは `boot_axes.py` 経由で行われ、その `boot_axes.py` が本ファイルを逆インポートしています。単純に呼び出すか、別モジュールに移動すべきです。 (Medium)
- **冗長なロジック**: `_load_projects` (L113-L121) にて `active`, `dormant`, `archived` のリストを作成するために3回イテレーションを行っていますが、その後のループで再度イテレーションを行っており非効率です。 (Low)
- **重複した解析処理**: `_load_skills` (L183-L199) にて YAML frontmatter の解析と本文抽出のために `content.startswith("---")` ブロックを2回繰り返しています。 (Low)
- **未使用の変数**: `_load_skills` 内の `skill_paths` はリストに値を蓄積していますが、戻り値に含まれるのみで実質的に使用されていません。 (Low)
- **過剰な複雑性 (Drift計算)**: `postcheck_boot_report` (L452-L475) における "Drift" および "ε precision" の計算ロジックは、単なる検証スクリプトにしては複雑すぎます。"Informational only" であるならば、この複雑さは正当化されません。 (Medium)
- **グローバルな副作用**: `sys.path.insert` (L34) がモジュールレベルで実行されており、インポート時に予期せぬ副作用を生む可能性があります。 (Low)

## 重大度
Medium
