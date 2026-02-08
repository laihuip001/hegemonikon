# PROOF: [L2/インフラ] <- mekhane/fep/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → FEP エージェントには学習がある
   → 学習結果をセッション間で保持する必要
   → persistence.py が担う

Q.E.D.

---

FEP Agent Persistence Module

Handles saving and loading of learned A matrices between sessions.
Enables Dirichlet-based learning accumulation across /boot and /bye cycles.

References:
- arXiv:2412.10425: Learning Parameters section
- Hegemonikón Handoff Protocol
"""

from pathlib import Path
from typing import Optional, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from .fep_agent import HegemonikónFEPAgent

# Default persistence paths
LEARNED_A_PATH = Path("/home/makaron8426/oikos/mneme/.hegemonikon/learned_A.npy")
LEARNED_A_METADATA_PATH = Path(
    "/home/makaron8426/oikos/mneme/.hegemonikon/learned_A_meta.json"
)


# PURPOSE: Ensure the persistence directory exists.
def ensure_persistence_dir() -> None:
    """Ensure the persistence directory exists."""
    LEARNED_A_PATH.parent.mkdir(parents=True, exist_ok=True)


# PURPOSE: Save learned A matrix to file.
def save_A(agent: "HegemonikónFEPAgent", path: Optional[Path] = None) -> Path:
    """Save learned A matrix to file.

    Args:
        agent: The FEP agent whose A matrix to save
        path: Optional custom path (defaults to LEARNED_A_PATH)

    Returns:
        Path where the A matrix was saved

    Example:
        >>> from mekhane.fep import HegemonikónFEPAgent
        >>> from mekhane.fep.persistence import save_A
        >>> agent = HegemonikónFEPAgent()
        >>> # ... training ...
        >>> saved_path = save_A(agent)
    """
    target_path = path or LEARNED_A_PATH
    ensure_persistence_dir()

    # Get A matrix from pymdp agent
    A = agent.agent.A

    # Save as numpy array
    np.save(str(target_path), A)

    return target_path


# PURPOSE: Load A matrix from file.
def load_A(path: Optional[Path] = None) -> Optional[np.ndarray]:
    """Load A matrix from file.

    Args:
        path: Optional custom path (defaults to LEARNED_A_PATH)

    Returns:
        Loaded A matrix, or None if file doesn't exist

    Example:
        >>> from mekhane.fep.persistence import load_A, A_exists
        >>> if A_exists():
        ...     A = load_A()
    """
    target_path = path or LEARNED_A_PATH

    if not target_path.exists():
        return None

    return np.load(str(target_path), allow_pickle=True)


# PURPOSE: Check if a saved A matrix exists.
def A_exists(path: Optional[Path] = None) -> bool:
    """Check if a saved A matrix exists.

    Args:
        path: Optional custom path (defaults to LEARNED_A_PATH)

    Returns:
        True if the file exists
    """
    target_path = path or LEARNED_A_PATH
    return target_path.exists()


# PURPOSE: Delete saved A matrix.
def delete_A(path: Optional[Path] = None) -> bool:
    """Delete saved A matrix.

    Args:
        path: Optional custom path (defaults to LEARNED_A_PATH)

    Returns:
        True if deletion was successful
    """
    target_path = path or LEARNED_A_PATH

    if target_path.exists():
        target_path.unlink()
        return True
    return False


# ============================================================
# Snapshot + Diff — 学習の可視化
# ============================================================

SNAPSHOT_DIR = LEARNED_A_PATH.parent / "snapshots"


def save_snapshot(agent: "HegemonikónFEPAgent", label: str = "") -> Path:
    """Save a timestamped A-matrix snapshot.

    Called during /boot after Dirichlet learning.
    Keeps at most 30 snapshots (auto-prune oldest).

    Returns:
        Path to the saved snapshot file.
    """
    from datetime import datetime

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    snap_path = SNAPSHOT_DIR / f"A_{ts}{suffix}.npy"

    A = agent.agent.A
    np.save(str(snap_path), A)

    # Auto-prune: keep latest 30
    snaps = sorted(SNAPSHOT_DIR.glob("A_*.npy"))
    if len(snaps) > 30:
        for old in snaps[:-30]:
            old.unlink()

    return snap_path


def list_snapshots() -> list:
    """List all A-matrix snapshots (oldest first).

    Returns:
        List of (path, timestamp_str) tuples.
    """
    if not SNAPSHOT_DIR.exists():
        return []
    snaps = sorted(SNAPSHOT_DIR.glob("A_*.npy"))
    result = []
    for s in snaps:
        # Extract timestamp from filename: A_20260208_171000[_label].npy
        name = s.stem  # A_20260208_171000
        ts_part = name[2:17] if len(name) >= 17 else name[2:]
        result.append((s, ts_part))
    return result


def diff_A(
    A_old: np.ndarray, A_new: np.ndarray, series_labels: Optional[list] = None
) -> dict:
    """Compare two A-matrices and return per-Series change metrics.

    Args:
        A_old: Previous A-matrix (may be pymdp object array)
        A_new: Current A-matrix (may be pymdp object array)
        series_labels: Optional list of series names (default: O,S,H,P,K,A)

    Returns:
        dict with:
            total_change: float (L1 norm of difference)
            per_series: {series: change} dict
            most_changed: name of series with largest change
            session_count: number of snapshots
    """
    if series_labels is None:
        series_labels = ["O", "S", "H", "P", "K", "A"]

    # pymdp stores A as object array shape (1,) → extract inner matrix
    a_old = A_old[0] if A_old.dtype == object else A_old
    a_new = A_new[0] if A_new.dtype == object else A_new

    delta = np.abs(a_new - a_old)
    total_change = float(delta.sum())

    # v2 A-matrix shape: (14, 48) — 14 obs dims, 48 states
    # Topic observations (obs 8-13) correspond to Series O,S,H,P,K,A
    per_series = {}
    for i, series in enumerate(series_labels):
        obs_idx = 8 + i  # topic observation index
        if obs_idx < delta.shape[0]:
            per_series[series] = float(delta[obs_idx, :].sum())
        else:
            per_series[series] = 0.0

    most_changed = max(per_series, key=per_series.get) if per_series else ""

    return {
        "total_change": round(total_change, 4),
        "per_series": {k: round(v, 4) for k, v in per_series.items()},
        "most_changed": most_changed,
        "session_count": len(list_snapshots()),
    }


def format_learning_diff(diff_result: dict) -> str:
    """Format A-matrix diff for boot output (compact Japanese).

    Args:
        diff_result: Output of diff_A()

    Returns:
        Formatted string for boot display.
    """
    if not diff_result or diff_result["total_change"] == 0:
        return "📊 学習差分: 初回セッション (ベースライン)"

    total = diff_result["total_change"]
    most = diff_result["most_changed"]
    count = diff_result["session_count"]

    # Per-series bar chart (text)
    per_s = diff_result["per_series"]
    max_val = max(per_s.values()) if per_s else 1.0
    bars = []
    for series in ["O", "S", "H", "P", "K", "A"]:
        val = per_s.get(series, 0)
        bar_len = int(8 * val / max_val) if max_val > 0 else 0
        bar = "█" * bar_len + "░" * (8 - bar_len)
        bars.append(f"{series}:{bar} {val:.3f}")

    lines = [
        f"📊 学習差分: Δ={total:.3f} (最大変化: {most}-series) "
        f"[{count}セッション蓄積]",
    ]
    lines.append("      " + " | ".join(bars[:3]))
    lines.append("      " + " | ".join(bars[3:]))

    return "\n".join(lines)

