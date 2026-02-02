# 会話ログ活用基盤 実装計画

## 目的

81件の会話ログ (conv_*.md) を意味検索可能にし、「継続する私」を実現する。

---

## Proposed Changes

### mekhane/symploke

#### [MODIFY] [kairos_ingest.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/symploke/kairos_ingest.py)

1. `parse_conversation(file_path)` 関数を追加
   - `2026-01-31_conv_50_*.md` 形式をパース
   - メタデータ: ID, 日時, タイトル, メッセージ数
   - 本文: 最初の 2000 文字を抽出

2. `get_conversation_files()` 関数を追加
   - `conv_*.md` ファイルを取得

3. `--conversations` フラグを追加
   - Handoff に加え会話ログも投入可能に

#### [MODIFY] [handoff_search.py](file:///home/makaron8426/oikos/hegemonikon/mekhane/symploke/handoff_search.py)

1. `get_boot_handoffs()` を拡張
   - 会話ログも検索対象に含める
   - `type: conversation` でフィルタ可能に

---

## Verification Plan

### 既存テスト実行

```bash
cd /home/makaron8426/oikos/hegemonikon && \
.venv/bin/python -m pytest mekhane/symploke/tests/test_ingest.py -v
```

### 新規投入テスト

```bash
cd /home/makaron8426/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python mekhane/symploke/kairos_ingest.py --conversations --dry-run
```

### 検索テスト

```bash
cd /home/makaron8426/oikos/hegemonikon && \
PYTHONPATH=. .venv/bin/python mekhane/symploke/kairos_ingest.py --load --search "FEP"
```

---

## 備考

- 会話ログは平均 40KB/件 → 全文投入は非効率
- 最初の 2000 文字 + タイトルで意味検索
- 詳細が必要なら元ファイルを参照
