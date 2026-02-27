# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (L147): `summary[:50]` による切り捨ては、サロゲートペアや結合文字（例: 絵文字、濁点付き文字）の途中で切断し、無効なUnicode列（文字化け）を生成するリスクがある (Low)
- `get_boot_context` (L222): `content[:200]` も同様に、多言語テキストに対するナイーブなスライシングであり、文脈の不自然な分断を招く恐れがある (Low)
- `generate_boot_template` (L416): `summary[:100]` も同様の問題を抱えている。特に「要約」という性質上、意味の塊を維持すべきである (Low)
- `postcheck_boot_report` (L477): `len(content)` は書記素クラスター数（Grapheme Clusters）ではなくコードポイント数を返すため、絵文字や結合文字を含む場合、ユーザーが認識する「文字数」よりも大きな値を報告し、「嘘をつく」状態にある (Low)
- 全体: 入力テキストに対して `unicodedata.normalize` による正規化が行われておらず、結合文字（NFD）と合成済み文字（NFC）の混在により、文字列比較や長さカウントが一貫しない可能性がある (Low)

## 重大度
Low
