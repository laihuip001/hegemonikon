#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/tests/ A0->Auto->AddedByCI
# PROOF: [L2/テスト] <- mekhane/symploke/tests/
# PURPOSE: Scheduler API (routes/scheduler.py) のユニットテスト
"""Scheduler Status API tests.

scheduler_*.json の読み取り + サマリー生成を検証。
旧ログ (result 内ネスト) / 新ログ (トップレベル) 両対応を確認。
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# === テスト用ログデータ ===

def _new_format_log(slot: str = "morning", mode: str = "basanos",
                     started: int = 10, failed: int = 1,
                     files: int = 5) -> dict:
    """新フォーマット (F11 以降): トップレベルキー。"""
    return {
        "slot": slot,
        "mode": mode,
        "timestamp": "2026-02-15 09:00:00",
        "total_tasks": started + failed,
        "total_started": started,
        "total_failed": failed,
        "files_reviewed": files,
        "dynamic": False,
        "result": {
            "files": [{"file": f"test_{i}.py"} for i in range(files)],
            "total_started": started,
            "total_failed": failed,
            "total_tasks": started + failed,
        },
        "daily_usage": {},
    }


def _old_format_log(slot: str = "morning", mode: str = "specialist",
                     started: int = 8, failed: int = 2,
                     files: int = 3) -> dict:
    """旧フォーマット (F11 以前): result 内にネスト。"""
    return {
        "slot": slot,
        "mode": mode,
        "timestamp": "2026-02-14 09:00:00",
        "result": {
            "files": [{"file": f"old_{i}.py"} for i in range(files)],
            "total_started": started,
            "total_failed": failed,
            "total_tasks": started + failed,
        },
        "daily_usage": {},
    }


# === テストクラス ===

class TestSchedulerAPI:
    """Scheduler Status API のテスト。"""

    def _create_log_dir(self, tmp: Path, logs: list[tuple[str, dict]]) -> Path:
        """テスト用ログディレクトリを作成。"""
        log_dir = tmp / "logs" / "specialist_daily"
        log_dir.mkdir(parents=True, exist_ok=True)
        for filename, data in logs:
            (log_dir / filename).write_text(json.dumps(data))
        return log_dir

    def test_no_log_dir(self):
        """ログディレクトリが存在しない場合 → no_data。"""
        import importlib
        import mekhane.api.routes.scheduler as mod
        with patch.object(mod, "LOG_DIR", Path("/nonexistent")):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            assert result["status"] == "no_data"
            assert result["runs"] == []

    def test_empty_log_dir(self, tmp_path: Path):
        """ログディレクトリが空の場合 → no_data。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = tmp_path / "logs" / "specialist_daily"
        log_dir.mkdir(parents=True)
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            assert result["status"] == "no_data"

    def test_new_format_log(self, tmp_path: Path):
        """新フォーマットのログ → 正しくパース。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = self._create_log_dir(tmp_path, [
            ("scheduler_20260215_0900.json", _new_format_log()),
        ])
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            assert result["status"] != "no_data"
            assert len(result["runs"]) == 1
            run = result["runs"][0]
            assert run["total_started"] == 10
            assert run["total_failed"] == 1
            assert run["files_reviewed"] == 5

    def test_old_format_log_fallback(self, tmp_path: Path):
        """旧フォーマット (result 内ネスト) → フォールバックでパース。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = self._create_log_dir(tmp_path, [
            ("scheduler_20260214_0900.json", _old_format_log()),
        ])
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            assert result["status"] != "no_data"
            run = result["runs"][0]
            # 旧フォーマットでも result 内から読み取れる
            assert run["total_started"] == 8
            assert run["total_failed"] == 2
            assert run["files_reviewed"] == 3  # len(result.files)

    def test_success_rate_calculation(self, tmp_path: Path):
        """成功率の計算が正しいか検証。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = self._create_log_dir(tmp_path, [
            ("scheduler_20260215_0900.json", _new_format_log(started=9, failed=1)),
        ])
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            summary = result["summary"]
            # (9 - 1) / 9 * 100 = 88.9%
            assert summary["success_rate"] == 88.9
            assert summary["status"] == "warn"  # 70 <= 88.9 < 90

    def test_status_ok(self, tmp_path: Path):
        """成功率 90%+ → status=ok。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = self._create_log_dir(tmp_path, [
            ("scheduler_20260215_0900.json", _new_format_log(started=10, failed=0)),
        ])
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            assert result["summary"]["status"] == "ok"

    def test_status_error(self, tmp_path: Path):
        """成功率 < 70% → status=error。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = self._create_log_dir(tmp_path, [
            ("scheduler_20260215_0900.json", _new_format_log(started=10, failed=5)),
        ])
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            assert result["summary"]["status"] == "error"

    def test_limit_parameter(self, tmp_path: Path):
        """limit パラメータが正しく機能するか。"""
        import mekhane.api.routes.scheduler as mod
        logs = [
            (f"scheduler_2026021{i}_0900.json", _new_format_log())
            for i in range(5)
        ]
        log_dir = self._create_log_dir(tmp_path, logs)
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=2))
            assert len(result["runs"]) == 2

    def test_mode_aggregation(self, tmp_path: Path):
        """モード集計が正しいか。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = self._create_log_dir(tmp_path, [
            ("scheduler_20260215_0900.json", _new_format_log(mode="basanos")),
            ("scheduler_20260214_0900.json", _new_format_log(mode="hybrid")),
            ("scheduler_20260213_0900.json", _new_format_log(mode="basanos")),
        ])
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            modes = result["summary"]["modes"]
            assert modes["basanos"] == 2
            assert modes["hybrid"] == 1

    def test_corrupt_log_skipped(self, tmp_path: Path):
        """壊れたログファイルはスキップされる。"""
        import mekhane.api.routes.scheduler as mod
        log_dir = tmp_path / "logs" / "specialist_daily"
        log_dir.mkdir(parents=True)
        # 壊れた JSON
        (log_dir / "scheduler_20260215_0900.json").write_text("{invalid json")
        # 正常な JSON
        (log_dir / "scheduler_20260214_0900.json").write_text(
            json.dumps(_new_format_log())
        )
        with patch.object(mod, "LOG_DIR", log_dir):
            import asyncio
            result = asyncio.run(mod.scheduler_status(limit=5))
            assert len(result["runs"]) == 1  # 壊れた方はスキップ
