# PROOF: [L2/言語] <- mekhane/ergasterion/typos/
# PURPOSE: Typos 言語定義
from dataclasses import dataclass
from typing import Optional

@dataclass
class ContextItem:
    ref_type: str
    path: str
    tool_chain: Optional[str] = None
