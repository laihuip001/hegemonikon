#!/usr/bin/env python3
"""
T-series 発動検知スクリプト
===========================

エクスポートされたチャット履歴から [Hegemonikon] T{N} パターンを検出し、
dispatch_log.yaml に自動追記する。

使用方法:
    python detect-t-series.py                           # 最新のセッションファイルを処理
    python detect-t-series.py <markdown_file>           # 特定ファイルを処理
    python detect-t-series.py --scan-dir <directory>    # ディレクトリをスキャン

検出パターン:
    [Hegemonikon] T1 Aisthēsis
    [Hegemonikon] T2 Krisis
    [Hegemonikon] O2 Boulēsis
    etc.
"""

import re
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Windows stdout UTF-8対策
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# パス設定
DISPATCH_LOG = Path(r"M:\Brain\.hegemonikon\logs\dispatch_log.yaml")
SESSIONS_DIR = Path(r"M:\Brain\.hegemonikon\sessions")

# T-series/O-series 発動パターン
HEGEMONIKON_PATTERN = re.compile(
    r'\[Hegemonikon\]\s*([TO])(\d)\s*(\w+)?',
    re.IGNORECASE
)

# 詳細パターン（入力/判断/出力を含む）
DETAIL_PATTERN = re.compile(
    r'\[Hegemonikon\]\s*([TO])(\d)\s*(\w+)?\s*\n\s*(?:入力|input):\s*(.+?)(?:\n|$)',
    re.IGNORECASE | re.DOTALL
)

# T-series名マッピング
T_SERIES_NAMES = {
    "T1": "Aisthēsis",
    "T2": "Krisis",
    "T3": "Theōria",
    "T4": "Phronēsis",
    "T5": "Peira",
    "T6": "Praxis",
    "T7": "Dokimē",
    "T8": "Anamnēsis",
}

O_SERIES_NAMES = {
    "O1": "Noēsis",
    "O2": "Boulēsis",
    "O3": "Zētēsis",
    "O4": "Energeia",
}

def load_dispatch_log() -> dict:
    """既存のログを読み込み"""
    if not DISPATCH_LOG.exists():
        return {"version": "1.0.0", "created": datetime.now().isoformat(), "entries": []}
    
    with open(DISPATCH_LOG, "r", encoding="utf-8") as f:
        content = f.read()
        # コメント行を除去してパース
        lines = [line for line in content.split("\n") if not line.strip().startswith("#")]
        return yaml.safe_load("\n".join(lines)) or {"entries": []}

def save_dispatch_log(data: dict, stats: dict):
    """ログを保存（統計コメント付き）"""
    DISPATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    with open(DISPATCH_LOG, "w", encoding="utf-8") as f:
        # ヘッダー
        f.write("# Dispatch Log\n")
        f.write("# Hegemonikón Phase B移行判定用の運用ログ\n")
        f.write(f"# 閾値: dispatch_count >= 50, failure_rate < 10%, exception_patterns >= 3\n\n")
        
        # データ部分
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # 統計コメント
        f.write(f"\n# === 統計サマリー ===\n")
        f.write(f"# dispatch_count: {stats['total']}\n")
        f.write(f"# success_count: {stats['success']}\n")
        f.write(f"# failure_count: {stats['failure']}\n")
        f.write(f"# failure_rate: {stats['failure_rate']}%\n")
        f.write(f"# exception_patterns: {stats['exceptions']}\n")
        f.write(f"# Phase B移行: {'達成' if stats['phase_b'] else '未達成'} ({stats['total']}/50)\n")

def detect_t_series(content: str) -> list:
    """T-series/O-series 発動パターンを検出"""
    detections = []
    
    for match in HEGEMONIKON_PATTERN.finditer(content):
        series_type = match.group(1).upper()  # T or O
        series_num = match.group(2)
        series_name = match.group(3) or ""
        
        series_id = f"{series_type}{series_num}"
        
        # 正式名を取得
        if series_type == "T":
            official_name = T_SERIES_NAMES.get(series_id, series_name)
        else:
            official_name = O_SERIES_NAMES.get(series_id, series_name)
        
        # 前後のコンテキストを取得（50文字）
        start = max(0, match.start() - 50)
        end = min(len(content), match.end() + 100)
        context = content[start:end].replace("\n", " ").strip()
        
        detections.append({
            "series_id": series_id,
            "series_type": "t_series" if series_type == "T" else "o_series",
            "name": official_name,
            "context": context[:150],
            "position": match.start()
        })
    
    return detections

