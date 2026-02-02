#!/usr/bin/env python3
"""
Handoff 形式検知・自動記録スクリプト
====================================

Markdownファイル内のYAML `handoff:` ブロックを検出し、
dispatch_log.yaml に自動追記する。

使用方法:
    python detect-handoff.py <markdown_file>
    python detect-handoff.py --scan-dir <directory>
"""

import re
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime

# Windows stdout UTF-8対策
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# パス設定
DISPATCH_LOG = Path(r"M:\Brain\.hegemonikon\logs\dispatch_log.yaml")

# Handoff YAMLパターン
HANDOFF_PATTERN = re.compile(
    r'```yaml\s*\n(handoff:.*?)```',
    re.DOTALL | re.IGNORECASE
)

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

def detect_handoffs(content: str) -> list:
    """Markdown内のhandoffブロックを検出"""
    handoffs = []
    
    for match in HANDOFF_PATTERN.finditer(content):
        yaml_block = match.group(1)
        try:
            parsed = yaml.safe_load(yaml_block)
            if parsed and "handoff" in parsed:
                handoffs.append(parsed["handoff"])
        except yaml.YAMLError as e:
            print(f"⚠️ YAML parse error in handoff block: {e}")
            continue
    
    return handoffs

def handoff_to_dispatch_entry(handoff: dict, source_file: str, existing_entries: list) -> dict:
    """Handoff形式をdispatch_log形式に変換"""
    # 今日のエントリ数をカウント
    today = datetime.now().strftime("%Y%m%d")
    today_count = sum(1 for e in existing_entries if e.get("id", "").startswith(f"HGK-{today}"))
    
    new_id = f"HGK-{today}-{str(today_count + 1).zfill(3)}"
    
    return {
        "id": new_id,
        "timestamp": datetime.now().isoformat(),
        "t_series": handoff.get("t_series", "unknown"),
        "o_series": handoff.get("o_series"),
        "source_agent": handoff.get("source_agent", "unknown"),
        "target_agent": handoff.get("target_agent", "unknown"),
        "task": handoff.get("instruction", "")[:100],  # 最初の100文字
        "status": "success",  # 検出時点では成功と仮定
        "duration_ms": None,
        "exception": None,
        "notes": f"Auto-detected from {source_file}"
    }

def process_file(filepath: Path) -> int:
    """ファイルを処理し、検出したhandoffを記録"""
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return 0
    
    content = filepath.read_text(encoding="utf-8")
    handoffs = detect_handoffs(content)
    
    if not handoffs:
        print(f"📄 No handoffs found in {filepath.name}")
        return 0
    
    # 既存ログ読み込み
    log_data = load_dispatch_log()
    entries = log_data.get("entries", [])
    
    # 新規エントリ追加
    added = 0
    for handoff in handoffs:
        entry = handoff_to_dispatch_entry(handoff, filepath.name, entries)
        
        # 重複チェック（同じtask_idがあればスキップ）
        task_id = handoff.get("task_id")
        if task_id and any(e.get("notes", "").endswith(task_id) for e in entries):
            print(f"⏩ Skipping duplicate: {task_id}")
            continue
        
        entries.append(entry)
        added += 1
        print(f"✅ Added: {entry['id']} - {entry['task'][:50]}...")
    
    if added > 0:
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
    
    return added

def scan_directory(directory: Path, pattern: str = "*.md") -> int:
    """ディレクトリ内のファイルをスキャン"""
    total_added = 0
    
    for filepath in directory.rglob(pattern):
        added = process_file(filepath)
        total_added += added
    
    return total_added

def main():
    parser = argparse.ArgumentParser(description="Detect handoff blocks and record to dispatch log")
    parser.add_argument("file", nargs="?", help="Markdown file to process")
    parser.add_argument("--scan-dir", "-d", help="Directory to scan for markdown files")
    parser.add_argument("--pattern", "-p", default="*.md", help="File pattern for scanning")
    
    args = parser.parse_args()
    
    if args.scan_dir:
        directory = Path(args.scan_dir)
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return 1
        
        added = scan_directory(directory, args.pattern)
        print(f"\n🎯 Total added: {added}")
        
    elif args.file:
        process_file(Path(args.file))
        
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
