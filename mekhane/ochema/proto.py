# PROOF: P2 (Hodos) mekhane/ochema/proto.py
# PURPOSE: Antigravity LS の ConnectRPC proto 定義を一元管理する
# REASON: scripts/ (実験) と ochema/ (正式) が同じ v8 proto 知識を共有し、
#         Creator が proto を更新するとき 1 箇所だけ変えれば済むようにする
"""Antigravity Language Server — Proto Definitions (v8).

LS の ConnectRPC JSON エンドポイント、ペイロード構造、モデル定数を定義。
Cortex API リバースエンジニアリングの成果を集約する単一ソース。

WARNING: ToS グレーゾーン。実験用途限定。公開禁止。
"""

from __future__ import annotations


# --- RPC Endpoints ---

RPC_BASE = "exa.language_server_pb.LanguageServerService"

# Core 4-Step Flow
RPC_START_CASCADE = f"{RPC_BASE}/StartCascade"
RPC_SEND_MESSAGE = f"{RPC_BASE}/SendUserCascadeMessage"
RPC_GET_TRAJECTORIES = f"{RPC_BASE}/GetAllCascadeTrajectories"
RPC_GET_STEPS = f"{RPC_BASE}/GetCascadeTrajectorySteps"

# Status & Config
RPC_GET_STATUS = f"{RPC_BASE}/GetUserStatus"
RPC_MODEL_CONFIG = f"{RPC_BASE}/GetCascadeModelConfigData"
RPC_EXPERIMENT_STATUS = f"{RPC_BASE}/GetStaticExperimentStatus"
RPC_USER_MEMORIES = f"{RPC_BASE}/GetUserMemories"


# --- IDE Metadata (v8) ---

IDE_METADATA = {
    "ideName": "antigravity",
    "ideVersion": "1.98.0",
    "extensionVersion": "2.23.0",
}

# CortexTrajectorySource enum (from extension.js proto3)
#   0=UNSPECIFIED, 1=CASCADE_CLIENT, 2=EXPLAIN_PROBLEM,
#   12=INTERACTIVE_CASCADE (IDE default), 15=SDK
SOURCE_INTERACTIVE_CASCADE = 12

# v8: trajectoryType (必須)
TRAJECTORY_TYPE = 17


# --- Model Constants ---

DEFAULT_MODEL = "MODEL_CLAUDE_4_5_SONNET_THINKING"

# Human-friendly aliases → proto enum
MODEL_ALIASES = {
    "claude-sonnet": "MODEL_CLAUDE_4_5_SONNET_THINKING",
    "claude-opus": "MODEL_PLACEHOLDER_M26",
    "gemini-pro": "MODEL_GEMINI_2_5_PRO",
    "gemini-flash": "MODEL_GEMINI_2_5_FLASH",
    "gpt-4.1": "MODEL_GPT_4_1",
}

# Timing
DEFAULT_TIMEOUT = 120  # seconds
POLL_INTERVAL = 1.0  # seconds


# --- Payload Builders (v8) ---

def build_start_cascade() -> dict:
    """StartCascade ペイロードを構築する。

    v8: metadata + trajectoryType:17 が必須。
    これがないと trajectory が生成されない。
    """
    return {
        "metadata": IDE_METADATA.copy(),
        "source": SOURCE_INTERACTIVE_CASCADE,
        "trajectoryType": TRAJECTORY_TYPE,
    }


def build_send_message(cascade_id: str, text: str, model: str) -> dict:
    """SendUserCascadeMessage ペイロードを構築する。

    v8 実証済み curl 構造に準拠:
    - items: トップレベルに直接配置
    - plannerTypeConfig: {conversational: {}}
    - requestedModel: {model: "MODEL_..."} (proto enum 形式)
    """
    return {
        "cascadeId": cascade_id,
        "items": [{"text": text}],
        "cascadeConfig": {
            "plannerConfig": {
                "plannerTypeConfig": {"conversational": {}},
                "requestedModel": {"model": model},
            },
        },
    }


def build_get_status() -> dict:
    """GetUserStatus ペイロードを構築する。"""
    return {
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "locale": "en",
        },
    }


def build_get_steps(cascade_id: str, trajectory_id: str) -> dict:
    """GetCascadeTrajectorySteps ペイロードを構築する。"""
    return {
        "cascadeId": cascade_id,
        "trajectoryId": trajectory_id,
    }


# --- Response Parsing Helpers ---

# Step types
STEP_TYPE_PLANNER = "CORTEX_STEP_TYPE_PLANNER_RESPONSE"
STEP_STATUS_DONE = "CORTEX_STEP_STATUS_DONE"

# Turn states indicating completion
TURN_STATES_DONE = ("", "TURN_STATE_WAITING_FOR_USER")


def extract_planner_response(step: dict) -> dict:
    """PLANNER_RESPONSE ステップからテキスト・thinking・model を抽出する。

    v8: generatorModel は step.metadata に格納 (fallback: plannerResponse)

    Returns:
        {text, thinking, model, token_usage, status}
    """
    pr = step.get("plannerResponse", {})
    step_metadata = step.get("metadata", {})

    # v8: model location migration
    model = step_metadata.get("generatorModel", "")
    if not model:
        model = pr.get("generatorModel", "")  # fallback

    return {
        "text": pr.get("response", "") or pr.get("modifiedResponse", ""),
        "thinking": pr.get("thinking", ""),
        "model": model,
        "token_usage": pr.get("tokenUsage", {}),
        "status": step.get("status", ""),
    }


def resolve_model(name: str) -> str:
    """モデルエイリアスを proto enum に解決する。"""
    if name in MODEL_ALIASES:
        return MODEL_ALIASES[name]
    if name.startswith("MODEL_"):
        return name
    # Fuzzy match
    lower = name.lower()
    for alias, model_id in MODEL_ALIASES.items():
        if lower in alias:
            return model_id
    return name  # Pass through, let the API validate
