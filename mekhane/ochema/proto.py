# PROOF: [L2/Antigravity] <- mekhane/ochema/ Antigravity Protocol Constants
# PURPOSE: ConnectRPC/JSON プロトコルの定数定義
"""Protocol Constants for Antigravity Language Server.

ConnectRPC over HTTP/2 (JSON) のエンドポイント定義と
リクエスト構築ヘルパー。
"""

from typing import Dict, Any, List

# --- Constants ---

DEFAULT_MODEL = "MODEL_CLAUDE_4_5_SONNET_THINKING"
DEFAULT_TIMEOUT = 120.0
POLL_INTERVAL = 0.5

# RPC Endpoints
RPC_START_CASCADE = "cortex.v1.CortexService/StartCascade"
RPC_SEND_MESSAGE = "cortex.v1.CortexService/SendUserCascadeMessage"
RPC_GET_TRAJECTORIES = "cortex.v1.CortexService/GetAllCascadeTrajectories"
RPC_GET_STEPS = "cortex.v1.CortexService/GetCascadeTrajectorySteps"
RPC_GET_STATUS = "cortex.v1.CortexService/GetUserStatus"
RPC_MODEL_CONFIG = "cortex.v1.CortexService/GetModelConfig"
RPC_EXPERIMENT_STATUS = "cortex.v1.CortexService/GetExperimentStatus"
RPC_USER_MEMORIES = "cortex.v1.CortexService/GetUserMemories"

# Step Types (from proto definitions)
STEP_TYPE_PLANNER = "CORTEX_STEP_TYPE_PLANNER_RESPONSE"
STEP_STATUS_DONE = "CORTEX_STEP_STATUS_DONE"
TURN_STATES_DONE = ["CORTEX_TURN_STATE_DONE", "CORTEX_TURN_STATE_ERROR"]

# --- Helpers ---

def build_start_cascade(profile_name: str = "default") -> Dict[str, Any]:
    """StartCascade リクエストボディを構築"""
    return {
        "profileName": profile_name,
        "metadata": {}
    }

def build_send_message(cascade_id: str, message: str, model: str) -> Dict[str, Any]:
    """SendUserCascadeMessage リクエストボディを構築"""
    return {
        "cascadeId": cascade_id,
        "message": message,
        "model": model
    }

def build_get_status() -> Dict[str, Any]:
    """GetUserStatus リクエストボディを構築"""
    return {
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "locale": "en",
        }
    }

def build_get_steps(cascade_id: str, trajectory_id: str) -> Dict[str, Any]:
    """GetCascadeTrajectorySteps リクエストボディを構築"""
    return {
        "cascadeId": cascade_id,
        "trajectoryId": trajectory_id
    }

def extract_planner_response(step: Dict[str, Any]) -> Dict[str, Any]:
    """PLANNER_RESPONSE ステップから応答を抽出"""
    pr = step.get("plannerResponse", {})
    return {
        "text": pr.get("response", ""),
        "thinking": pr.get("thinking", ""),
        "model": pr.get("generatorModel", ""),
        "token_usage": pr.get("tokenUsage", {})
    }
