# PROOF: [L2/インフラ] <- mekhane/ergasterion/_limbo/factory/ O4→工房機能が必要→verify_batch_5 が担う

import json

# 1. Read URL list to get expected URLs
expected_urls = []
with open(
    r"C:\Users\raikh\Forge\Raw\aidb\_index\url_list.txt", "r", encoding="utf-8"
) as f:
    lines = f.readlines()
    # Indices 510 to 594 (0-indexed) correspond to lines 511 to 595 (1-indexed)
    # Line 595 was empty, so up to 594.
    target_lines = lines[510:594]
    for line in target_lines:
        if line.strip():
            expected_urls.append(line.strip())

print(f"Expected count: {len(expected_urls)}")

# 2. Read Manifest to get actual URLs
actual_urls = set()
with open(
    r"C:\Users\raikh\Forge\Raw\aidb\_index\manifest_batch_5.jsonl",
    "r",
    encoding="utf-8",
) as f:
    for line in f:
        if line.strip():
            try:
                data = json.loads(line)
                actual_urls.add(data["url"])
            except Exception:
                pass  # TODO: Add proper error handling

print(f"Actual count: {len(actual_urls)}")

# 3. Find missing
missing = [url for url in expected_urls if url not in actual_urls]
print("Missing URLs:")
for m in missing:
    print(m)