def detection_to_dispatch_entry(detection: dict, source_file: str, existing_ids: set) -> dict:
    """検出結果をdispatch_log形式に変換"""
    today = datetime.now().strftime("%Y%m%d")
    
    # 既存IDとの重複を避けながら新IDを生成
    counter = 1
    while True:
        new_id = f"HGK-{today}-{str(counter).zfill(3)}"
        if new_id not in existing_ids:
            break
        counter += 1
    
    existing_ids.add(new_id)
    
    # source_agentとtarget_agentを推測
    # T-series発動はClaude内部の処理なので、両方claude_antigravityとする
    source_agent = "claude_antigravity"
    target_agent = "claude_antigravity"
    
    # T5, O3 は外部エージェントへの委譲を示唆
    if detection["series_id"] in ["T5", "O3"]:
        target_agent = "perplexity"
    elif detection["series_id"] in ["T6", "O4"]:
        target_agent = "local_filesystem"
    
    return {
        "id": new_id,
        "timestamp": datetime.now().isoformat(),
        "t_series": detection["series_id"] if detection["series_type"] == "t_series" else None,
        "o_series": detection["series_id"] if detection["series_type"] == "o_series" else None,
        "source_agent": source_agent,
        "target_agent": target_agent,
        "task": f"{detection['series_id']} {detection['name']} 発動",
        "status": "success",
        "duration_ms": None,
        "exception": None,
        "notes": f"Auto-detected from {source_file}: {detection['context'][:80]}..."
    }

def process_file(filepath: Path, existing_ids: set) -> list:
    """ファイルを処理し、T-series発動を検出"""
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return []
    
    content = filepath.read_text(encoding="utf-8")
    detections = detect_t_series(content)
    
    if not detections:
        print(f"📄 No T-series detections in {filepath.name}")
        return []
    
    entries = []
    for detection in detections:
        entry = detection_to_dispatch_entry(detection, filepath.name, existing_ids)
        entries.append(entry)
        print(f"✅ Detected: {detection['series_id']} {detection['name']}")
    
    return entries

def get_latest_session_file() -> Path:
    """最新のセッションファイルを取得"""
    if not SESSIONS_DIR.exists():
        return None
    
    md_files = list(SESSIONS_DIR.glob("*.md"))
    if not md_files:
        return None
    
    # 更新日時でソート
    md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return md_files[0]

def main():
    parser = argparse.ArgumentParser(description="Detect T-series activations and record to dispatch log")
    parser.add_argument("file", nargs="?", help="Markdown file to process")
    parser.add_argument("--scan-dir", "-d", help="Directory to scan for markdown files")
    parser.add_argument("--pattern", "-p", default="*.md", help="File pattern for scanning")
    parser.add_argument("--dry-run", action="store_true", help="Detect only, don't write to log")
    
    args = parser.parse_args()
    
    # 既存ログ読み込み
    log_data = load_dispatch_log()
    entries = log_data.get("entries", [])
    existing_ids = set(e.get("id", "") for e in entries)
    
    new_entries = []
    
    if args.scan_dir:
        directory = Path(args.scan_dir)
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return 1
        
        for filepath in directory.rglob(args.pattern):
            new_entries.extend(process_file(filepath, existing_ids))
            
    elif args.file:
        new_entries = process_file(Path(args.file), existing_ids)
        
    else:
        # 最新のセッションファイルを処理
        latest = get_latest_session_file()
        if latest:
            print(f"📄 Processing latest session: {latest.name}")
            new_entries = process_file(latest, existing_ids)
        else:
            print("❌ No session files found")
            return 1
    
    if not new_entries:
        print("\n📊 No new T-series detections")
        return 0
    
    print(f"\n🎯 Detected {len(new_entries)} T-series activations")
    
    if args.dry_run:
        print("🔍 Dry run - not writing to log")
        return 0
    
    # ログに追加
    entries.extend(new_entries)
    log_data["entries"] = entries
    
    # 統計計算
    total = len(entries)
    success = sum(1 for e in entries if e.get("status") == "success")
    failure = total - success
    exceptions = len(set(e.get("exception") for e in entries if e.get("exception")))
    
    stats = {
        "total": total,
        "success": success,
        "failure": failure,
        "failure_rate": round(failure / total * 100, 1) if total > 0 else 0,
        "exceptions": exceptions,
        "phase_b": total >= 50 and (failure / total * 100 if total > 0 else 0) < 10 and exceptions >= 3
    }
    
    save_dispatch_log(log_data, stats)
    print(f"\n📊 Total dispatches: {total}/50 ({round(total/50*100, 1)}%)")
    
    return 0

if __name__ == "__main__":
    exit(main())
