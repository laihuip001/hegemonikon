# PROOF: [L1/Hodos] <- mekhane/ochema/
# PURPOSE: Antigravity LS Protocol Definitions
"""Antigravity Language Server Protocol Definitions (v8).

ConnectRPC 経由で Antigravity LS と通信するためのプロトコル定義。
"""

# --- Constants ---

DEFAULT_MODEL = "MODEL_CLAUDE_4_5_SONNET_THINKING"
DEFAULT_TIMEOUT = 120.0
POLL_INTERVAL = 0.5

# ConnectRPC Endpoints
RPC_START_CASCADE = "cortex.v1.CortexService/StartCascade"
RPC_SEND_MESSAGE = "cortex.v1.CortexService/SendUserCascadeMessage"
RPC_GET_TRAJECTORIES = "cortex.v1.CortexService/GetAllCascadeTrajectories"
RPC_GET_STEPS = "cortex.v1.CortexService/GetCascadeTrajectorySteps"
RPC_GET_STATUS = "user.v1.UserService/GetUserStatus"
RPC_MODEL_CONFIG = "cascadenet.v1.CascadenetService/GetClientModelConfig"
RPC_EXPERIMENT_STATUS = "experiment.v1.ExperimentService/GetExperimentStatus"
RPC_USER_MEMORIES = "cortex.v1.CortexService/GetUserMemories"

# Step Types
STEP_TYPE_PLANNER = "CORTEX_STEP_TYPE_PLANNER_RESPONSE"
STEP_TYPE_USER = "CORTEX_STEP_TYPE_USER_REQUEST"
STEP_TYPE_MCP = "CORTEX_STEP_TYPE_MCP_TOOL"
STEP_TYPE_TOOL = "CORTEX_STEP_TYPE_TOOL_CALL"

# Step Status
STEP_STATUS_DONE = "CORTEX_STEP_STATUS_DONE"

# Turn States
TURN_STATES_DONE = (
    "CORTEX_TURN_STATE_DONE",
    "CORTEX_TURN_STATE_WAITING_FOR_USER_INPUT"
)


# --- Protocol Builders ---

# PURPOSE: [L2-auto] StartCascade ペイロードを構築。
def build_start_cascade() -> dict:
    """StartCascade ペイロードを構築。"""
    return {
        "is_interactive": True,
        "source": 12,  # SOURCE_INTERACTIVE_CASCADE
        "files_context": [],
    }


# PURPOSE: [L2-auto] SendUserCascadeMessage ペイロードを構築。
def build_send_message(cascade_id: str, message: str, model: str) -> dict:
    """SendUserCascadeMessage ペイロードを構築。"""
    return {
        "cascade_id": cascade_id,
        "message": {
            "metadata": {},
            "items": [
                {
                    "text": message,
                    "type": "CORTEX_PART_TYPE_TEXT",
                }
            ],
        },
        "model": model,
        "regenerate_trajectory_id": "",
    }


# PURPOSE: [L2-auto] GetUserStatus ペイロードを構築。
def build_get_status() -> dict:
    """GetUserStatus ペイロードを構築。"""
    return {
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "locale": "en",
        }
    }


# PURPOSE: [L2-auto] GetCascadeTrajectorySteps ペイロードを構築。
def build_get_steps(cascade_id: str, trajectory_id: str) -> dict:
    """GetCascadeTrajectorySteps ペイロードを構築。"""
    return {
        "cascadeId": cascade_id,
        "trajectoryId": trajectory_id,
    }


# --- Response Parsers ---

# PURPOSE: [L2-auto] PlannerResponse ステップから情報を抽出。
def extract_planner_response(step: dict) -> dict:
    """PlannerResponse ステップから情報を抽出。"""
    resp = step.get("plannerResponse", {})
    return {
        "text": resp.get("response", ""),
        "thinking": resp.get("thinking", ""),
        "model": resp.get("generatorModel", ""),
        "token_usage": resp.get("usage", {}),
    }
