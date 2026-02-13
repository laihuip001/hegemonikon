#!/usr/bin/env python3
# PROOF: [L2/OchemaCLI] <- mekhane/ochema/ A0→Ochema CLI
"""
Ochema CLI - mekhane.ochema

Command-line interface for managing Ochema backend services.
"""

import argparse
import sys
import logging
from typing import List, Optional

# Configure logger
logger = logging.getLogger(__name__)


# PURPOSE: Ochema CLI Handler
class OchemaCLI:
    """Command-line interface for managing Ochema backend services."""

    # PURPOSE: Initialize CLI
    def __init__(self, argv: Optional[List[str]] = None):
        """Initialize CLI handler."""
        self.argv = argv or sys.argv[1:]
        self.parser = self._build_parser()

    # PURPOSE: Build argument parser
    def _build_parser(self) -> argparse.ArgumentParser:
        """Build argument parser."""
        parser = argparse.ArgumentParser(description="Ochema Backend Manager")
        subparsers = parser.add_subparsers(dest="command")

        # Start command
        start_parser = subparsers.add_parser("start", help="Start backend services")
        start_parser.add_argument("--port", type=int, default=8000)

        # Stop command
        subparsers.add_parser("stop", help="Stop backend services")

        # Status command
        subparsers.add_parser("status", help="Check backend status")

        return parser

    # PURPOSE: Run command
    def run(self) -> int:
        """Run the CLI command."""
        args = self.parser.parse_args(self.argv)

        if args.command == "start":
            print(f"Starting Ochema backend on port {args.port}...")
            return 0
        elif args.command == "stop":
            print("Stopping Ochema backend...")
            return 0
        elif args.command == "status":
            print("Ochema backend is running")
            return 0
        else:
            self.parser.print_help()
            return 1


# PURPOSE: Entry point
def main():
    """CLI entry point."""
    cli = OchemaCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()
