# PURPOSE: Ochēma — Antigravity Language Server クライアント
# REASON: Ultra プランの LLM + セッション管理 + Quota 監視を HGK から利用する橋渡し
"""Ochēma (ὄχημα, 乗り物) — Antigravity Language Server Client.

Local Language Server の ConnectRPC JSON エンドポイントを介して
LLM テキスト生成を行う非公式 Python クライアント。

4-Step API Flow:
    1. StartCascade          → cascade_id 取得
    2. SendUserCascadeMessage → メッセージ送信
    3. GetAllCascadeTrajectories → trajectory_id 取得
    4. GetCascadeTrajectorySteps → LLM 応答取得 (ポーリング)

WARNING: ToS グレーゾーン。実験用途限定。公開禁止。
"""

from __future__ import annotations

import json
import re
import ssl
import subprocess
import os
import time
import urllib.request
import uuid
from dataclasses import dataclass, field
from typing import Optional


# --- Data Classes ---

@dataclass
# PURPOSE: [L2-auto] LLM からの応答を保持する。
class LLMResponse:
    """LLM からの応答を保持する。"""
    text: str = ""
    thinking: str = ""
    model: str = ""
    token_usage: dict = field(default_factory=dict)
    cascade_id: str = ""
    trajectory_id: str = ""
    raw_steps: list = field(default_factory=list)


@dataclass
# PURPOSE: [L2-auto] Language Server の接続情報。
class LSInfo:
    """Language Server の接続情報。"""
    pid: int = 0
    csrf: str = ""
    port: int = 0
    workspace: str = ""
    all_ports: list = field(default_factory=list)


# --- Constants ---

DEFAULT_MODEL = "MODEL_CLAUDE_4_5_SONNET_THINKING"
DEFAULT_TIMEOUT = 120  # seconds
POLL_INTERVAL = 1.0  # seconds
USER_AGENT = "ochema/0.1"

# RPC endpoints
RPC_BASE = "exa.language_server_pb.LanguageServerService"
RPC_GET_STATUS = f"{RPC_BASE}/GetUserStatus"
RPC_START_CASCADE = f"{RPC_BASE}/StartCascade"
RPC_SEND_MESSAGE = f"{RPC_BASE}/SendUserCascadeMessage"
RPC_GET_TRAJECTORIES = f"{RPC_BASE}/GetAllCascadeTrajectories"
RPC_GET_STEPS = f"{RPC_BASE}/GetCascadeTrajectorySteps"
RPC_MODEL_CONFIG = f"{RPC_BASE}/GetCascadeModelConfigData"
RPC_EXPERIMENT_STATUS = f"{RPC_BASE}/GetStaticExperimentStatus"
RPC_USER_MEMORIES = f"{RPC_BASE}/GetUserMemories"

# Episode memory
BRAIN_DIR = os.path.expanduser("~/.gemini/antigravity/brain")


# --- Client ---

