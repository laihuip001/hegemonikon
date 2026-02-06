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
LEARNED_A_PATH = Path("/home/laihuip001/oikos/mneme/.hegemonikon/learned_A.npy")
LEARNED_A_METADATA_PATH = Path(
    "/home/laihuip001/oikos/mneme/.hegemonikon/learned_A_meta.json"
)


def ensure_persistence_dir(path: Optional[Path] = None) -> None:
    """Ensure the persistence directory exists.

    Args:
        path: Optional custom path (defaults to LEARNED_A_PATH)
    """
    target_path = path or LEARNED_A_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)


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
    ensure_persistence_dir(target_path)

    # Get A matrix from pymdp agent
    A = agent.agent.A

    # Save as numpy array
    np.save(str(target_path), A)

    return target_path


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


def A_exists(path: Optional[Path] = None) -> bool:
    """Check if a saved A matrix exists.

    Args:
        path: Optional custom path (defaults to LEARNED_A_PATH)

    Returns:
        True if the file exists
    """
    target_path = path or LEARNED_A_PATH
    return target_path.exists()


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
