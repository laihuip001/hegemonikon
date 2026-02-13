# PROOF: [L2/エージェント] <- mekhane/ochema/ CLI Interface
"""
Ochema Command Line Interface
"""
import argparse
import sys
from typing import Optional

class OchemaCLI:
    """CLI for Ochema operations."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Ochema CLI")
        self.parser.add_argument("--check", action="store_true", help="Check status")
        self.parser.add_argument("--sync", action="store_true", help="Sync data")

    def run(self, args: Optional[list] = None):
        """Run the CLI."""
        parsed = self.parser.parse_args(args)
        if parsed.check:
            print("Ochema is running.")
        if parsed.sync:
            print("Syncing...")

def main():
    cli = OchemaCLI()
    cli.run()

if __name__ == "__main__":
    main()
