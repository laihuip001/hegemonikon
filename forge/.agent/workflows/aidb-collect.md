---
description: AIDB記事をHTTPベースで一括収集するワークフロー
---

# AIDB記事収集ワークフロー

## 概要
`browser_subagent` の429エラー回避のため、`requests` + `BeautifulSoup` を使用したHTTPベース収集。

## 前提条件
```powershell
pip install requests beautifulsoup4 html2text
```

## 実行手順

### Step 1: URLリストの確認
```powershell
# 行数を確認
Get-Content Raw\aidb\_index\url_list.txt | Measure-Object -Line
```

### Step 2: バッチ収集スクリプト実行
// turbo
```powershell
python scripts/phase3-fetch-simple.py <batch_id> <start_line> <end_line>
```

**例 (Batch 5, Index 511-595):**
```powershell
python scripts/phase3-fetch-simple.py 5 511 595
```

### Step 3: 収集結果確認
// turbo
```powershell
python -c "import json; data=json.load(open('temp_batch_data_<batch_id>.json','r',encoding='utf-8')); print(f'Articles: {len(data)}')"
```

### Step 4: Markdown変換・保存
// turbo
```powershell
python scripts/phase3-save-batch-parallel.py <batch_id>
```

### Step 5: 検証
// turbo
```powershell
Get-ChildItem -Path Raw\aidb -Recurse -Filter "*.md" | Measure-Object | Select-Object -ExpandProperty Count
```

## バッチ割り当て

| Batch | Index Range | Lines | Status |
|-------|-------------|-------|--------|
| 1 | 31-150 | 120 | 完了 |
| 2 | 151-270 | 120 | 完了 |
| 3 | 271-390 | 120 | 完了 |
| 4 | 391-510 | 120 | 完了 |
| 5 | 511-595 | 85 | 未実行 |

## スクリプトの場所
- **収集**: `scripts/phase3-fetch-simple.py`
- **保存**: `scripts/phase3-save-batch-parallel.py`

## 出力先
- **一時ファイル**: `temp_batch_data_<batch_id>.json`
- **Markdownファイル**: `Raw/aidb/YYYY/MM/<post_id>.md`
- **マニフェスト**: `Raw/aidb/_index/manifest_<batch_id>.jsonl`
