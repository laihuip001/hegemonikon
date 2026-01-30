# PROOF: [L2/インフラ] A0→消化処理が必要→__init__ が担う
# Digestor Module
# Gnosis → /eat 自動連携インフラ

from .selector import DigestorSelector
from .pipeline import DigestorPipeline

__all__ = ["DigestorSelector", "DigestorPipeline"]
