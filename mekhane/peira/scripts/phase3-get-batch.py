# PROOF: [L3/ユーティリティ] O4→実験スクリプトが必要
import os
import json
import sys

URL_LIST_FILE = os.path.join('Raw', 'aidb', '_index', 'url_list.txt')

try:
    offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    with open(URL_LIST_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    batch_urls = urls[offset : offset + limit]
    
    print(json.dumps(batch_urls))

except Exception as e:
    print(json.dumps({"error": str(e)}))

