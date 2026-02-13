# PROOF: [L2/学習] <- mekhane/ccl/learning/
# PURPOSE: 失敗事例データベース
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class FailureDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.data = {"failures": []}
        if self.db_path.exists():
            with open(self.db_path, "r") as f:
                self.data = json.load(f)

    def record_failure(self, ccl_expr: str, operator: str, failure_type: str, cause: str, resolution: Optional[str] = None) -> int:
        record = {
            "ccl_expr": ccl_expr,
            "operator": operator,
            "failure_type": failure_type,
            "cause": cause,
            "resolution": resolution
        }
        self.data["failures"].append(record)
        with open(self.db_path, "w") as f:
            json.dump(self.data, f)
        return len(self.data["failures"]) - 1

    def get_warnings(self, ccl_expr: str) -> List[str]:
        warnings = []
        if "!" in ccl_expr:
             warnings.append("Known issue: !")
        for f in self.data["failures"]:
            if f["operator"] in ccl_expr:
                warnings.append(f"Past failure: {f['cause']}")
        return warnings

    def format_warnings(self, warnings: List[str]) -> str:
        formatted = []
        for w in warnings:
            if "Known issue" in w:
                formatted.append(f"🔴 {w}")
            else:
                formatted.append(w)
        return "\n".join(formatted)

def get_failure_db(db_path: Path) -> FailureDB:
    return FailureDB(db_path)
