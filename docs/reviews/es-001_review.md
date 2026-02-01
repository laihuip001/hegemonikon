# 査読バイアス検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **特権バイアス (Privilege Bias)**: `MAX_CONCURRENT = 60` とハードコードされており、「Ultraプラン」の利用を前提としている。標準プランのユーザーに対してレート制限エラーを引き起こす可能性がある。
- **楽観バイアス (Optimism Bias)**: `create_session` のデフォルト引数が `auto_approve=True` となっており、AIの計画に対する人間による承認プロセスをスキップすることを推奨している。安全性よりも速度を優先するバイアスが見られる。
- **確証バイアス / 願望的思考 (Confirmation Bias / Wishful Thinking)**: `synedrion_review` メソッドにおいて、`str(r.session)` に "SILENCE" が含まれているかで問題なしと判定しているが、`JulesSession` クラスにはレビュー出力が含まれていないため、この判定は機能しない（常に False となるか、無関係なフィールドにマッチする）。データが利用可能であるという誤った仮定に基づいている。
- **内集団バイアス (In-Group Bias)**: ドキュメントやコード内で "Synedrion", "Hegemonikón", "Symplokē" といった独自のギリシャ語用語が説明なく多用されており、プロジェクトの背景知識がない開発者に対する認知負荷が高い。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
