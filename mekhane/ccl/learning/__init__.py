# PROOF: [L2/Mekhane] <- mekhane/ccl/learning/ A0->Auto->AddedByCI
# PROOF: [L3/テスト] <- mekhane/ccl/learning/
"""Learning sub-package"""

from .failure_db import FailureDB, get_failure_db

__all__ = ["FailureDB", "get_failure_db"]
