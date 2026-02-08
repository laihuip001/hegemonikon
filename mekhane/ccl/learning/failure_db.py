# PROOF: [L2/インフラ] <- mekhane/ccl/learning/
# Phase 4: 失敗パターン学習

"""
CCL Failure Database - 失敗パターンの記録と警告

目的:
- 過去の失敗を記録
- 同じ演算子/式で再度失敗しないよう警告
- 成功パターンも学習
"""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
# PURPOSE: 失敗記録
class FailureRecord:
    """失敗記録"""

    timestamp: str
    ccl_expr: str
    operator: str
    failure_type: str
    cause: str
    resolution: Optional[str] = None


@dataclass
# PURPOSE: 警告記録
class WarningRecord:
    """警告記録"""

    operator: str
    message: str
    severity: str  # "critical", "warning", "info"
    source_failure_id: int


# PURPOSE: 失敗パターンデータベース
class FailureDB:
    """失敗パターンデータベース"""

    # PURPOSE: FailureDB の構成と依存関係の初期化
    def __init__(self, db_path: Path = None):
        self.db_path = (
            db_path
            or Path(__file__).parent.parent.parent
            / "ccl"
            / "learning"
            / "failures.json"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict = None

    @property
    # PURPOSE: データを遅延読み込み
    def data(self) -> Dict:
        """データを遅延読み込み"""
        if self._data is None:
            if self.db_path.exists():
                self._data = json.loads(self.db_path.read_text(encoding="utf-8"))
            else:
                self._data = {
                    "failures": [],
                    "known_issues": {
                        # ハードコードされた既知の問題
                        "!": {
                            "message": "演算子 `!` は「階乗 = 全派生同時実行」です。「否定」ではありません。",
                            "severity": "critical",
                            "added": "2026-01-31",
                        },
                        "*^": {
                            "message": "`*^` は「融合 + メタ分析」です。両方のセクションが必要です。",
                            "severity": "warning",
                            "added": "2026-01-31",
                        },
                    },
                    "success_patterns": [],
                }
        return self._data

    # PURPOSE: データを保存
    def save(self):
        """データを保存"""
        self.db_path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # PURPOSE: 失敗を記録
    def record_failure(
        self,
        ccl_expr: str,
        operator: str,
        failure_type: str,
        cause: str,
        resolution: str = None,
    ) -> int:
        """失敗を記録"""
        record = FailureRecord(
            timestamp=datetime.now().isoformat(),
            ccl_expr=ccl_expr,
            operator=operator,
            failure_type=failure_type,
            cause=cause,
            # NOTE: Removed self-assignment: resolution = resolution
        )
        self.data["failures"].append(asdict(record))
        self.save()
        return len(self.data["failures"]) - 1  # 記録ID

    # PURPOSE: 成功パターンを記録
    def record_success(self, ccl_expr: str, output_summary: str):
        """成功パターンを記録"""
        self.data["success_patterns"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "ccl_expr": ccl_expr,
                "output_summary": output_summary[:200],  # 要約のみ
            }
        )
        self.save()

    # PURPOSE: CCL 式に関連する警告を取得
    def get_warnings(self, ccl_expr: str) -> List[WarningRecord]:
        """CCL 式に関連する警告を取得"""
        warnings = []

        # 既知の問題をチェック
        for pattern, issue in self.data.get("known_issues", {}).items():
            if pattern in ccl_expr:
                warnings.append(
                    WarningRecord(
                        operator=pattern,
                        message=issue["message"],
                        severity=issue["severity"],
                        source_failure_id=-1,
                    )
                )

        # 過去の失敗をチェック
        for i, failure in enumerate(self.data.get("failures", [])):
            # 同じ演算子を含む式で過去に失敗している場合
            if failure["operator"] in ccl_expr:
                warnings.append(
                    WarningRecord(
                        operator=failure["operator"],
                        message=f"過去の失敗: {failure['cause']}",
                        severity="warning",
                        source_failure_id=i,
                    )
                )

        return warnings

    # PURPOSE: 警告をフォーマット
    def format_warnings(self, warnings: List[WarningRecord]) -> str:
        """警告をフォーマット"""
        if not warnings:
            return ""

        lines = ["## ⚠️ 注意事項 (過去の失敗から)\n"]

        for w in warnings:
            severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(
                w.severity, "⚪"
            )

            lines.append(f"{severity_icon} **{w.operator}**: {w.message}")

        lines.append("")
        return "\n".join(lines)

    # PURPOSE: 既知の問題を追加
    def add_known_issue(self, operator: str, message: str, severity: str = "warning"):
        """既知の問題を追加"""
        self.data["known_issues"][operator] = {
            "message": message,
            "severity": severity,
            "added": datetime.now().strftime("%Y-%m-%d"),
# PURPOSE: FailureDB のシングルトンを取得
        }
        self.save()


# シングルトンインスタンス
_db_instance: Optional[FailureDB] = None


def get_failure_db() -> FailureDB:
    """FailureDB のシングルトンを取得"""
    global _db_instance
    if _db_instance is None:
        _db_instance = FailureDB()
    return _db_instance


# テスト用
if __name__ == "__main__":
    db = FailureDB(Path("/tmp/test_failures.json"))

    # 警告をテスト
    warnings = db.get_warnings("/noe!~/u+")
    print(db.format_warnings(warnings))

    # 失敗を記録
    db.record_failure(
        ccl_expr="/noe!",
        operator="!",
        failure_type="演算子誤解",
        cause="! を否定と解釈した",
        resolution="operators.md を確認",
    )

    # 再度警告を確認
    warnings = db.get_warnings("/noe!~/u+")
    print(db.format_warnings(warnings))
