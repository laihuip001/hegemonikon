#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] P3→データ処理が必要→pb_parser が担う
"""
Protocol Buffers ファイルから記憶（テキスト）を抽出
スキーマなしで解析し、読めるテキストを Markdown にエクスポート

Usage: python pb_parser.py [pb_file]
"""

import struct
import re
from pathlib import Path
from datetime import datetime

def parse_varint(data: bytes, pos: int):
    """Varint デコード"""
    result = 0
    shift = 0
    while pos < len(data):
        byte = data[pos]
        result |= (byte & 0x7F) << shift
        pos += 1
        if not (byte & 0x80):
            break
        shift += 7
    return result, pos

def extract_text_from_pb(filepath: Path):
    """
    Protocol Buffers から全てのテキスト文字列を抽出
    スキーマなしで length-delimited フィールドを探索
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    texts = []
    pos = 0
    errors = 0
    
    while pos < len(data):
        try:
            # フィールドヘッダ
            header, pos = parse_varint(data, pos)
            wire_type = header & 0x07
            
            if wire_type == 0:  # Varint
                _, pos = parse_varint(data, pos)
            
            elif wire_type == 2:  # Length-delimited (string/bytes)
                length, pos = parse_varint(data, pos)
                if length > 100000 or pos + length > len(data):
                    # 異常な長さ → スキップ
                    pos += 1
                    continue
                
                value = data[pos:pos+length]
                pos += length
                
                # UTF-8 デコード試行
                try:
                    text = value.decode('utf-8')
                    # 意味のあるテキストのみ抽出
                    # (最低10文字、ASCII/日本語を含む)
                    if len(text) >= 10 and re.search(r'[\u3040-\u9fff\w]{3,}', text):
                        texts.append(text)
                except Exception:
                    pass  # TODO: Add proper error handling
            
            elif wire_type == 5:  # 32-bit
                pos += 4
            elif wire_type == 1:  # 64-bit
                pos += 8
            else:
                pos += 1
                errors += 1
                
        except Exception:
            pos += 1
            errors += 1
            if errors > 1000:
                break
    
    return texts

def save_as_markdown(texts: list, output_path: Path, source_name: str):
    """抽出したテキストを Markdown として保存"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# 記憶の発掘: {source_name}\n\n")
        f.write(f"- **抽出日時**: {datetime.now().isoformat()}\n")
        f.write(f"- **抽出テキスト数**: {len(texts)}\n\n")
        f.write("---\n\n")
        
        for i, text in enumerate(texts, 1):
            # 長いテキストは User/Claude の発言の可能性が高い
            if len(text) > 100:
                f.write(f"## [{i}]\n\n")
                f.write(f"{text}\n\n")
                f.write("---\n\n")
    
    print(f"[OK] Saved: {output_path}")

def main():
    import sys
    
    if len(sys.argv) > 1:
        pb_file = Path(sys.argv[1])
    else:
        # デフォルト: archive フォルダの最初のファイル
        archive_dir = Path(r"M:\.gemini\antigravity\archive")
        pb_files = list(archive_dir.glob("*.pb"))
        if not pb_files:
            print("[!] No .pb files found in archive")
            return
        pb_file = pb_files[0]
    
    print(f"[*] Extracting from: {pb_file.name}")
    print(f"[*] Size: {pb_file.stat().st_size:,} bytes")
    print()
    
    texts = extract_text_from_pb(pb_file)
    
    print(f"[*] Found {len(texts)} text segments")
    
    # 長いテキスト（発言）のみをフィルタリング
    long_texts = [t for t in texts if len(t) > 50]
    print(f"[*] Long texts (>50 chars): {len(long_texts)}")
    
    # 出力
    output_dir = Path(r"M:\Brain\.hegemonikon\excavated")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{pb_file.stem}_excavated.md"
    save_as_markdown(long_texts, output_path, pb_file.name)
    
    # プレビュー
    print("\n=== Preview (first 5 long texts) ===\n")
    for i, text in enumerate(long_texts[:5], 1):
        preview = text[:200].replace('\n', ' ')
        print(f"{i}. {preview}...")
        print()

if __name__ == "__main__":
    main()
