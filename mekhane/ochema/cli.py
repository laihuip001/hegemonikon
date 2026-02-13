# PROOF: [L2/Infra] <- mekhane/ochema/ CLI Entrypoint
"""Ochēma CLI.

Command-line interface for Antigravity operations.
"""

import click
from mekhane.ochema.antigravity_client import AntigravityClient

@click.group()
def cli():
    """Ochēma CLI."""
    pass

@cli.command()
@click.argument("message")
def ask(message: str):
    """Ask a question to the LLM."""
    client = AntigravityClient()
    response = client.ask(message)
    print(response.text)

if __name__ == "__main__":
    cli()
