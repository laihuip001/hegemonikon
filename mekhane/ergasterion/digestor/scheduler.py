# PROOF: [L2/インフラ] <- mekhane/ergasterion/digestor/ A0→消化処理が必要→scheduler が担う
#!/usr/bin/env python3
"""
Digestor Scheduler - OS 非依存の定時収集デーモン

Usage:
    # フォアグラウンド実行
    python scheduler.py

    # バックグラウンド実行
    nohup python scheduler.py &

    # 停止
    kill $(cat ~/.hegemonikon/digestor/scheduler.pid)
"""

import os
import sys
import time
import signal
from datetime import datetime
from pathlib import Path

# Import path setup — project root + mekhane dir
_mekhane_dir = Path(__file__).parent.parent.parent
_project_root = _mekhane_dir.parent
for _p in [str(_project_root), str(_mekhane_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import schedule

from mekhane.ergasterion.digestor.pipeline import DigestorPipeline

# 設定
SCHEDULE_TIME = "06:00"  # 毎日実行時刻
MAX_PAPERS = 30  # 取得論文数
DRY_RUN = False  # Live mode — 実際に論文を取得
LOG_DIR = Path.home() / ".hegemonikon" / "digestor"
PID_FILE = LOG_DIR / "scheduler.pid"
LOG_FILE = LOG_DIR / "scheduler.log"


# PURPOSE: ログ出力
def log(msg: str):
    """ログ出力"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)

    # ファイルにも書き込み
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# PURPOSE: 消化パイプライン実行
def run_digestor():
    """消化パイプライン実行"""
    log("Starting scheduled digestor run...")

    try:
        pipeline = DigestorPipeline()
        result = pipeline.run(max_papers=MAX_PAPERS, max_candidates=10, dry_run=DRY_RUN)

        log(
            f"Digestor complete: {result.total_papers} papers, {result.candidates_selected} candidates"
        )

        # 候補サマリー
        for i, c in enumerate(result.candidates[:5], 1):
            log(f"  {i}. [{c.score:.2f}] {c.paper.title[:50]}...")

    except Exception as e:
        log(f"Digestor error: {e}")


# PURPOSE: PID ファイル保存
def save_pid():
    """PID ファイル保存"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    log(f"PID saved: {PID_FILE}")


# PURPOSE: クリーンアップ
def cleanup(signum=None, frame=None):
    """クリーンアップ"""
    log("Scheduler stopping...")
    if PID_FILE.exists():
        PID_FILE.unlink()
    sys.exit(0)


# PURPOSE: メインループ
def main():
    """メインループ"""
    log("=" * 50)
    log("Digestor Scheduler starting")
    log(f"Schedule: daily at {SCHEDULE_TIME}")
    log(f"Max papers: {MAX_PAPERS}")
    log(f"Log file: {LOG_FILE}")
    log("=" * 50)

    # シグナルハンドラ
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    # PID 保存
    save_pid()

    # スケジュール設定
    schedule.every().day.at(SCHEDULE_TIME).do(run_digestor)

    # 初回実行（確認用）
    log("Running initial check...")
    run_digestor()

    # メインループ
    log(f"Scheduler running. Next run at {SCHEDULE_TIME}")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 1分ごとにチェック


if __name__ == "__main__":
    main()
