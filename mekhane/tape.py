# PROOF: [L2/Mekhane] <- mekhane/ A0->Auto->AddedByCI
"""
Tape Writer — WF 実行トレースを JSONL として記録する。

Usage:
    from mekhane.tape import TapeWriter

    tape = TapeWriter()
    tape.log("/noe+", "EXPANSION", nodes_created=["H1", "H2", "H3"])
    tape.log("/noe+", "CONFLICT", crud={"action": "modify", "target": "H2", "reason": "反証あり"})
    tape.log("/noe+", "CONVERGENCE", active_nodes=["H1", "H3"], confidence=85)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

TAPE_DIR = Path(__file__).resolve().parents[2] / ".agent" / "tape"


class TapeWriter:
    """Append-only JSONL tape for WF execution traces."""

    def __init__(self, tape_dir: Path | None = None):
        self.tape_dir = tape_dir or TAPE_DIR
        self.tape_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        self.filepath = self.tape_dir / f"tape_{now.strftime('%Y-%m-%d_%H%M')}.jsonl"

    def log(self, wf: str, step: str, **kwargs) -> dict:
        """Append a trace entry to the tape file.

        Args:
            wf: Workflow name (e.g. "/noe+")
            step: Phase name (e.g. "EXPANSION", "CONFLICT", "CONVERGENCE")
            **kwargs: Additional fields (nodes_created, crud, active_nodes, confidence, meta)

        Returns:
            The logged entry dict
        """
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "wf": wf,
            "step": step,
            **kwargs,
        }
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def read(self) -> list[dict]:
        """Read all entries from the current tape file."""
        if not self.filepath.exists():
            return []
        entries = []
        with open(self.filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def summary(self) -> dict:
        """Return a summary of the current tape."""
        entries = self.read()
        wfs = {}
        for e in entries:
            wf = e.get("wf", "unknown")
            wfs[wf] = wfs.get(wf, 0) + 1
        return {
            "file": str(self.filepath),
            "total_entries": len(entries),
            "workflows": wfs,
        }
