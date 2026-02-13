# PROOF: [L2/Infrastructure] <- mekhane/ochema/cli.py
# PURPOSE: CLI インターフェース (CLI Interface)
"""
Ochēma CLI.
"""
import click

@click.group()
# PURPOSE: CLI
def cli():
    """Ochēma CLI."""
    pass

if __name__ == "__main__":
    cli()
