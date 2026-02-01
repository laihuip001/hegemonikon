#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→データ処理が必要→extract_strings が担う
"""
バイナリファイルから strings を抽出（protobuf パース不要）
Python の strings 相当: ASCII/UTF-8 の連続文字列を抽出

Usage: python extract_strings.py [pb_file]
"""

import re
from pathlib import Path
from datetime import datetime

def extract_strings(filepath: Path, min_length: int = 20):
    """
    バイナリファイルから読める文字列を抽出
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    strings = []
    
    # ASCII 文字列 (印刷可能文字の連続)
    ascii_pattern = rb'[\x20-\x7e]{' + str(min_length).encode() + rb',}'
    for match in re.finditer(ascii_pattern, data):
        try:
            text = match.group().decode('ascii')
            strings.append(('ascii', text))
        except Exception:
            pass  # TODO: Add proper error handling
    
    # UTF-8 文字列 (日本語を含む)
    # マジックバイトで UTF-8 開始を検出
    pos = 0
    while pos < len(data) - min_length:
        # UTF-8 マルチバイト開始を探す (0xC0-0xDF, 0xE0-0xEF, 0xF0-0xF7)
        if 0xC0 <= data[pos] <= 0xF7:
            # 可能な UTF-8 シーケンスを試行
            for end in range(pos + min_length, min(pos + 10000, len(data))):
                try:
                    text = data[pos:end].decode('utf-8')
                    if len(text) >= min_length // 3:  # UTF-8 は 1文字3バイト
                        # 日本語を含むか確認
                        if re.search(r'[\u3040-\u9fff]', text):
                            strings.append(('utf8', text))
                            pos = end
                            break
                except Exception:
                    break
        pos += 1
    
    return strings

def save_as_markdown(strings: list, output_path: Path, source_name: str):
    """抽出した文字列を Markdown として保存"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# 記憶の発掘: {source_name}\n\n")
        f.write(f"- **抽出日時**: {datetime.now().isoformat()}\n")
        f.write(f"- **抽出テキスト数**: {len(strings)}\n\n")
        f.write("---\n\n")
        
        for i, (encoding, text) in enumerate(strings, 1):
            if len(text) > 50:  # 意味のある長さ
                f.write(f"## [{i}] ({encoding})\n\n")
                f.write(f"```\n{text[:2000]}\n```\n\n")
                f.write("---\n\n")
    
    print(f"[OK] Saved: {output_path}")

def main():
    import sys
    
    if len(sys.argv) > 1:
        pb_file = Path(sys.argv[1])
    else:
        archive_dir = Path(r"M:\.gemini\antigravity\archive")
        pb_files = list(archive_dir.glob("*.pb"))
        if not pb_files:
            print("[!] No .pb files found")
            return
        pb_file = pb_files[0]
    
    print(f"[*] Extracting strings from: {pb_file.name}")
    print(f"[*] Size: {pb_file.stat().st_size:,} bytes")
    print()
    
    strings = extract_strings(pb_file, min_length=20)
    
    # 長い文字列でフィルタリング
    long_strings = [(e, s) for e, s in strings if len(s) > 50]
    
    print(f"[*] Total strings: {len(strings)}")
    print(f"[*] Long strings (>50): {len(long_strings)}")
    
    # 出力
    output_dir = Path(r"M:\Brain\.hegemonikon\excavated")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{pb_file.stem}_strings.md"
    save_as_markdown(long_strings, output_path, pb_file.name)
    
    # プレビュー
    print("\n=== Preview ===\n")
    for i, (enc, text) in enumerate(long_strings[:5], 1):
        preview = text[:150].replace('\n', ' ')
        print(f"{i}. [{enc}] {preview}...")
        print()

if __name__ == "__main__":
    main()
