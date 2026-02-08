# PROOF: [L3/ユーティリティ] <- mekhane/peira/scripts/ O4→実験スクリプトが必要
#!/usr/bin/env python3
import os
import glob

INDEX_DIR = r"Raw/aidb/_index"
MASTER_MANIFEST = os.path.join(INDEX_DIR, "manifest.jsonl")


# PURPOSE: 関数: main
def main():
    print("Merging manifest files...")

    # Get all batch manifests
    batch_files = glob.glob(os.path.join(INDEX_DIR, "manifest_batch_*.jsonl"))
    batch_files += glob.glob(os.path.join(INDEX_DIR, "manifest_retry.jsonl"))

    total_lines = 0

    with open(MASTER_MANIFEST, "a", encoding="utf-8") as outfile:
        for fname in batch_files:
            if not os.path.exists(fname):
                continue

            print(f"Processing {fname}...")
            with open(fname, "r", encoding="utf-8") as infile:
                for line in infile:
                    if line.strip():
                        outfile.write(line)
                        total_lines += 1

    print(f"Successfully merged {len(batch_files)} files.")
    print(f"Added {total_lines} entries to master manifest.")


if __name__ == "__main__":
    main()
