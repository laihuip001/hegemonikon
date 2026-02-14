# PROOF: [L2/P3] <- mekhane/anamnesis
"""
Session Monitor - セッション状態の監視と自動インデックス
"""
import time
import schedule
from pathlib import Path
from typing import Optional

from mekhane.ochema.antigravity_client import AntigravityClient
from mekhane.anamnesis.session_indexer import index_conversations, index_steps


# PURPOSE: [L2-auto] アクティブなセッションを監視し、変更があればインデックスを更新する
class SessionMonitor:
    """アクティブなセッションを監視し、変更があればインデックスを更新する"""

    def __init__(self, check_interval_minutes: int = 5):
        self.check_interval = check_interval_minutes
        self.client = AntigravityClient()
        self.last_checked = {}  # {cascade_id: last_modified_timestamp}

    # PURPOSE: [L2-auto] 変更があったセッションを検出する
    def check_updates(self):
        """変更があったセッションを検出する"""
        try:
            # 最新のセッション一覧を取得
            summary = self.client.session_list(limit=20)
            if "error" in summary:
                print(f"[Monitor] Error fetching sessions: {summary['error']}")
                return

            summaries = summary.get("trajectorySummaries", {})
            updated_sessions = []

            for cid, info in summaries.items():
                last_modified = info.get("lastModifiedTime", "")
                if not last_modified:
                    continue

                # 前回チェック時より新しければ更新対象
                if cid not in self.last_checked or last_modified > self.last_checked[cid]:
                    updated_sessions.append(cid)
                    self.last_checked[cid] = last_modified

            if updated_sessions:
                print(f"[Monitor] Detected updates in {len(updated_sessions)} sessions")
                self.trigger_indexing(updated_sessions)
            else:
                print("[Monitor] No updates detected")

        except Exception as e:
            print(f"[Monitor] Exception in check_updates: {e}")

    # PURPOSE: [L2-auto] インデックス処理を実行する
    def trigger_indexing(self, session_ids: list[str]):
        """インデックス処理を実行する"""
        print(f"[Monitor] Triggering indexing for: {session_ids}")

        # 会話内容のインデックス (重いので頻度は要検討だが、ここでは都度実行)
        # TODO: 特定セッションのみ更新する機能が indexer に必要 (現状は全件/最新N件)
        # ここでは簡易的に「最新20件を再インデックス」する
        try:
            index_conversations(max_sessions=20)
            index_steps(max_per_session=10)
        except Exception as e:
            print(f"[Monitor] Indexing failed: {e}")

    # PURPOSE: [L2-auto] 監視ループを開始する
    def start(self):
        """監視ループを開始する"""
        print(f"[Monitor] Starting session monitor (interval: {self.check_interval} min)")

        # 初回実行
        self.check_updates()

        schedule.every(self.check_interval).minutes.do(self.check_updates)

        while True:
            schedule.run_pending()
            time.sleep(1)


# PURPOSE: [L2-auto] 関数: main
def main():  # PURPOSE: CLI エントリポイント
    import argparse
    parser = argparse.ArgumentParser(description="Session Monitor")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in minutes")
    args = parser.parse_args()

    monitor = SessionMonitor(check_interval_minutes=args.interval)
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\n[Monitor] Stopping...")


if __name__ == "__main__":
    main()
