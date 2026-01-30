# PROOF: [L3/ユーティリティ] O4→実験スクリプトが必要
#!/usr/bin/env python3
"""
cleanup-duplicates.py
Find and remove duplicate files not tracked in manifest.
"""

import json
import os

ROOT_DIR = os.path.join('Raw', 'aidb')
MANIFEST_FILE = os.path.join(ROOT_DIR, '_index', 'manifest.jsonl')

def main():
    # Load manifest
    manifest_paths = set()
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line.strip())
            path = entry.get('file_path', '')
            # Normalize path
            path = path.replace('\\\\', '/').replace('\\', '/')
            manifest_paths.add(path)
    
    print(f"Manifest entries: {len(manifest_paths)}")
    
    # Find all .md files
    all_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip _index folder
        if '_index' in root:
            continue
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                all_files.append(filepath)
    
    print(f"Total .md files: {len(all_files)}")
    
    # Find orphans (files not in manifest)
    orphans = []
    for filepath in all_files:
        normalized = filepath.replace('\\', '/')
        if normalized not in manifest_paths:
            orphans.append(filepath)
    
    print(f"\nOrphan files (not in manifest): {len(orphans)}")
    
    if orphans:
        print("\nOrphans found:")
        for f in orphans[:20]:  # Show first 20
            print(f"  - {f}")
        if len(orphans) > 20:
            print(f"  ... and {len(orphans) - 20} more")
        
        # Ask for confirmation
        confirm = input("\nDelete orphan files? (y/n): ").lower().strip()
        if confirm == 'y':
            for filepath in orphans:
                try:
                    os.remove(filepath)
                    try:
                        print(f"Deleted: {filepath}")
                    except UnicodeEncodeError:
                        print(f"Deleted: {filepath.encode('ascii', 'replace').decode('ascii')}")
                except OSError as e:
                    print(f"Error deleting {filepath}: {e}")
            print(f"\nDeleted {len(orphans)} orphan files.")
        else:
            print("Skipped deletion.")
    else:
        print("No orphan files found.")

if __name__ == "__main__":
    main()
