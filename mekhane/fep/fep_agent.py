# PROOF: [L1/定理] <- mekhane/fep/
"""
PROOF: [L1/定理] このファイルは存在しなければならない

A0 → FEP (予測誤差最小化) が核である
   → FEP を実装するエージェントが必要
   → Active Inference エージェントが担う

Q.E.D.

---

Hegemonikón FEP Agent

Active Inference agent wrapping pymdp for cognitive processes.

Implements:
- O1 Noēsis: State inference (belief updating)
- O2 Boulēsis: Policy selection (expected free energy minimization)

References:
- pymdp documentation: https://pymdp-rtd.readthedocs.io
- Active Inference KI
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

try:
    from pymdp.agent import Agent
    from pymdp import utils

    PYMDP_AVAILABLE = True
except ImportError:
    PYMDP_AVAILABLE = False
    Agent = None
    utils = None

from .state_spaces import (
    PHANTASIA_STATES,
    ASSENT_STATES,
    HORME_STATES,
    OBSERVATION_MODALITIES,
    get_state_dim,
    index_to_state,
)
from .config import get_default_params


class HegemonikónFEPAgent:
    """Active Inference agent for Hegemonikón cognitive processes.

    Maps Stoic philosophy concepts to FEP:
    - Phantasia (Impression) -> Prior belief P(s)
    - Assent (Syncatasthesis) -> Belief update Q(s)
    - Hormē (Impulse) -> Action selection π*
    - Prohairesis (Will) -> Policy selection minimizing G(π)

    Attributes:
        agent: Underlying pymdp Agent
        state_dim: Total number of hidden states
        obs_dims: Dimension of each observation modality
        beliefs: Current belief distribution over states
    """

    def __init__(
        self,
        A: Optional[np.ndarray] = None,
        B: Optional[np.ndarray] = None,
        C: Optional[np.ndarray] = None,
        D: Optional[np.ndarray] = None,
        use_defaults: bool = True,
        state_dim: Optional[int] = None,
        obs_dims: Optional[Dict[str, int]] = None,
    ):
        """Initialize the FEP agent.

        Args:
            A: Observation likelihood matrix P(o|s). Shape: (num_obs, num_states)
            B: State transition matrix P(s'|s,a). Shape: (num_states, num_states, num_actions)
            C: Preference vector over observations. Shape: (num_obs,)
            D: Initial state belief (prior). Shape: (num_states,)
            use_defaults: If True and matrices not provided, use default Hegemonikón matrices
            state_dim: Optional override for state dimension
            obs_dims: Optional override for observation dimensions

        Raises:
            ImportError: If pymdp is not available
        """
        if not PYMDP_AVAILABLE:
            raise ImportError("pymdp is not installed. Install with: pip install pymdp")

        self.state_dim = state_dim if state_dim is not None else get_state_dim()
        self.obs_dims = (
            obs_dims
            if obs_dims is not None
            else {k: len(v) for k, v in OBSERVATION_MODALITIES.items()}
        )

        # Use provided matrices or generate defaults
        if use_defaults:
            A = A if A is not None else self._default_A()
            B = B if B is not None else self._default_B()
            C = C if C is not None else self._default_C()
            D = D if D is not None else self._default_D()

        # Initialize pymdp Agent with 2-step policy horizon (arXiv:2412.10425 pattern)
        # policy_len=2: Evaluate policies over 2 future timesteps
        # inference_horizon=1: Single-step inference for belief updating
        self.agent = Agent(
            A=A,
            B=B,
            C=C,
            D=D,
            policy_len=2,
            inference_horizon=1,
        )
        self.beliefs = (
            D.copy() if D is not None else np.ones(self.state_dim) / self.state_dim
        )

        # Learning parameters (from arXiv:2412.10425)
        self.learning_rate = 50.0  # η for Dirichlet updates

        # Track history for analysis
        self._history: List[Dict[str, Any]] = []

    def _default_A(self) -> np.ndarray:
        """Generate Hegemonikón-optimized observation likelihood matrix.

        Maps hidden states to expected observations based on Stoic philosophy:
        - Clear phantasia → clear context observation
        - Granted assent → high confidence observation
        - Active hormē → higher urgency observation

        Returns:
            A matrix of shape (num_obs, num_states)
        """
        # Observation order: context(2) + urgency(3) + confidence(3) = 8
        num_obs = sum(self.obs_dims.values())  # 8
        A = np.zeros((num_obs, self.state_dim))

        # Iterate through all 8 hidden states
        for state_idx in range(self.state_dim):
            phantasia, assent, horme = index_to_state(state_idx)

            obs_idx = 0  # Running observation index

            # Context observation (indices 0-1): depends on phantasia
            if phantasia == "clear":
                A[1, state_idx] = 0.9  # clear context
                A[0, state_idx] = 0.1  # ambiguous
            else:  # uncertain
                A[0, state_idx] = 0.7  # ambiguous
                A[1, state_idx] = 0.3  # clear
            obs_idx += 2

            # Urgency observation (indices 2-4): depends on hormē
            if horme == "active":
                A[obs_idx + 0, state_idx] = 0.1  # low
                A[obs_idx + 1, state_idx] = 0.3  # medium
                A[obs_idx + 2, state_idx] = 0.6  # high
            else:  # passive
                A[obs_idx + 0, state_idx] = 0.6  # low
                A[obs_idx + 1, state_idx] = 0.3  # medium
                A[obs_idx + 2, state_idx] = 0.1  # high
            obs_idx += 3

            # Confidence observation (indices 5-7): depends on assent
            if assent == "granted":
                A[obs_idx + 0, state_idx] = 0.1  # low
                A[obs_idx + 1, state_idx] = 0.2  # medium
                A[obs_idx + 2, state_idx] = 0.7  # high
            else:  # withheld (Epochē)
                A[obs_idx + 0, state_idx] = 0.5  # low
                A[obs_idx + 1, state_idx] = 0.4  # medium
                A[obs_idx + 2, state_idx] = 0.1  # high

        # Normalize columns
        A = A / A.sum(axis=0, keepdims=True)
        return A

    def _default_B(self) -> np.ndarray:
        """Generate Hegemonikón-optimized state transition matrix.

        Actions:
        - 0: observe (O1 Noēsis) → clarifies phantasia, tends toward passive
        - 1: act (O4 Energeia) → grants assent, activates hormē

        Returns:
            B matrix of shape (num_states, num_states, num_actions)
        """
        num_actions = 2
        B = np.zeros((self.state_dim, self.state_dim, num_actions))

        for from_idx in range(self.state_dim):
            from_p, from_a, from_h = index_to_state(from_idx)

            for to_idx in range(self.state_dim):
                to_p, to_a, to_h = index_to_state(to_idx)

                # Action 0: observe (clarify, suspend, calm)
                p_observe = 1.0
                if from_p == "uncertain" and to_p == "clear":
                    p_observe *= 0.6  # Observation clarifies
                elif from_p == "clear" and to_p == "clear":
                    p_observe *= 0.8  # Clarity maintained
                elif from_p == "uncertain" and to_p == "uncertain":
                    p_observe *= 0.4
                else:
                    p_observe *= 0.1

                if from_a == "granted" and to_a == "withheld":
                    p_observe *= 0.3  # Observation can induce Epochē
                elif to_a == "withheld":
                    p_observe *= 0.6  # Tends toward suspension
                else:
                    p_observe *= 0.4

                if to_h == "passive":
                    p_observe *= 0.7  # Observation calms
                else:
                    p_observe *= 0.3

                B[to_idx, from_idx, 0] = p_observe

                # Action 1: act (commit, engage)
                p_act = 1.0
                if to_p == from_p:
                    p_act *= 0.6  # Phantasia unchanged
                elif to_p == "clear":
                    p_act *= 0.3  # Action may clarify
                else:
                    p_act *= 0.1

                if to_a == "granted":
                    p_act *= 0.7  # Acting implies assent
                else:
                    p_act *= 0.3

                if to_h == "active":
                    p_act *= 0.8  # Action activates
                else:
                    p_act *= 0.2

                B[to_idx, from_idx, 1] = p_act

        # Normalize columns for each action
        for a in range(num_actions):
            col_sums = B[:, :, a].sum(axis=0, keepdims=True)
            col_sums[col_sums == 0] = 1  # Avoid division by zero
            B[:, :, a] = B[:, :, a] / col_sums

        return B

    def _default_C(self) -> np.ndarray:
        """Generate Hegemonikón-optimized preference vector.

        Based on PREFERENCES from state_spaces.py:
        - Clear context: +2.0 (Zero Entropy principle)
        - Ambiguous context: -2.0
        - High confidence: +1.5
        - Low confidence: -1.0 (Epochē trigger)

        Returns:
            C vector of shape (num_obs,)
        """
        from .state_spaces import PREFERENCES

        C = []
        for modality, values in OBSERVATION_MODALITIES.items():
            if modality in PREFERENCES:
                for obs in values:
                    C.append(PREFERENCES[modality].get(obs, 0.0))
            else:
                C.extend([0.0] * len(values))

        return np.array(C, dtype=np.float64)

    def _default_D(self) -> np.ndarray:
        """Generate Hegemonikón-optimized initial state belief.

        Prior: Slightly prefers uncertain phantasia (epistemic humility),
        withheld assent (Epochē default), and passive hormē (prudence).

        Returns:
            D vector of shape (num_states,)
        """
        D = np.zeros(self.state_dim)

        for idx in range(self.state_dim):
            phantasia, assent, horme = index_to_state(idx)

            prob = 1.0
            # Epistemic humility: slightly prefer uncertain initially
            prob *= 0.6 if phantasia == "uncertain" else 0.4
            # Epochē default: prefer withheld assent
            prob *= 0.6 if assent == "withheld" else 0.4
            # Prudence: prefer passive initially
            prob *= 0.6 if horme == "passive" else 0.4

            D[idx] = prob

        # Normalize
        D = D / D.sum()
        return D

    def infer_states(self, observation: int) -> Dict[str, Any]:
        """O1 Noēsis: Update beliefs based on new observation.

        Performs variational inference to update the posterior distribution
        over hidden states given the new observation (Recursive Self-Evidencing).

        Args:
            observation: Index into observation space

        Returns:
            Dict containing:
                - beliefs: Updated belief distribution
                - map_state: Maximum a posteriori state
                - map_state_names: MAP state as (phantasia, assent, horme) tuple
                - entropy: Entropy of belief distribution
        """
        # pymdp expects observation as tuple/list for multi-modality
        obs_tuple = (
            (observation,) if isinstance(observation, int) else tuple(observation)
        )

        # Use pymdp agent to infer states
        self.beliefs = self.agent.infer_states(obs_tuple)

        # Handle pymdp output: object-dtype ndarray containing inner arrays
        # or list of arrays for multi-factor models
        if isinstance(self.beliefs, np.ndarray):
            if self.beliefs.dtype == object:
                # Object array containing inner array
                beliefs_array = np.asarray(self.beliefs[0], dtype=np.float64)
            else:
                beliefs_array = np.asarray(self.beliefs, dtype=np.float64)
        elif isinstance(self.beliefs, list):
            beliefs_array = np.asarray(self.beliefs[0], dtype=np.float64)
        else:
            beliefs_array = np.asarray(self.beliefs, dtype=np.float64)

        # Flatten if needed
        beliefs_array = beliefs_array.flatten()

        # Compute MAP state
        map_idx = int(np.argmax(beliefs_array))
        map_names = index_to_state(map_idx)

        # Compute entropy
        # Avoid log(0) by adding small epsilon
        eps = 1e-10
        entropy = -np.sum(beliefs_array * np.log(beliefs_array + eps))

        result = {
            "beliefs": beliefs_array,
            "map_state": map_idx,
            "map_state_names": {
                "phantasia": map_names[0],
                "assent": map_names[1],
                "horme": map_names[2],
            },
            "entropy": float(entropy),
        }

        self._history.append({"type": "infer_states", "result": result})
        return result

    def infer_policies(self) -> Tuple[np.ndarray, np.ndarray]:
        """O2 Boulēsis: Select policy minimizing expected free energy.

        Computes the expected free energy for each policy and returns
        the policy probabilities (softmax of negative EFE).

        Returns:
            Tuple of:
                - q_pi: Policy probabilities
                - neg_efe: Negative expected free energy for each policy
        """
        q_pi, neg_efe = self.agent.infer_policies()

        self._history.append(
            {
                "type": "infer_policies",
                "q_pi": q_pi,
                "neg_efe": neg_efe,
            }
        )

        return q_pi, neg_efe

    def sample_action(self) -> int:
        """Sample action from policy distribution.

        Returns:
            Sampled action index
        """
        action = self.agent.sample_action()

        # Handle case where action is an array
        if isinstance(action, np.ndarray):
            action = int(action[0])

        self._history.append({"type": "action", "action": action})
        return action

    def step(self, observation: int) -> Dict[str, Any]:
        """Complete inference-action cycle.

        Performs:
        1. O1 Noēsis: State inference
        2. O2 Boulēsis: Policy selection
        3. Action sampling

        Args:
            observation: Index into observation space

        Returns:
            Dict containing:
                - beliefs: Updated belief distribution
                - map_state_names: MAP state interpretation
                - entropy: Belief entropy
                - q_pi: Policy probabilities
                - action: Sampled action
                - action_name: Human-readable action name
        """
        # 1. Infer states (O1 Noēsis)
        state_result = self.infer_states(observation)

        # 2. Infer policies (O2 Boulēsis)
        q_pi, neg_efe = self.infer_policies()

        # 3. Sample action
        action = self.sample_action()

        # Action interpretation
        action_names = ["observe", "act"]
        action_name = (
            action_names[action] if action < len(action_names) else f"action_{action}"
        )

        return {
            "beliefs": state_result["beliefs"],
            "map_state_names": state_result["map_state_names"],
            "entropy": state_result["entropy"],
            "q_pi": q_pi,
            "neg_efe": neg_efe,
            "action": action,
            "action_name": action_name,
        }

    def get_history(self) -> List[Dict[str, Any]]:
        """Return inference history for analysis."""
        return self._history

    def reset(self):
        """Reset agent state to initial beliefs."""
        self.beliefs = self._default_D()
        self._history = []

    # =========================================================================
    # Persistence Methods (arXiv:2412.10425 pattern)
    # =========================================================================

    def save_learned_A(self, path: Optional[str] = None) -> str:
        """Save learned A matrix to file.

        Enables Dirichlet learning accumulation across sessions.
        Called automatically by /bye workflow.

        Args:
            path: Optional custom path (uses default if not specified)

        Returns:
            Path where the A matrix was saved
        """
        from .persistence import save_A, LEARNED_A_PATH
        from pathlib import Path

        target_path = Path(path) if path else None
        saved_path = save_A(self, target_path)

        self._history.append(
            {
                "type": "save_A",
                "path": str(saved_path),
            }
        )

        return str(saved_path)

    def load_learned_A(self, path: Optional[str] = None) -> bool:
        """Load A matrix from file and update agent.

        Restores learned observation model from previous sessions.
        Called automatically by /boot workflow.

        Args:
            path: Optional custom path (uses default if not specified)

        Returns:
            True if successfully loaded, False if file doesn't exist
        """
        from .persistence import load_A, A_exists, LEARNED_A_PATH
        from pathlib import Path

        target_path = Path(path) if path else None

        if not A_exists(target_path):
            return False

        loaded_A = load_A(target_path)
        if loaded_A is not None:
            self.agent.A = loaded_A

            self._history.append(
                {
                    "type": "load_A",
                    "path": str(target_path or LEARNED_A_PATH),
                }
            )
            return True

        return False

    # =========================================================================
    # Dirichlet Learning (arXiv:2412.10425 pattern)
    # =========================================================================

    def update_A_dirichlet(
        self,
        observation: int,
        learning_rate: Optional[float] = None,
    ) -> None:
        """Update A matrix using Dirichlet concentration update.

        Implements the learning rule from arXiv:2412.10425:
            pA += η * outer(observation, beliefs)

        This enables the agent to learn observation likelihoods from experience.

        Args:
            observation: The observed outcome (index or tuple of indices)
            learning_rate: Learning rate η (defaults to self.learning_rate = 50.0)

        Example:
            >>> agent.infer_states(observation=3)
            >>> agent.update_A_dirichlet(observation=3)

            # Or with tuple input (from encode_noesis_output):
            >>> obs_tuple = (1, 0, 2)  # context, urgency, confidence
            >>> agent.update_A_dirichlet(observation=obs_tuple)
        """
        eta = learning_rate if learning_rate is not None else self.learning_rate

        # Handle tuple observation input (from encode_noesis_output)
        # Convert (context_idx, urgency_idx, confidence_idx) to flat index
        if isinstance(observation, tuple):
            context_idx, urgency_idx, confidence_idx = observation
            # Compute flat observation index
            # Layout: context (2) + urgency (3) + confidence (3) = 8
            # Flat index = context + 2*urgency + confidence
            # But for A matrix we need the primary context indicator
            observation = context_idx + 2 * urgency_idx + confidence_idx

        # Get current beliefs (flattened)
        if isinstance(self.beliefs, np.ndarray):
            if self.beliefs.dtype == object:
                beliefs_array = np.asarray(self.beliefs[0], dtype=np.float64).flatten()
            else:
                beliefs_array = np.asarray(self.beliefs, dtype=np.float64).flatten()
        elif isinstance(self.beliefs, list):
            beliefs_array = np.asarray(self.beliefs[0], dtype=np.float64).flatten()
        else:
            beliefs_array = np.asarray(self.beliefs, dtype=np.float64).flatten()

        # Handle pymdp's A matrix format (may be object array containing arrays)
        A = self.agent.A
        if isinstance(A, np.ndarray) and A.dtype == object:
            # Object array: A[0] is the actual matrix
            A_matrix = np.asarray(A[0], dtype=np.float64)
        elif isinstance(A, list):
            A_matrix = np.asarray(A[0], dtype=np.float64)
        else:
            A_matrix = np.asarray(A, dtype=np.float64)

        # Create one-hot observation vector
        num_obs = A_matrix.shape[0]
        # Clamp observation to valid range
        obs_idx = min(int(observation), num_obs - 1)
        obs_vector = np.zeros(num_obs)
        obs_vector[obs_idx] = 1.0

        # Dirichlet update: pA += η * outer(o, beliefs)
        # This increases concentration parameters for observed state-observation pairs
        update = eta * np.outer(obs_vector, beliefs_array)

        # Apply update with numerical stability
        eps = 1e-10
        A_matrix = np.clip(A_matrix + update, eps, None)
        # Renormalize columns
        A_matrix = A_matrix / A_matrix.sum(axis=0, keepdims=True)

        # Write back to agent
        if isinstance(self.agent.A, np.ndarray) and self.agent.A.dtype == object:
            self.agent.A[0] = A_matrix
        elif isinstance(self.agent.A, list):
            self.agent.A[0] = A_matrix
        else:
            self.agent.A = A_matrix

        self._history.append(
            {
                "type": "dirichlet_update",
                "observation": observation,
                "learning_rate": eta,
            }
        )
