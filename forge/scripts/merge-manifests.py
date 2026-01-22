#!/usr/bin/env python3
"""
merge-manifests.py
Merges all batch-specific manifest files into a single manifest.jsonl

Usage:
  python scripts/merge-manifests.py

This will:
1. Find all manifest_*.jsonl files in Raw/aidb/_index/
2. Merge them into manifest.jsonl
3. Optionally remove the individual batch files
"""

import os
import glob
import json

ROOT_DIR = os.path.join('Raw', 'aidb', '_index')
OUTPUT_FILE = os.path.join(ROOT_DIR, 'manifest.jsonl')

def main():
    pattern = os.path.join(ROOT_DIR, 'manifest_*.jsonl')
    batch_files = glob.glob(pattern)
    
    if not batch_files:
        print("No batch manifest files found.")
        return
    
    print(f"Found {len(batch_files)} batch manifest files:")
    for f in batch_files:
        print(f"  - {f}")
    
    all_entries = []
    for batch_file in batch_files:
        with open(batch_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    all_entries.append(json.loads(line))
    
    # Sort by captured_at timestamp
    all_entries.sort(key=lambda x: x.get('captured_at', ''))
    
    # Write merged manifest
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"\nMerged {len(all_entries)} entries into {OUTPUT_FILE}")
    
    # Optionally clean up batch files
    cleanup = input("Delete individual batch manifest files? (y/n): ").lower().strip()
    if cleanup == 'y':
        for batch_file in batch_files:
            os.remove(batch_file)
            print(f"Deleted: {batch_file}")

if __name__ == "__main__":
    main()
