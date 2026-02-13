# PROOF: [L2/Hodos] <- mekhane/ochema/proto.py
# PURPOSE: ConnectRPC Protocol Definitions (v8)
# REASON: Centralize protocol constants and builders to avoid duplication.
"""
Antigravity ConnectRPC Protocol Definitions (v8).

Contains constants, enums, and request builders for interacting with the
Antigravity Language Server via ConnectRPC.
"""

import json
from typing import Dict, Any, List

# --- Constants ---

DEFAULT_MODEL = "MODEL_CLAUDE_4_5_SONNET_THINKING"
DEFAULT_TIMEOUT = 120.0
POLL_INTERVAL = 0.5

# RPC Endpoints
RPC_START_CASCADE = "antigravity.cortex.v1.CortexService/StartCascade"
RPC_SEND_MESSAGE = "antigravity.cortex.v1.CortexService/SendUserCascadeMessage"
RPC_GET_TRAJECTORIES = "antigravity.cortex.v1.CortexService/GetAllCascadeTrajectories"
RPC_GET_STEPS = "antigravity.cortex.v1.CortexService/GetCascadeTrajectorySteps"
RPC_GET_STATUS = "antigravity.user.v1.UserService/GetUserStatus"
RPC_MODEL_CONFIG = "antigravity.cortex.v1.CortexService/GetCascadeModelConfig"
RPC_EXPERIMENT_STATUS = "antigravity.experiments.v1.ExperimentsService/GetExperimentsStatus"
RPC_USER_MEMORIES = "antigravity.cortex.v1.CortexService/GetUserMemories"

# Step Types & Status
STEP_TYPE_PLANNER = "CORTEX_STEP_TYPE_PLANNER_RESPONSE"
STEP_STATUS_DONE = "CORTEX_STEP_STATUS_DONE"
TURN_STATES_DONE = ("CORTEX_TURN_STATE_DONE", "CORTEX_TURN_STATE_WAITING_FOR_USER_INPUT")


# --- Request Builders ---

# PURPOSE: StartCascade リクエストを構築。
def build_start_cascade() -> Dict[str, Any]:
    """StartCascade リクエストを構築。"""
    return {
        "filesContext": {"activeFile": {"path": ""}},
        "isHeadless": True,
    }


# PURPOSE: SendUserCascadeMessage リクエストを構築。
def build_send_message(cascade_id: str, message: str, model: str) -> Dict[str, Any]:
    """SendUserCascadeMessage リクエストを構築。"""
    return {
        "cascadeId": cascade_id,
        "message": message,
        "model": model,
    }


# PURPOSE: GetUserStatus リクエストを構築。
def build_get_status() -> Dict[str, Any]:
    """GetUserStatus リクエストを構築。"""
    return {
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "locale": "en",
        }
    }


# PURPOSE: GetCascadeTrajectorySteps リクエストを構築。
def build_get_steps(cascade_id: str, trajectory_id: str) -> Dict[str, Any]:
    """GetCascadeTrajectorySteps リクエストを構築。"""
    return {
        "cascadeId": cascade_id,
        "trajectoryId": trajectory_id,
    }


# --- Response Parsers ---

# PURPOSE: PlannerResponse ステップから情報を抽出。
def extract_planner_response(step: Dict[str, Any]) -> Dict[str, Any]:
    """PlannerResponse ステップから情報を抽出。"""
    result = {
        "text": "",
        "thinking": "",
        "model": "",
        "token_usage": {},
    }

    if step.get("type") != STEP_TYPE_PLANNER:
        return result

    pr = step.get("plannerResponse", {})

    # テキスト応答
    if "response" in pr:
        result["text"] = pr["response"]

    # 思考過程
    if "thinking" in pr:
        result["thinking"] = pr["thinking"]

    # モデル名
    if "generatorModel" in pr:
        result["model"] = pr["generatorModel"]

    # トークン使用量
    if "usage" in pr:
        result["token_usage"] = pr["usage"]

    return result
