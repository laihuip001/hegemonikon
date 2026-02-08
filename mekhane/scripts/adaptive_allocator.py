# PROOF: [L3/ユーティリティ] <- mekhane/scripts/ O4→運用スクリプトが必要→adaptive_allocator が担う
#!/usr/bin/env python3
"""
Adaptive Swarm Allocator

Dynamically allocate 1,800 daily sessions based on:
1. Change-driven (40%): Focus on recently modified files
2. Discovery (40%): Random sampling of untouched code
3. Weekly deep dive (20%): Focused domain rotation

Usage:
    python adaptive_allocator.py --budget 1800 --mode all
    python adaptive_allocator.py --budget 480 --mode change
"""

import subprocess
import random
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional

# Load perspectives configuration
PERSPECTIVES_FILE = (
    Path(__file__).parent / "mekhane/ergasterion/synedrion/perspectives.yaml"
)


@dataclass
# PURPOSE: Daily allocation plan.
class AllocationPlan:
    """Daily allocation plan."""

    date: str
    total_budget: int
    change_driven: list[dict] = field(default_factory=list)
    discovery: list[dict] = field(default_factory=list)
    weekly_focus: list[dict] = field(default_factory=list)


# PURPOSE: Allocate sessions intelligently.
class AdaptiveAllocator:
    """Allocate sessions intelligently."""

    # Weekly focus rotation (Monday = 0)
    WEEKLY_FOCUS = {
        0: ["Security", "Auth"],  # Monday: Security
        1: ["Performance", "Memory"],  # Tuesday: Performance
        2: ["Error", "Async"],  # Wednesday: Error handling
        3: ["API", "Integration"],  # Thursday: API
        4: ["Testing", "Docs"],  # Friday: Quality
        5: ["Logging", "Config"],  # Saturday: Operations
        6: ["Architecture", "DI"],  # Sunday: Architecture
    }

    # All 24 axes
    ALL_AXES = [
        "O1",
        "O2",
        "O3",
        "O4",  # Ousia
        "S1",
        "S2",
        "S3",
        "S4",  # Schema
        "H1",
        "H2",
        "H3",
        "H4",  # Hormē
        "P1",
        "P2",
        "P3",
        "P4",  # Perigraphē
        "K1",
        "K2",
        "K3",
        "K4",  # Kairos
        "A1",
        "A2",
        "A3",
        "A4",  # Akribeia
    ]

    # All 20 domains
    ALL_DOMAINS = [
        "Security",
        "Error",
        "Performance",
        "Memory",
        "Async",
        "Logging",
        "Testing",
        "API",
        "Auth",
        "Config",
        "Modules",
        "DI",
        "Lifecycle",
        "Caching",
        "Networking",
        "DB",
        "UI",
        "Docs",
        "Architecture",
        "Integration",
    ]

    # PURPOSE: 運用ツールコンポーネントの初期化
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.today = datetime.now()

    # PURPOSE: Get files changed in the last N hours.
    def get_changed_files(self, since_hours: int = 24) -> list[str]:
        """Get files changed in the last N hours."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--since={since_hours} hours ago",
                    "--name-only",
                    "--pretty=format:",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            return list(set(files))  # Deduplicate
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []

    # PURPOSE: Match domains based on file paths/names.
    def match_domains_to_files(self, files: list[str]) -> list[str]:
        """Match domains based on file paths/names."""
        domains = set()

        for f in files:
            f_lower = f.lower()

            # Security-related files
            if any(
                k in f_lower
                for k in ["auth", "security", "token", "credential", "password"]
            ):
                domains.add("Security")
                domains.add("Auth")

            # Error handling
            if any(k in f_lower for k in ["error", "exception", "handler"]):
                domains.add("Error")

            # Performance
            if any(k in f_lower for k in ["perf", "cache", "optimize", "fast"]):
                domains.add("Performance")
                domains.add("Caching")

            # Async
            if any(k in f_lower for k in ["async", "await", "concurrent", "parallel"]):
                domains.add("Async")

            # Testing
            if any(k in f_lower for k in ["test", "spec", "mock"]):
                domains.add("Testing")

            # API/MCP
            if any(k in f_lower for k in ["api", "mcp", "server", "client"]):
                domains.add("API")
                domains.add("Networking")

            # Config
            if any(
                k in f_lower for k in ["config", "settings", "env", ".yaml", ".json"]
            ):
                domains.add("Config")

        return list(domains) if domains else ["Architecture"]  # Default

    # PURPOSE: Allocate based on recent changes.
    def allocate_change_driven(self, budget: int) -> list[dict]:
        """Allocate based on recent changes."""
        changed_files = self.get_changed_files()

        if not changed_files:
            print("No recent changes, using Architecture focus")
            domains = ["Architecture", "Modules"]
        else:
            domains = self.match_domains_to_files(changed_files)
            print(f"Detected {len(changed_files)} changed files → Domains: {domains}")

        # Select axes that complement the domains
        # For code changes, prioritize critical review axes
        priority_axes = [
            "O1",
            "A2",
            "S2",
            "H2",
            "K3",
        ]  # Noēsis, Krisis, Mekhanē, Pistis, Telos

        tasks = []
        for domain in domains:
            for axis in priority_axes:
                if len(tasks) >= budget:
                    break
                tasks.append(
                    {
                        "domain": domain,
                        "axis": axis,
                        "perspective_id": f"{domain}-{axis}",
                        "allocation_type": "change_driven",
                        "reason": (
                            f"変更ファイル: {changed_files[:3]}"
                            if changed_files
                            else "default"
                        ),
                    }
                )
            if len(tasks) >= budget:
                break

        return tasks[:budget]

    # PURPOSE: Random sampling for discovery.
    def allocate_discovery(
        self, budget: int, excluded_domains: list[str] = None
    ) -> list[dict]:
        """Random sampling for discovery."""
        excluded = set(excluded_domains or [])
        available_domains = [d for d in self.ALL_DOMAINS if d not in excluded]

        tasks = []
        while len(tasks) < budget:
            domain = random.choice(available_domains)
            axis = random.choice(self.ALL_AXES)

            task = {
                "domain": domain,
                "axis": axis,
                "perspective_id": f"{domain}-{axis}",
                "allocation_type": "discovery",
                "reason": "random sampling",
            }

            # Avoid duplicates
            if task["perspective_id"] not in [t["perspective_id"] for t in tasks]:
                tasks.append(task)

        return tasks

    # PURPOSE: Weekly domain rotation.
    def allocate_weekly_focus(self, budget: int) -> list[dict]:
        """Weekly domain rotation."""
        weekday = self.today.weekday()
        focus_domains = self.WEEKLY_FOCUS.get(weekday, ["Architecture"])

        print(f"Today is {self.today.strftime('%A')} → Focus: {focus_domains}")

        tasks = []
        for domain in focus_domains:
            for axis in self.ALL_AXES:
                if len(tasks) >= budget:
                    break
                tasks.append(
                    {
                        "domain": domain,
                        "axis": axis,
                        "perspective_id": f"{domain}-{axis}",
                        "allocation_type": "weekly_focus",
                        "reason": f"weekly rotation: {self.today.strftime('%A')}",
                    }
                )
            if len(tasks) >= budget:
                break

        return tasks[:budget]

    # PURPOSE: Create complete allocation plan.
    def create_allocation_plan(
        self,
        total_budget: int = 1800,
        change_ratio: float = 0.4,
        discovery_ratio: float = 0.4,
        focus_ratio: float = 0.2,
    ) -> AllocationPlan:
        """Create complete allocation plan."""

        change_budget = int(total_budget * change_ratio)
        discovery_budget = int(total_budget * discovery_ratio)
        focus_budget = total_budget - change_budget - discovery_budget

        print(f"\n=== Allocation Plan for {self.today.strftime('%Y-%m-%d')} ===")
        print(
            f"Total: {total_budget}, Change: {change_budget}, Discovery: {discovery_budget}, Focus: {focus_budget}"
        )

        # Allocate in order
        change_tasks = self.allocate_change_driven(change_budget)
        change_domains = set(t["domain"] for t in change_tasks)

        discovery_tasks = self.allocate_discovery(
            discovery_budget, excluded_domains=list(change_domains)
        )
        focus_tasks = self.allocate_weekly_focus(focus_budget)

        plan = AllocationPlan(
            date=self.today.isoformat(),
            total_budget=total_budget,
            change_driven=change_tasks,
            discovery=discovery_tasks,
            weekly_focus=focus_tasks,
        )

        return plan

    # PURPOSE: Save allocation plan to file.
    def save_plan(self, plan: AllocationPlan, output_path: Path = None):
        """Save allocation plan to file."""
        output_path = (
            output_path or self.repo_path / f"allocation_plan_{plan.date[:10]}.json"
        )
# PURPOSE: CLI エントリポイント — 運用ツールの直接実行

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(asdict(plan), f, indent=2, ensure_ascii=False)

        print(f"\nPlan saved to: {output_path}")
        return output_path


# PURPOSE: main の処理
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Adaptive Swarm Allocator")
    parser.add_argument("--budget", type=int, default=1800, help="Daily session budget")
    parser.add_argument(
        "--mode", choices=["all", "change", "discovery", "focus"], default="all"
    )
    parser.add_argument("--output", help="Output file path")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    args = parser.parse_args()

    allocator = AdaptiveAllocator()

    if args.mode == "all":
        plan = allocator.create_allocation_plan(args.budget)
    elif args.mode == "change":
        tasks = allocator.allocate_change_driven(args.budget)
        plan = AllocationPlan(
            date=datetime.now().isoformat(),
            total_budget=args.budget,
            change_driven=tasks,
        )
    elif args.mode == "discovery":
        tasks = allocator.allocate_discovery(args.budget)
        plan = AllocationPlan(
            date=datetime.now().isoformat(), total_budget=args.budget, discovery=tasks
        )
    elif args.mode == "focus":
        tasks = allocator.allocate_weekly_focus(args.budget)
        plan = AllocationPlan(
            date=datetime.now().isoformat(),
            total_budget=args.budget,
            weekly_focus=tasks,
        )

    # Print summary
    total_tasks = len(plan.change_driven) + len(plan.discovery) + len(plan.weekly_focus)
    print(f"\n📊 Allocation Summary:")
    print(f"   Change-driven: {len(plan.change_driven)}")
    print(f"   Discovery: {len(plan.discovery)}")
    print(f"   Weekly Focus: {len(plan.weekly_focus)}")
    print(f"   Total: {total_tasks}")

    if not args.dry_run:
        output_path = Path(args.output) if args.output else None
        allocator.save_plan(plan, output_path)


if __name__ == "__main__":
    main()
