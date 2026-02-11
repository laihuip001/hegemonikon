# PROOF: [L2/インフラ] <- mekhane/synedrion/gateway/ A0→セキュリティポリシー強制が必要→PolicyEnforcerが担う
"""
Policy Enforcer — MCP Gateway のセキュリティポリシー強制

policy.yaml を読み込み、ツール呼び出しごとに Allow/Deny/RequireApproval を判定する。
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

POLICY_FILE = Path(__file__).parent / "policy.yaml"


class PolicyDecision(Enum):
    """ポリシー判定結果"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class PolicyResult:
    """ポリシー判定の詳細結果"""
    decision: PolicyDecision
    reason: str
    policy_name: str = ""
    log_level: str = "info"
    message: str = ""


@dataclass
class RateLimitWindow:
    """レートリミット管理用のスライディングウィンドウ"""
    max_requests: int = 60
    window_seconds: float = 60.0
    timestamps: deque[float] = field(default_factory=deque)

    def check_and_record(self) -> bool:
        """リクエストが制限内かチェックし、記録する。True=許可"""
        now = time.monotonic()
        # ウィンドウ外のタイムスタンプを除去
        while self.timestamps and (now - self.timestamps[0]) > self.window_seconds:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(now)
        return True

    @property
    def remaining(self) -> int:
        """残りリクエスト数"""
        now = time.monotonic()
        while self.timestamps and (now - self.timestamps[0]) > self.window_seconds:
            self.timestamps.popleft()
        return max(0, self.max_requests - len(self.timestamps))


class PolicyEnforcer:
    """
    MCP Gateway のポリシー強制エンジン。

    policy.yaml を読み込み、ツール呼び出しを検査する。

    使用例:
        enforcer = PolicyEnforcer()
        result = enforcer.check("gnosis", "search")
        if result.decision == PolicyDecision.ALLOW:
            # 実行
        elif result.decision == PolicyDecision.REQUIRE_APPROVAL:
            # 人間の承認を要求
    """

    def __init__(self, policy_path: Path | str | None = None) -> None:
        self._policy_path = Path(policy_path) if policy_path else POLICY_FILE
        self._policies: list[dict[str, Any]] = []
        self._allowed_servers: set[str] = set()
        self._denied_patterns: list[str] = []
        self._rate_limiters: dict[str, RateLimitWindow] = {}
        self._load()

    def _load(self) -> None:
        """policy.yaml をロードしてパースする"""
        if not self._policy_path.exists():
            logger.warning("Policy file not found: %s — using permissive defaults", self._policy_path)
            return

        with open(self._policy_path) as f:
            data = yaml.safe_load(f)

        self._policies = data.get("policies", [])

        for policy in self._policies:
            name = policy.get("name", "")

            # allowed-servers ポリシーの処理
            if "servers" in policy:
                servers = policy["servers"]
                self._allowed_servers = set(servers.get("allow", []))
                self._denied_patterns = servers.get("deny", [])

            # rate-limit ポリシーの処理
            if "rate_limit" in policy:
                rpm = policy["rate_limit"].get("requests_per_minute", 60)
                self._rate_limiters[name] = RateLimitWindow(max_requests=rpm)

        logger.info(
            "Loaded %d policies, %d allowed servers",
            len(self._policies),
            len(self._allowed_servers),
        )

    def check(self, server_name: str, tool_name: str) -> PolicyResult:
        """
        ツール呼び出しをポリシーに照らしてチェックする。

        Args:
            server_name: MCP サーバー名 (例: "gnosis")
            tool_name: ツール名 (例: "search")

        Returns:
            PolicyResult: 判定結果
        """
        # 1. サーバー許可チェック
        server_result = self._check_server(server_name)
        if server_result.decision == PolicyDecision.DENY:
            return server_result

        # 2. 破壊的操作チェック
        for policy in self._policies:
            if "match" not in policy or "action" not in policy:
                continue

            tools_patterns = policy["match"].get("tools", [])
            if any(fnmatch(tool_name, pattern) for pattern in tools_patterns):
                action = policy["action"]
                if action.get("require_human_approval"):
                    msg = action.get("message", "").format(tool_name=tool_name)
                    return PolicyResult(
                        decision=PolicyDecision.REQUIRE_APPROVAL,
                        reason=f"Policy '{policy['name']}' requires approval",
                        policy_name=policy["name"],
                        log_level=action.get("log_level", "audit"),
                        message=msg,
                    )

        # 3. レートリミットチェック
        rate_result = self._check_rate_limit()
        if rate_result is not None:
            return rate_result

        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="All policies passed",
        )

    def _check_server(self, server_name: str) -> PolicyResult:
        """サーバーが許可リストに含まれるかチェック"""
        if not self._allowed_servers and not self._denied_patterns:
            # サーバーポリシー未定義 → 許可
            return PolicyResult(decision=PolicyDecision.ALLOW, reason="No server policy defined")

        if server_name in self._allowed_servers:
            return PolicyResult(decision=PolicyDecision.ALLOW, reason=f"Server '{server_name}' is allowed")

        # deny パターンチェック
        for pattern in self._denied_patterns:
            if fnmatch(server_name, pattern):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Server '{server_name}' denied by pattern '{pattern}'",
                    policy_name="allowed-servers",
                )

        return PolicyResult(decision=PolicyDecision.ALLOW, reason="Server not explicitly denied")

    def _check_rate_limit(self) -> PolicyResult | None:
        """レートリミットをチェック。超過時は DENY を返す"""
        for name, limiter in self._rate_limiters.items():
            if not limiter.check_and_record():
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Rate limit exceeded ({limiter.max_requests}/min)",
                    policy_name=name,
                )
        return None

    def get_server_list(self) -> set[str]:
        """許可されたサーバーの一覧を返す"""
        return self._allowed_servers.copy()

    @property
    def policy_count(self) -> int:
        """ロード済みポリシー数"""
        return len(self._policies)
