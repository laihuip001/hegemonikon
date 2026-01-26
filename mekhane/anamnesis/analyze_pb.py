#!/usr/bin/env python3
"""Antigravity .pb ファイルからテキスト文字列を抽出"""
import re
import sys
from pathlib import Path

def extract_strings(filepath: Path, min_length: int = 10):
    """バイナリファイルから ASCII/日本語文字列を抽出"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # ASCII 文字列（10文字以上）
    ascii_pattern = rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}'
    ascii_strings = re.findall(ascii_pattern, data)
    
    return [s.decode('ascii', errors='ignore') for s in ascii_strings]

if __name__ == '__main__':
    pb_dir = Path(r"M:\.gemini\antigravity\conversations")
    
    # 最初のファイルを解析
    pb_files = list(pb_dir.glob("*.pb"))
    if pb_files:
        sample = pb_files[0]
        print(f"[*] Analyzing: {sample.name}")
        print(f"[*] Size: {sample.stat().st_size} bytes")
        print()
        
        strings = extract_strings(sample)
        print(f"[*] Found {len(strings)} strings")
        print()
        print("=== First 50 strings ===")
        for s in strings[:50]:
            print(s[:200])
