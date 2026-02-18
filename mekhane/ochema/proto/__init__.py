# Re-export all symbols from the sibling proto.py module
# This is needed because Python resolves `mekhane.ochema.proto` to this
# package (proto/) rather than the file (proto.py).
import importlib.util as _ilu
import os as _os

# Import the sibling proto.py directly
_proto_file = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "proto.py")
_spec = _ilu.spec_from_file_location("mekhane.ochema._proto_module", _proto_file)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export proto.py symbols used by antigravity_client.py, claude_cli.py, etc.
DEFAULT_MODEL = _mod.DEFAULT_MODEL
DEFAULT_TIMEOUT = _mod.DEFAULT_TIMEOUT
POLL_INTERVAL = _mod.POLL_INTERVAL
MODEL_ALIASES = _mod.MODEL_ALIASES
RPC_BASE = _mod.RPC_BASE
RPC_START_CASCADE = _mod.RPC_START_CASCADE
RPC_SEND_MESSAGE = _mod.RPC_SEND_MESSAGE
RPC_GET_TRAJECTORIES = _mod.RPC_GET_TRAJECTORIES
RPC_GET_STEPS = _mod.RPC_GET_STEPS
RPC_GET_STATUS = _mod.RPC_GET_STATUS
RPC_MODEL_CONFIG = _mod.RPC_MODEL_CONFIG
RPC_EXPERIMENT_STATUS = _mod.RPC_EXPERIMENT_STATUS
RPC_USER_MEMORIES = _mod.RPC_USER_MEMORIES
IDE_METADATA = _mod.IDE_METADATA
SOURCE_INTERACTIVE_CASCADE = _mod.SOURCE_INTERACTIVE_CASCADE
TRAJECTORY_TYPE = _mod.TRAJECTORY_TYPE
STEP_TYPE_PLANNER = _mod.STEP_TYPE_PLANNER
STEP_STATUS_DONE = _mod.STEP_STATUS_DONE
TURN_STATES_DONE = _mod.TURN_STATES_DONE

build_start_cascade = _mod.build_start_cascade
build_send_message = _mod.build_send_message
build_get_status = _mod.build_get_status
build_get_steps = _mod.build_get_steps
extract_planner_response = _mod.extract_planner_response
resolve_model = _mod.resolve_model
