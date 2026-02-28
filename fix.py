import re

with open("mekhane/fep/derivative_selector.py", "r") as f:
    content = f.read()

# Fix the bug with encode_for_derivative_selection. It IS defined in derivative_selector.py, but maybe it was declared AFTER `encode_derivative_context` in my patch.
# My patch was inserted where `update_derivative_selector` was, which is line 2850.
# `encode_for_derivative_selection` is defined at line 1176. So it is NOT hallucinated and IS available. The reviewer was wrong about the NameError, it's just that they didn't see the import/definition in the patch diff! Oh wait, maybe `encode_derivative_context` needs to use it properly. Let's check.
# "The most critical issue is that it relies on a hallucinated helper function, encode_for_derivative_selection... The patch fails to provide a working solution... Calling it will result in a runtime NameError."
# If `encode_for_derivative_selection` is in the same file, calling it is totally fine. But the reviewer thought it was missing.

# Math bug:
# Reviewer: "In a proper Dirichlet formulation, updates are applied to a matrix of prior counts (a), which is then normalized to get probabilities (A). The patch instead stores the normalized probability matrix directly and adds 1.0 (or -0.5) to it. Because the column is renormalized after every update, a single success=True update will cut the probability mass of all historical observations roughly in half, leading to catastrophic forgetting of previously learned preferences."
# So I should save the unnormalized prior counts `pA` instead of the normalized probabilities.

# I will rewrite `update_derivative_selector` to use a `pA_O1.npy` matrix.

new_code = """
# -----------------------------------------------------------------------------
# FEP Integration for Derivative Selection
# -----------------------------------------------------------------------------
DERIVATIVE_FEP_DIR = SELECTION_LOG_PATH.parent / "derivative_fep"

# PURPOSE: Encode text context to a flat observation index (0-26).
def encode_derivative_context(problem_text: str, theorem: str) -> int:
    \"\"\"Encode text context to a flat observation index (0-26).\"\"\"
    abs_lvl, ctx_dep, ref_need = encode_for_derivative_selection(problem_text, theorem)
    # Ensure values are within 0-2 bounds just in case
    abs_lvl = max(0, min(2, abs_lvl))
    ctx_dep = max(0, min(2, ctx_dep))
    ref_need = max(0, min(2, ref_need))
    return abs_lvl * 9 + ctx_dep * 3 + ref_need

# PURPOSE: Map a derivative string to its state index (0-2).
def _get_derivative_index(theorem: str, derivative: str) -> int:
    \"\"\"Map a derivative string to its state index (0-2).\"\"\"
    derivatives = list_derivatives(theorem)
    if not derivatives:
        raise ValueError(f"Unknown theorem: {theorem}")
    if derivative not in derivatives:
        raise ValueError(f"Derivative '{derivative}' not valid for theorem '{theorem}'")
    return derivatives.index(derivative)

# PURPOSE: Record feedback for derivative selection learning.
def update_derivative_selector(
    theorem: str, derivative: str, problem_context: str, success: bool
) -> None:
    \"\"\"
    Record feedback for derivative selection learning.

    Future enhancement: integrate with Dirichlet learning in FEP agent
    to improve derivative selection based on outcomes.

    Args:
        theorem: O-series theorem
        derivative: Selected derivative
        problem_context: Problem description
        success: Whether the derivative was effective
    \"\"\"
    # 1. Derivative-specific state space in FEP (3 states per theorem)
    num_states = len(list_derivatives(theorem))
    if num_states == 0:
        return

    # 2. Observation encoding for derivative context (27 possible observations)
    num_obs = 27
    obs_idx = encode_derivative_context(problem_context, theorem)

    try:
        state_idx = _get_derivative_index(theorem, derivative)
    except ValueError:
        return

    # 3. Persistence of learned derivative preferences (Unnormalized Dirichlet counts pA)
    DERIVATIVE_FEP_DIR.mkdir(parents=True, exist_ok=True)
    pa_matrix_path = DERIVATIVE_FEP_DIR / f"pA_{theorem}.npy"

    # Initialize with uniform prior concentration parameters (e.g., 1.0)
    if pa_matrix_path.exists():
        pA_matrix = np.load(str(pa_matrix_path))
        # Validate shape in case states/obs definitions change
        if pA_matrix.shape != (num_obs, num_states):
            pA_matrix = np.ones((num_obs, num_states))
    else:
        pA_matrix = np.ones((num_obs, num_states))

    # Update logic (Dirichlet)
    # If success=True, increase count. We only do positive reinforcement.
    # The FEP learning rule pA += eta * outer(o, s).
    # Negative updates to Dirichlet parameters are mathematically unsound and can lead to <=0 counts.
    if success:
        eta = 50.0  # standard learning rate used in HegemonikónFEPAgent

        obs_vector = np.zeros(num_obs)
        obs_vector[obs_idx] = 1.0

        state_vector = np.zeros(num_states)
        state_vector[state_idx] = 1.0

        update = eta * np.outer(obs_vector, state_vector)

        pA_matrix += update

        np.save(str(pa_matrix_path), pA_matrix)
"""

# Need to replace the old block from my first patch
content = re.sub(
    r"# -----------------------------------------------------------------------------\n# FEP Integration for Derivative Selection\n# -----------------------------------------------------------------------------.*?np\.save\(str\(a_matrix_path\), A_matrix\)",
    new_code.strip(),
    content,
    flags=re.DOTALL
)

with open("mekhane/fep/derivative_selector.py", "w") as f:
    f.write(content)