# PURPOSE: [L2-auto] Antigravity Language Server の非公式クライアント。
class AntigravityClient:
    """Antigravity Language Server の非公式クライアント。

    Usage:
        client = AntigravityClient()
        response = client.ask("Say hello world")
        print(response.text)
    """

    # PURPOSE: [L2-auto] LS を自動検出して接続する。
    def __init__(self, workspace: str = "hegemonikon"):
        """LS を自動検出して接続する。

        Args:
            workspace: ワークスペース名 (ps aux のフィルタに使用)
        """
        self.workspace = workspace
        self._ssl_ctx = self._make_ssl_context()
        self.ls = self._detect_ls()

    @property
    # PURPOSE: [L2-auto] 関数: pid
    def pid(self) -> int:
        return self.ls.pid

    @property
    # PURPOSE: [L2-auto] 関数: port
    def port(self) -> int:
        return self.ls.port

    @property
    # PURPOSE: [L2-auto] 関数: csrf
    def csrf(self) -> str:
        return self.ls.csrf

    # --- Public API ---

    # PURPOSE: [L2-auto] LLM にメッセージを送り、応答を取得する。
    def ask(
        self,
        message: str,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> LLMResponse:
        """LLM にメッセージを送り、応答を取得する。

        4-Step フローを内部で実行:
        1. StartCascade → cascade_id
        2. SendUserCascadeMessage → {}
        3. GetAllCascadeTrajectories → trajectory_id
        4. GetCascadeTrajectorySteps → response (polling)

        Args:
            message: LLM に送るテキスト
            model: モデル名 (enum string)
            timeout: 最大待機秒数

        Returns:
            LLMResponse with text, thinking, model, token_usage
        """
        # Step 1: Start Cascade
        cascade_id = self._start_cascade()

        # Step 2: Send Message
        self._send_message(cascade_id, message, model)

        # Step 3-4: Poll for response
        return self._poll_response(cascade_id, timeout)

    # PURPOSE: [L2-auto] LS のユーザーステータスを取得する。接続確認にも使用。
    def get_status(self) -> dict:
        """LS のユーザーステータスを取得する。接続確認にも使用。"""
        return self._rpc(RPC_GET_STATUS, {
            "metadata": {
                "ideName": "antigravity",
                "extensionName": "antigravity",
                "locale": "en",
            }
        })

    # PURPOSE: [L2-auto] 利用可能なモデル一覧を取得する。
    def list_models(self) -> list[dict]:
        """利用可能なモデル一覧を取得する。"""
        status = self.get_status()
        configs = (
            status.get("userStatus", {})
            .get("cascadeModelConfigData", {})
            .get("clientModelConfigs", [])
        )
        return [
            {
                "name": c.get("modelOrAlias", {}).get("model", ""),
                "label": c.get("label", ""),
                "remaining": round(
                    c.get("quotaInfo", {}).get("remainingFraction", 0) * 100
                ),
            }
            for c in configs
            if c.get("quotaInfo")
        ]

    # PURPOSE: [L2-auto] 全モデルの Quota 残量と設定をリアルタイムで取得する。
    def quota_status(self) -> dict:
        """全モデルの Quota 残量と設定をリアルタイムで取得する。

        Returns:
            dict with models (list), experiments (list), total_models (int)
        """
        # モデル設定と Quota
        config = self._rpc(RPC_MODEL_CONFIG, {})
        models = []
        for c in config.get("clientModelConfigs", []):
            quota = c.get("quotaInfo", {})
            models.append({
                "label": c.get("label", ""),
                "model": c.get("modelOrAlias", {}).get("model", ""),
                "remaining_pct": round(
                    quota.get("remainingFraction", 0) * 100
                ),
                "reset_time": quota.get("resetTime", ""),
                "images": c.get("supportsImages", False),
                "recommended": c.get("isRecommended", False),
            })

        # Experiment flags (context/memory 関連のみ)
        exp_data = self._rpc(RPC_EXPERIMENT_STATUS, {})
        context_keys = {
            "CASCADE_USE_EXPERIMENT_CHECKPOINTER",
            "CASCADE_GLOBAL_CONFIG_OVERRIDE",
            "CASCADE_USER_MEMORIES_IN_SYS_PROMPT",
            "CASCADE_ENABLE_AUTOMATED_MEMORIES",
            "CHAT_TOKENS_SOFT_LIMIT",
            "CHAT_COMPLETION_TOKENS_SOFT_LIMIT",
            "CASCADE_MEMORY_CONFIG_OVERRIDE",
            "MAX_PAST_TRAJECTORY_TOKENS_FOR_RETRIEVAL",
            "CUMULATIVE_PROMPT_CASCADE_CONFIG",
            "CORTEX_CONFIG",
        }
        experiments = [
            {
                "key": s.get("experimentKey", ""),
                "enabled": s.get("enabled", False),
            }
            for s in exp_data.get("status", [])
            if s.get("experimentKey", "") in context_keys
        ]

        return {
            "models": models,
            "experiments": experiments,
            "total_models": len(models),
        }

    # PURPOSE: [L2-auto] セッション情報を取得する。
    def session_info(self, cascade_id: Optional[str] = None) -> dict:
        """セッション情報を取得する。

        Args:
            cascade_id: 特定セッションの ID (省略時は全セッション一覧)

        Returns:
            dict with sessions (list) or session detail
        """
        data = self._rpc(RPC_GET_TRAJECTORIES, {})
        summaries = data.get("trajectorySummaries", {})

        sessions = []
        for cid, info in summaries.items():
            session = {
                "cascade_id": cid,
                "trajectory_id": info.get("trajectoryId", ""),
                "step_count": info.get("stepCount", 0),
                "summary": info.get("summary", ""),
                "status": info.get("status", ""),
                "created": info.get("createdTime", ""),
                "modified": info.get("lastModifiedTime", ""),
                "last_input_time": info.get("lastUserInputTime", ""),
            }
            sessions.append(session)

        if cascade_id:
            # 特定セッションの詳細
            for s in sessions:
                if s["cascade_id"] == cascade_id:
                    # ステップ詳細も取得
                    steps_data = self._rpc(RPC_GET_STEPS, {
                        "cascadeId": cascade_id,
                        "trajectoryId": s["trajectory_id"],
                    })
                    step_types: dict[str, int] = {}
                    for step in steps_data.get("steps", []):
                        st = step.get("type", "UNKNOWN")
                        step_types[st] = step_types.get(st, 0) + 1
                    s["step_types"] = step_types
                    return s
            return {"error": f"cascade_id {cascade_id} not found"}

        # 最新順にソート
        sessions.sort(key=lambda x: x.get("modified", ""), reverse=True)
        return {
            "total": len(sessions),
            "sessions": sessions[:20],  # 最新20件
        }

    # PURPOSE: [L2-auto] セッションの会話内容を読み取る。
    def session_read(
        self,
        cascade_id: str,
        max_turns: int = 10,
        full: bool = False,
    ) -> dict:
        """セッションの会話内容を読み取る。

        ステップを種別ごとにパースし、時系列の会話ログとして返す。

        Args:
            cascade_id: セッションの cascade_id
            max_turns: 返す最大ターン数 (デフォルト: 10)
            full: True → フル取得 (上限 30000 文字)

        Returns:
            dict with conversation (list of turns), metadata
        """
        # trajectory_id を取得
        info = self.session_info(cascade_id)
        if "error" in info:
            return info
        trajectory_id = info.get("trajectory_id", "")
        if not trajectory_id:
            return {"error": f"No trajectory for cascade {cascade_id}"}

        # 全ステップを取得
        steps_data = self._rpc(RPC_GET_STEPS, {
            "cascadeId": cascade_id,
            "trajectoryId": trajectory_id,
        })
        steps = steps_data.get("steps", [])

        # ステップを会話ターンにパース
        conversation: list[dict] = []
        max_content = 30000 if full else 2000

        for step in steps:
            step_type = step.get("type", "")
            status = step.get("status", "")

            if step_type == "CORTEX_STEP_TYPE_USER_REQUEST":
                # ユーザー入力
                items = step.get("userRequest", {}).get("items", [])
                text = ""
                for item in items:
                    if "text" in item:
                        text += item["text"]
                if text:
                    conversation.append({
                        "role": "user",
                        "content": text[:max_content],
                        "truncated": len(text) > max_content,
                    })

            elif step_type == "CORTEX_STEP_TYPE_PLANNER_RESPONSE":
                # Claude 応答
                pr = step.get("plannerResponse", {})
                text = pr.get("response", "")
                model = pr.get("generatorModel", "")
                if text:
                    conversation.append({
                        "role": "assistant",
                        "content": text[:max_content],
                        "model": model,
                        "truncated": len(text) > max_content,
                    })

            elif step_type == "CORTEX_STEP_TYPE_MCP_TOOL":
                # ツール呼出し (サマリのみ)
                tool_info = step.get("mcpToolCall", step.get("toolCall", {}))
                tool_name = tool_info.get("toolName", tool_info.get("name", "unknown"))
                tool_status = "done" if status == "CORTEX_STEP_STATUS_DONE" else status
                conversation.append({
                    "role": "tool",
                    "tool": tool_name,
                    "status": tool_status,
                })

            elif step_type == "CORTEX_STEP_TYPE_TOOL_CALL":
                # 内部ツール呼出し
                tool_call = step.get("toolCall", {})
                tool_name = tool_call.get("name", "unknown")
                conversation.append({
                    "role": "tool",
                    "tool": tool_name,
                    "status": "done" if status == "CORTEX_STEP_STATUS_DONE" else status,
                })

        # 最新 N ターン
        if not full and len(conversation) > max_turns * 3:
            # user+assistant+tool で約3エントリ/ターン
            conversation = conversation[-(max_turns * 3):]

        return {
            "cascade_id": cascade_id,
            "trajectory_id": trajectory_id,
            "total_steps": len(steps),
            "total_turns": len(conversation),
            "summary": info.get("summary", ""),
            "conversation": conversation,
        }

    # PURPOSE: [L2-auto] 過去セッションのエピソード記憶 (.system_generated/steps/) にアクセスする。
    def session_episodes(self, brain_id: Optional[str] = None) -> dict:
        """過去セッションのエピソード記憶 (.system_generated/steps/) にアクセスする。

        Args:
            brain_id: 特定 brain の ID (省略時は全 brain 一覧)

        Returns:
            dict with episodes summary or specific episode contents
        """
        if not os.path.isdir(BRAIN_DIR):
            return {"error": f"Brain directory not found: {BRAIN_DIR}"}

        if brain_id:
            # 特定 brain のエピソード取得
            brain_path = os.path.join(BRAIN_DIR, brain_id, ".system_generated", "steps")
            if not os.path.isdir(brain_path):
                return {"error": f"No episodes for brain {brain_id}"}

            episodes = []
            for step_dir in sorted(os.listdir(brain_path)):
                output_file = os.path.join(brain_path, step_dir, "output.txt")
                if os.path.isfile(output_file):
                    size = os.path.getsize(output_file)
                    # 先頭200文字だけ読む
                    with open(output_file, "r", errors="replace") as f:
                        preview = f.read(200)
                    episodes.append({
                        "step": int(step_dir) if step_dir.isdigit() else step_dir,
                        "size_bytes": size,
                        "preview": preview,
                    })
            return {
                "brain_id": brain_id,
                "total_episodes": len(episodes),
                "episodes": episodes,
            }

        # 全 brain 一覧
        brains = []
        for entry in os.listdir(BRAIN_DIR):
            sys_gen = os.path.join(BRAIN_DIR, entry, ".system_generated", "steps")
            if os.path.isdir(sys_gen):
                count = len([
                    d for d in os.listdir(sys_gen)
                    if os.path.isfile(os.path.join(sys_gen, d, "output.txt"))
                ])
                if count > 0:
                    # brain のアーティファクト名を取得
                    task_file = os.path.join(BRAIN_DIR, entry, "task.md")
                    title = ""
                    if os.path.isfile(task_file):
                        with open(task_file, "r", errors="replace") as f:
                            for line in f:
                                if line.startswith("# "):
                                    title = line[2:].strip()
                                    break
                    brains.append({
                        "brain_id": entry,
                        "episode_count": count,
                        "title": title,
                    })
        brains.sort(key=lambda x: x["episode_count"], reverse=True)
        return {
            "total_brains": len(brains),
            "brains": brains,
        }

    # --- Proposal A: Context Rot Detection ---

    # PURPOSE: [L2-auto] コンテキスト健全性を評価する。
    def context_health(self, cascade_id: Optional[str] = None) -> dict:
        """コンテキスト健全性を評価する。

        tool-mastery.md §5.5 の N chat messages 閾値に基づく:
            ≤30: 🟢 HEALTHY
            31-50: 🟡 WARNING
            >50: 🔴 DANGER

        Args:
            cascade_id: 特定セッション (省略時は最新の RUNNING セッション)

        Returns:
            dict with level, message, step_count, recommendation
        """
        sessions = self.session_info()
        if "error" in sessions:
            return sessions

        target = None
        if cascade_id:
            for s in sessions.get("sessions", []):
                if s["cascade_id"] == cascade_id:
                    target = s
                    break
        else:
            # 最新の RUNNING セッション
            for s in sessions.get("sessions", []):
                if "RUNNING" in s.get("status", ""):
                    target = s
                    break
            # なければ最新セッション
            if not target and sessions.get("sessions"):
                target = sessions["sessions"][0]

        if not target:
            return {"level": "unknown", "message": "No sessions found"}

        step_count = target.get("step_count", 0)

        if step_count <= 30:
            level = "healthy"
            icon = "🟢"
            message = "Context is healthy"
            recommendation = None
        elif step_count <= 50:
            level = "warning"
            icon = "🟡"
            message = "Context pressure rising"
            recommendation = "Consider /bye soon"
        else:
            level = "danger"
            icon = "🔴"
            message = "Context Rot risk HIGH"
            recommendation = "/bye recommended — context degradation likely"

        # Quota も統合
        try:
            quota = self.quota_status()
            low_quota_models = [
                m["label"] for m in quota.get("models", [])
                if m["remaining_pct"] < 20
            ]
        except Exception:
            low_quota_models = []

        return {
            "level": level,
            "icon": icon,
            "message": message,
            "step_count": step_count,
            "cascade_id": target.get("cascade_id", ""),
            "summary": target.get("summary", ""),
            "recommendation": recommendation,
            "low_quota_models": low_quota_models,
        }

    # --- Proposal C: Multi-Model Orchestration ---

    # Model routing table: task keywords → preferred model
    _MODEL_ROUTES = {
        # Claude Thinking — deep analysis, security, architecture
        "MODEL_CLAUDE_4_5_SONNET_THINKING": [
            "security", "audit", "architecture", "design", "review",
            "analyze", "explain", "why", "philosophy", "proof",
        ],
        # Gemini Flash — speed, simple tasks
        "MODEL_PLACEHOLDER_M18": [
            "translate", "format", "list", "simple", "quick",
            "calculate", "convert", "summarize",
        ],
        # Gemini Pro — general purpose, multimodal
        "MODEL_PLACEHOLDER_M8": [
            "image", "video", "multimodal", "diagram", "chart",
        ],
    }

    # Fallback chain
    _MODEL_FALLBACK = {
        "MODEL_CLAUDE_4_5_SONNET_THINKING": "MODEL_PLACEHOLDER_M26",
        "MODEL_PLACEHOLDER_M26": "MODEL_CLAUDE_4_5_SONNET",
        "MODEL_CLAUDE_4_5_SONNET": "MODEL_PLACEHOLDER_M18",
        "MODEL_PLACEHOLDER_M8": "MODEL_PLACEHOLDER_M18",
        "MODEL_PLACEHOLDER_M18": "MODEL_CLAUDE_4_5_SONNET",
    }

    # PURPOSE: [L2-auto] タスク内容に応じて最適モデルを自動選択し、LLM に問い合わせる。
    def smart_ask(
        self,
        message: str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> LLMResponse:
        """タスク内容に応じて最適モデルを自動選択し、LLM に問い合わせる。

        T2 Krisis priority rules を内部で再現:
            1. キーワードマッチでモデルを選択
            2. Quota 残量チェック (20%未満ならフォールバック)
            3. デフォルトは Claude Sonnet 4.5 Thinking

        Args:
            message: LLM に送るテキスト
            timeout: 最大待機秒数

        Returns:
            LLMResponse (model フィールドに実際に使用されたモデル名)
        """
        selected = self._select_model(message)
        return self.ask(message, model=selected, timeout=timeout)

    # PURPOSE: [L2-auto] メッセージ内容と Quota に基づいてモデルを選択する。
    def _select_model(self, message: str) -> str:
        """メッセージ内容と Quota に基づいてモデルを選択する。"""
        msg_lower = message.lower()

        # Step 1: キーワードマッチ
        best_model = DEFAULT_MODEL
        best_score = 0
        for model, keywords in self._MODEL_ROUTES.items():
            score = sum(1 for kw in keywords if kw in msg_lower)
            if score > best_score:
                best_score = score
                best_model = model

        # Step 2: Quota チェック → フォールバック
        try:
            quota = self.quota_status()
            model_quota = {
                m["model"]: m["remaining_pct"]
                for m in quota.get("models", [])
            }

            current = best_model
            attempts = 0
            while attempts < 3:
                remaining = model_quota.get(current, 100)
                if remaining >= 20:
                    return current
                # Quota 不足 → フォールバック
                fallback = self._MODEL_FALLBACK.get(current)
                if not fallback:
                    break
                current = fallback
                attempts += 1
        except Exception:
            pass

        return best_model

    # --- Proposal D: Session Archive ---

    # PURPOSE: [L2-auto] セッションを Markdown でアーカイブする。
    def archive_sessions(
        self,
        output_dir: Optional[str] = None,
        max_sessions: int = 5,
        since: Optional[str] = None,
    ) -> dict:
        """セッションを Markdown でアーカイブする。

        Args:
            output_dir: 出力ディレクトリ (デフォルト: ~/oikos/mneme/.ochema/sessions/)
            max_sessions: 最大エクスポート数
            since: この日時以降のセッションのみ (ISO format)

        Returns:
            dict with exported (list of paths), skipped (int)
        """
        if output_dir is None:
            output_dir = os.path.expanduser(
                "~/oikos/mneme/.ochema/sessions"
            )
        os.makedirs(output_dir, exist_ok=True)

        sessions = self.session_info()
        if "error" in sessions:
            return sessions

        exported: list[str] = []
        skipped = 0

        for s in sessions.get("sessions", [])[:max_sessions]:
            cid = s["cascade_id"]
            modified = s.get("modified", "")

            # since フィルタ
            if since and modified < since:
                skipped += 1
                continue

            # 既にエクスポート済みか確認
            filename = f"session_{cid[:12]}_{modified[:10]}.md"
            filepath = os.path.join(output_dir, filename)
            if os.path.exists(filepath):
                skipped += 1
                continue

            # 会話を取得
            try:
                conv = self.session_read(cid, max_turns=50, full=True)
            except Exception:
                skipped += 1
                continue

            # Markdown 生成
            lines = [
                f"# Session {cid[:12]}",
                f"",
                f"- **Cascade ID**: `{cid}`",
                f"- **Modified**: {modified}",
                f"- **Steps**: {conv.get('total_steps', 0)}",
                f"- **Summary**: {conv.get('summary', '(none)')}",
                f"",
                f"---",
                f"",
            ]

            for turn in conv.get("conversation", []):
                role = turn.get("role", "")
                if role == "user":
                    lines.append(f"## 👤 User\n")
                    lines.append(turn.get("content", ""))
                    lines.append("")
                elif role == "assistant":
                    model = turn.get("model", "")
                    lines.append(f"## 🤖 Assistant ({model})\n")
                    lines.append(turn.get("content", ""))
                    lines.append("")
                elif role == "tool":
                    tool = turn.get("tool", "")
                    lines.append(f"- 🔧 `{tool}` ({turn.get('status', '')})")

            # ファイル書き出し
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            exported.append(filepath)

        return {
            "exported": exported,
            "skipped": skipped,
            "output_dir": output_dir,
        }

    # --- Internal: LS Detection ---

    # PURPOSE: [L2-auto] Language Server プロセスを検出し、接続情報を返す。
    def _detect_ls(self) -> LSInfo:
        """Language Server プロセスを検出し、接続情報を返す。

        agq-check.sh L80-117 の Python 移植。
        """
        info = LSInfo(workspace=self.workspace)

        # Step 1: ps aux から LS プロセスを検出
        try:
            ps_out = subprocess.check_output(
                ["ps", "aux"], text=True, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ps aux failed: {e}") from e

        proc_line = ""
        # Antigravity はフォルダ名のハイフンをアンダースコアに変換する
        # (e.g., synteleia-sandbox → synteleia_sandbox)
        ws_normalized = self.workspace.replace("-", "_")
        for line in ps_out.splitlines():
            if "language_server_linux" in line:
                line_normalized = line.replace("-", "_")
                if ws_normalized in line_normalized:
                    if "grep" not in line:
                        proc_line = line
                        break

        if not proc_line:
            raise RuntimeError(
                f"Language Server not found (workspace: {self.workspace})"
            )

        # PID 取得
        parts = proc_line.split()
        info.pid = int(parts[1])

        # CSRF トークン取得
        csrf_match = re.search(r"csrf_token\s+(\S+)", proc_line)
        if not csrf_match:
            raise RuntimeError("CSRF token not found in process cmdline")
        info.csrf = csrf_match.group(1)

        # Step 2: ss からリスニングポートを取得
        try:
            ss_out = subprocess.check_output(
                ["ss", "-tlnp"], text=True, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            ss_out = ""

        ports = set()
        for line in ss_out.splitlines():
            if f"pid={info.pid}" in line:
                port_match = re.search(r"127\.0\.0\.1:(\d+)", line)
                if port_match:
                    ports.add(int(port_match.group(1)))

        if not ports:
            raise RuntimeError(f"No listening ports for PID {info.pid}")

        info.all_ports = sorted(ports)

        # Step 3: 全ポート試行 → GetUserStatus 成功で確定
        for port in info.all_ports:
            try:
                result = self._raw_rpc(port, info.csrf, RPC_GET_STATUS, {
                    "metadata": {
                        "ideName": "antigravity",
                        "extensionName": "antigravity",
                        "locale": "en",
                    }
                })
                if "userStatus" in result:
                    info.port = port
                    return info
            except Exception:
                continue

        raise RuntimeError(
            f"All ports failed ({info.all_ports}) for GetUserStatus"
        )

    # --- Internal: 4-Step Flow ---

    # CortexTrajectorySource enum (from extension.js proto3 定義):
    #   0=UNSPECIFIED, 1=CASCADE_CLIENT, 2=EXPLAIN_PROBLEM,
    #   12=INTERACTIVE_CASCADE (IDE 標準), 15=SDK
    SOURCE_INTERACTIVE_CASCADE = 12

    # PURPOSE: [L2-auto] Step 1: StartCascade → cascade_id を取得。
    def _start_cascade(self) -> str:
        """Step 1: StartCascade → cascade_id を取得。"""
        result = self._rpc(RPC_START_CASCADE, {
            "source": self.SOURCE_INTERACTIVE_CASCADE,
        })
        cascade_id = result.get("cascadeId", "")
        if not cascade_id:
            raise RuntimeError(f"StartCascade returned no cascadeId: {result}")
        return cascade_id

    # PURPOSE: [L2-auto] Step 2: SendUserCascadeMessage → メッセージ送信。
    def _send_message(self, cascade_id: str, message: str, model: str) -> None:
        """Step 2: SendUserCascadeMessage → メッセージ送信。

        walkthrough.md の実証済み curl 構造に準拠:
        - items: トップレベルに直接配置
        - cascadeConfig.plannerConfig: conversational + planModel
        """
        self._rpc(RPC_SEND_MESSAGE, {
            "cascadeId": cascade_id,
            "items": [{"text": message}],
            "cascadeConfig": {
                "plannerConfig": {
                    "conversational": {},
                    "planModel": model,
                },
            },
        })

    # PURPOSE: [L2-auto] Step 3-4: ポーリングで LLM 応答を取得。
    def _poll_response(
        self, cascade_id: str, timeout: float
    ) -> LLMResponse:
        """Step 3-4: ポーリングで LLM 応答を取得。

        walkthrough.md の構造:
        - GetAllCascadeTrajectories: trajectorySummaries[cascadeId].trajectoryId
        - GetCascadeTrajectorySteps: cascadeId + trajectoryId が必須
        """
        start_time = time.time()
        trajectory_id = ""

        while time.time() - start_time < timeout:
            # Step 3: trajectory_id を取得
            if not trajectory_id:
                try:
                    trajs = self._rpc(RPC_GET_TRAJECTORIES, {})
                    # Response: {"trajectorySummaries": {"<cascadeId>": {...}}}
                    summaries = trajs.get("trajectorySummaries", {})
                    cascade_summary = summaries.get(cascade_id, {})
                    if cascade_summary:
                        trajectory_id = cascade_summary.get(
                            "trajectoryId", ""
                        )
                except Exception:
                    pass

            # Step 4: trajectory のステップを取得
            if trajectory_id:
                try:
                    steps_result = self._rpc(RPC_GET_STEPS, {
                        "cascadeId": cascade_id,
                        "trajectoryId": trajectory_id,
                    })
                    steps = steps_result.get("steps", [])
                    turn_state = steps_result.get("turnState", "")

                    # PLANNER_RESPONSE ステップが存在し、状態が完了を示す
                    has_response = any(
                        s.get("type") == "CORTEX_STEP_TYPE_PLANNER_RESPONSE"
                        and s.get("status") == "CORTEX_STEP_STATUS_DONE"
                        for s in steps
                    )
                    # turnState: "" (空) or "TURN_STATE_WAITING_FOR_USER"
                    is_done = turn_state in (
                        "", "TURN_STATE_WAITING_FOR_USER",
                    )
                    if has_response and is_done:
                        return self._parse_steps(
                            steps, cascade_id, trajectory_id
                        )
                except Exception:
                    pass

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(
            f"LLM response timed out after {timeout}s "
            f"(cascade_id={cascade_id})"
        )

    # PURPOSE: [L2-auto] ステップから LLM 応答をパースする。
    def _parse_steps(
        self,
        steps: list,
        cascade_id: str,
        trajectory_id: str,
    ) -> LLMResponse:
        """ステップから LLM 応答をパースする。

        walkthrough.md の構造:
        - type: CORTEX_STEP_TYPE_PLANNER_RESPONSE
        - plannerResponse: {response, thinking, generatorModel, ...}
        """
        response = LLMResponse(
            cascade_id=cascade_id,
            trajectory_id=trajectory_id,
            raw_steps=steps,
        )

        for step in steps:
            step_type = step.get("type", "")
            if step_type == "CORTEX_STEP_TYPE_PLANNER_RESPONSE":
                pr = step.get("plannerResponse", {})
                if "response" in pr:
                    response.text += pr["response"]
                if "thinking" in pr:
                    response.thinking += pr["thinking"]
                if "generatorModel" in pr:
                    response.model = pr["generatorModel"]
                if "tokenUsage" in pr:
                    response.token_usage = pr["tokenUsage"]

        return response

    # --- Internal: HTTP/RPC ---

    # PURPOSE: [L2-auto] ConnectRPC JSON で RPC を呼び出す。
    def _rpc(self, endpoint: str, payload: dict) -> dict:
        """ConnectRPC JSON で RPC を呼び出す。"""
        return self._raw_rpc(self.ls.port, self.ls.csrf, endpoint, payload)

    # PURPOSE: [L2-auto] 低レベル RPC 呼び出し。
    def _raw_rpc(
        self, port: int, csrf: str, endpoint: str, payload: dict
    ) -> dict:
        """低レベル RPC 呼び出し。"""
        url = f"https://127.0.0.1:{port}/{endpoint}"
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Codeium-Csrf-Token": csrf,
                "Connect-Protocol-Version": "1",
                "User-Agent": USER_AGENT,
            },
        )

        with urllib.request.urlopen(req, context=self._ssl_ctx, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)

    # --- Internal: Utilities ---

    @staticmethod
    # PURPOSE: [L2-auto] 自己署名証明書を許可する SSL コンテキスト。
    def _make_ssl_context() -> ssl.SSLContext:
        """自己署名証明書を許可する SSL コンテキスト。"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    @staticmethod
    # PURPOSE: [L2-auto] 現在のユーザー名を取得。
    def _get_user() -> str:
        """現在のユーザー名を取得。"""
        import os
        return os.environ.get("USER", "makaron8426")
