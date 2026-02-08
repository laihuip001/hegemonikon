# PROOF: [L3/ユーティリティ] <- mekhane/scripts/ O4→運用スクリプトが必要→swarm_scheduler が担う
#!/usr/bin/env python3
"""
Swarm Scheduler - Daily 4AM Execution

Manages the daily 1,800 session allocation across 6 accounts.

Usage:
    # Manual run
    python swarm_scheduler.py --run

    # Install cron
    python swarm_scheduler.py --install-cron

    # Check status
    python swarm_scheduler.py --status
"""

import asyncio
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from adaptive_allocator import AdaptiveAllocator, AllocationPlan
from mekhane.symploke.jules_client import JulesClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "swarm_scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# PURPOSE: Orchestrate daily session execution.
class SwarmScheduler:
    """Orchestrate daily session execution."""

    # Realistic limits:
    # - 3 accounts × 3 keys = 9 keys
    # - 90 sessions/key/day limit
    # - Total: 810/day, using 720 with safety margin
    SESSIONS_PER_KEY = 90
    KEYS_AVAILABLE = 9
    DAILY_BUDGET = 720  # 80% of max to avoid hitting limits

    # PURPOSE: 内部処理: init__
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.env_file = self.repo_path / ".env.jules"
        self.results_dir = self.repo_path / "swarm_results"
        self.results_dir.mkdir(exist_ok=True)

    # PURPOSE: Load API keys from .env.jules.
    def load_api_keys(self) -> list[str]:
        """Load API keys from .env.jules."""
        keys = []
        if self.env_file.exists():
            with open(self.env_file) as f:
                for line in f:
                    if line.startswith("JULIUS_API_KEY_"):
                        key = line.split("=", 1)[1].strip()
                        if key:
                            keys.append(key)

        logger.info(f"Loaded {len(keys)} API keys")
        return keys

    # PURPOSE: Execute a batch of tasks with one API key.
    async def execute_batch(
        self,
        api_key: str,
        tasks: list[dict],
        source: str = "sources/github/laihuip001/hegemonikon",
        branch: str = "master",
    ) -> list[dict]:
        """Execute a batch of tasks with one API key."""
        async with JulesClient(api_key=api_key) as client:
            results = []
            for task in tasks:
                try:
                    # Generate prompt from perspective
                    from mekhane.ergasterion.synedrion import PerspectiveMatrix

                    matrix = PerspectiveMatrix.load()
                    perspective = matrix.get(task["domain"], task["axis"])

                    if not perspective:
                        logger.warning(
                            f"Perspective not found: {task['domain']}-{task['axis']}"
                        )
                        continue

                    prompt = matrix.generate_prompt(perspective)

                    # Create session (don't wait for completion)
                    session = await client.create_session(
                        prompt=prompt, source=source, branch=branch, auto_approve=True
                    )

                    results.append(
                        {
                            "perspective_id": task["perspective_id"],
                            "session_id": session.id,
                            "url": f"https://jules.google.com/session/{session.id}",
                            "status": "started",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    logger.info(f"Started: {task['perspective_id']} → {session.id}")

                    # Rate limiting
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error for {task['perspective_id']}: {e}")
                    results.append(
                        {
                            "perspective_id": task["perspective_id"],
                            "error": str(e),
                            "status": "failed",
                        }
                    )

            return results

    # PURPOSE: Execute full allocation plan across all accounts.
    async def execute_plan(self, plan: AllocationPlan) -> dict:
        """Execute full allocation plan across all accounts."""
        keys = self.load_api_keys()
        if len(keys) < self.ACCOUNTS:
            logger.warning(
                f"Only {len(keys)} keys available (expected {self.ACCOUNTS})"
            )

        # Combine all tasks
        all_tasks = plan.change_driven + plan.discovery + plan.weekly_focus
        logger.info(f"Total tasks: {len(all_tasks)}")

        # Distribute across keys (max 90 per key)
        keys = self.load_api_keys()
        sessions_per_key = min(len(all_tasks) // len(keys) + 1, self.SESSIONS_PER_KEY)
        batches = []
        for i in range(0, len(all_tasks), sessions_per_key):
            batches.append(all_tasks[i : i + sessions_per_key])

        # Execute in parallel
        all_results = []
        for i, (key, batch) in enumerate(zip(keys, batches)):
            logger.info(f"Account {i+1}: {len(batch)} tasks")
            results = await self.execute_batch(key, batch)
            all_results.extend(results)

        # Save results
        output_file = (
            self.results_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "plan_date": plan.date,
                    "total_tasks": len(all_tasks),
                    "results": all_results,
                    "summary": {
                        "started": sum(
                            1 for r in all_results if r.get("status") == "started"
                        ),
                        "failed": sum(
                            1 for r in all_results if r.get("status") == "failed"
                        ),
                    },
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"Results saved to: {output_file}")
        return {"output_file": str(output_file), "results": all_results}

    # PURPOSE: Generate crontab entry for 4AM daily.
    def get_crontab_entry(self) -> str:
        """Generate crontab entry for 4AM daily."""
        script_path = Path(__file__).absolute()
        repo_path = self.repo_path.absolute()
        venv_python = repo_path / ".venv/bin/python"

        # 4:00 AM JST = 19:00 UTC (previous day)
        return f"0 19 * * * cd {repo_path} && {venv_python} {script_path} --run >> {repo_path}/swarm_scheduler.log 2>&1"

    # PURPOSE: Install cron job.
    def install_cron(self) -> bool:
        """Install cron job."""
        entry = self.get_crontab_entry()

        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current = result.stdout if result.returncode == 0 else ""

            # Check if already installed
            if "swarm_scheduler.py" in current:
                logger.info("Cron job already installed")
                return True

            # Add new entry
            new_crontab = current.strip() + "\n" + entry + "\n"

            process = subprocess.Popen(
                ["crontab", "-"], stdin=subprocess.PIPE, text=True
            )
            process.communicate(input=new_crontab)

            logger.info(f"Cron installed: {entry}")
            return True

        except Exception as e:
            logger.error(f"Failed to install cron: {e}")
            return False

    # PURPOSE: Get scheduler status.
    def get_status(self) -> dict:
        """Get scheduler status."""
        # Check cron
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cron_installed = (
            "swarm_scheduler.py" in result.stdout if result.returncode == 0 else False
        )

        # Check recent runs
        recent_runs = (
            sorted(self.results_dir.glob("run_*.json"))[-5:]
            if self.results_dir.exists()
            else []
        )

        return {
            "cron_installed": cron_installed,
# PURPOSE: Execute daily swarm.
            "results_dir": str(self.results_dir),
            "recent_runs": [str(r) for r in recent_runs],
            "api_keys": len(self.load_api_keys()),
            "daily_budget": self.DAILY_BUDGET,
        }


async def run_daily():
    """Execute daily swarm."""
    scheduler = SwarmScheduler()
    allocator = AdaptiveAllocator()

    logger.info("=" * 60)
    logger.info(f"Starting daily swarm run: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    # Create allocation plan
    plan = allocator.create_allocation_plan(scheduler.DAILY_BUDGET)

    # Execute
# PURPOSE: 関数: main
    results = await scheduler.execute_plan(plan)

    logger.info("=" * 60)
    logger.info(f"Completed: {results['output_file']}")
    logger.info("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Swarm Scheduler")
    parser.add_argument("--run", action="store_true", help="Execute daily run")
    parser.add_argument("--install-cron", action="store_true", help="Install cron job")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--budget", type=int, help="Override daily budget")
    args = parser.parse_args()

    scheduler = SwarmScheduler()

    if args.run:
        asyncio.run(run_daily())

    elif args.install_cron:
        if scheduler.install_cron():
            print("✅ Cron job installed for 4:00 AM JST daily")
            print(f"   Entry: {scheduler.get_crontab_entry()}")
        else:
            print("❌ Failed to install cron")

    elif args.status:
        status = scheduler.get_status()
        print("\n📊 Swarm Scheduler Status:")
        print(f"   Cron installed: {'✅' if status['cron_installed'] else '❌'}")
        print(f"   API keys: {status['api_keys']}")
        print(f"   Daily budget: {status['daily_budget']}")
        print(f"   Recent runs: {len(status['recent_runs'])}")
        for run in status["recent_runs"]:
            print(f"     - {Path(run).name}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
