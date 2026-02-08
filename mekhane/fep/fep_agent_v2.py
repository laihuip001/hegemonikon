# PROOF: [L1/定理] <- mekhane/fep/
# PURPOSE: 48-state FEP Agent v2 — Series 統合認知モデル
"""
PROOF: [L1/定理] このファイルは存在しなければならない

A0 → FEP Agent は「何を」「どう」を統合的に判断すべき
   → Series を hidden state に組み込む
   → 48-state FEP Agent v2 が担う

Q.E.D.

---

Hegemonikón FEP Agent v2

Extends v1 by integrating Series into the generative model:
- v1: « act or observe? »      (meta-level only)
- v2: « which Series to act on? » (unified cognitive-content judgment)

State Space:
    phantasia(2) × assent(2) × horme(2) × series(6) = 48 hidden states

Observation Space:
    context(2) + urgency(3) + confidence(3) + topic(6) = 14 obs dims

Action Space:
    observe(0), act_O(1), act_S(2), act_H(3), act_P(4), act_K(5), act_A(6)
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

try:
    from pymdp.agent import Agent
    PYMDP_AVAILABLE = True
except ImportError:
    PYMDP_AVAILABLE = False
    Agent = None

from .state_spaces_v2 import (
    PHANTASIA_STATES,
    ASSENT_STATES,
    HORME_STATES,
    SERIES_STATES,
    OBSERVATION_MODALITIES_V2,
    PREFERENCES_V2,
    ACTIONS_V2,
    ACTION_TO_SERIES,
    NUM_STATES_V2,
    NUM_OBS_V2,
    NUM_ACTIONS_V2,
    get_state_dim_v2,
    index_to_state_v2,
    action_name_v2,
)


class HegemonikónFEPAgentV2:
    """48-state Active Inference Agent with Series integration.

    Maps Stoic philosophy + 6 Series to a unified generative model:
    - Phantasia → impression clarity
    - Assent → belief commitment
    - Hormē → action impulse
    - Series → cognitive domain (O/S/H/P/K/A)
    """

    def __init__(
        self,
        A: Optional[np.ndarray] = None,
        B: Optional[np.ndarray] = None,
        C: Optional[np.ndarray] = None,
        D: Optional[np.ndarray] = None,
        use_defaults: bool = True,
    ):
        if not PYMDP_AVAILABLE:
            raise ImportError("pymdp is not installed. Install with: pip install pymdp")

        self.state_dim = NUM_STATES_V2  # 48
        self.num_obs = NUM_OBS_V2       # 14
        self.num_actions = NUM_ACTIONS_V2  # 7
        self.obs_dims = {k: len(v) for k, v in OBSERVATION_MODALITIES_V2.items()}

        if use_defaults:
            A = A if A is not None else self._default_A()
            B = B if B is not None else self._default_B()
            C = C if C is not None else self._default_C()
            D = D if D is not None else self._default_D()

        self.agent = Agent(
            A=A, B=B, C=C, D=D,
            policy_len=2,
            inference_horizon=1,
        )

        self.beliefs = (
            D.copy() if D is not None
            else np.ones(self.state_dim) / self.state_dim
        )

        self.learning_rate = 50.0
        self.precision_weights: Dict[str, float] = {
            "context": 1.0, "urgency": 1.0,
            "confidence": 1.0, "topic": 1.0,
        }
        self.precision_lr: float = 0.1
        self._base_A: Optional[np.ndarray] = None
        self._history: List[Dict[str, Any]] = []

    # =========================================================================
    # A Matrix: P(observation | hidden_state) — 14 × 48
    # =========================================================================

    def _default_A(self) -> np.ndarray:
        """Generate 48-state observation likelihood matrix.

        Rows 0-1:   context (depends on phantasia)
        Rows 2-4:   urgency (depends on horme)
        Rows 5-7:   confidence (depends on assent)
        Rows 8-13:  topic (depends on series)
        """
        A = np.zeros((self.num_obs, self.state_dim))

        for s_idx in range(self.state_dim):
            phantasia, assent, horme, series = index_to_state_v2(s_idx)
            row = 0

            # --- Context (rows 0-1): phantasia ---
            if phantasia == "clear":
                A[row + 0, s_idx] = 0.1   # ambiguous
                A[row + 1, s_idx] = 0.9   # clear
            else:
                A[row + 0, s_idx] = 0.7   # ambiguous
                A[row + 1, s_idx] = 0.3   # clear
            row += 2

            # --- Urgency (rows 2-4): horme ---
            if horme == "active":
                A[row + 0, s_idx] = 0.1   # low
                A[row + 1, s_idx] = 0.3   # medium
                A[row + 2, s_idx] = 0.6   # high
            else:
                A[row + 0, s_idx] = 0.6   # low
                A[row + 1, s_idx] = 0.3   # medium
                A[row + 2, s_idx] = 0.1   # high
            row += 3

            # --- Confidence (rows 5-7): assent ---
            if assent == "granted":
                A[row + 0, s_idx] = 0.1   # low
                A[row + 1, s_idx] = 0.2   # medium
                A[row + 2, s_idx] = 0.7   # high
            else:
                A[row + 0, s_idx] = 0.5   # low
                A[row + 1, s_idx] = 0.4   # medium
                A[row + 2, s_idx] = 0.1   # high
            row += 3

            # --- Topic (rows 8-13): series ---
            #
            # This is the key innovation:
            # When the hidden state's series = X, the agent expects to
            # observe topic = X with high probability.
            #
            # P(topic=X | series=X) = 0.75 (strong signal)
            # P(topic=Y | series=X) = 0.05 (noise from other Series)
            #
            series_idx = SERIES_STATES.index(series)
            for t in range(6):
                if t == series_idx:
                    A[row + t, s_idx] = 0.75
                else:
                    A[row + t, s_idx] = 0.05
            # row += 6

        # Normalize columns
        col_sums = A.sum(axis=0, keepdims=True)
        col_sums[col_sums == 0] = 1
        A = A / col_sums
        return A

    # =========================================================================
    # B Matrix: P(s' | s, a) — 48 × 48 × 7
    # =========================================================================

    def _default_B(self) -> np.ndarray:
        """Generate 48-state transition matrix for 7 actions.

        Key insight: The agent should prefer act_X when it knows the Series.
        observe = passive waiting (state-preserving, no clarification)
        act_X = active engagement (clarifies phantasia + transitions Series)

        This makes act_X epistemically and pragmatically superior when
        topic observation provides clear Series signal.
        """
        B = np.zeros((self.state_dim, self.state_dim, self.num_actions))

        for from_idx in range(self.state_dim):
            from_p, from_a, from_h, from_s = index_to_state_v2(from_idx)

            for to_idx in range(self.state_dim):
                to_p, to_a, to_h, to_s = index_to_state_v2(to_idx)

                # --- Action 0: observe (passive waiting) ---
                # State-preserving: high inertia on ALL dimensions
                # Does NOT clarify — it's waiting, not investigating
                p = 1.0
                # Phantasia: STAYS as-is (observation alone doesn't clarify)
                p *= 0.9 if to_p == from_p else 0.1
                # Assent: stays (no decision)
                p *= 0.9 if to_a == from_a else 0.1
                # Horme: stays (no impulse change)
                p *= 0.9 if to_h == from_h else 0.1
                # Series: stays (no domain commitment)
                p *= 0.85 if to_s == from_s else 0.03

                B[to_idx, from_idx, 0] = p

                # --- Actions 1-6: act_O..act_A ---
                for act_idx in range(1, 7):
                    target_series = SERIES_STATES[act_idx - 1]

                    p = 1.0
                    # Phantasia: acting CLARIFIES (engagement reveals truth)
                    if from_p == "uncertain" and to_p == "clear":
                        p *= 0.7  # Action reveals
                    elif to_p == "clear":
                        p *= 0.6  # Maintains clarity
                    else:
                        p *= 0.2  # Rarely regresses
                    # Assent: action implies commitment
                    p *= 0.75 if to_a == "granted" else 0.25
                    # Horme: action activates
                    p *= 0.8 if to_h == "active" else 0.2
                    # Series: transitions to action's target
                    if to_s == target_series:
                        p *= 0.80
                    elif to_s == from_s:
                        p *= 0.10
                    else:
                        p *= 0.02

                    B[to_idx, from_idx, act_idx] = p

        # Normalize columns per action
        for a in range(self.num_actions):
            col_sums = B[:, :, a].sum(axis=0, keepdims=True)
            col_sums[col_sums == 0] = 1
            B[:, :, a] = B[:, :, a] / col_sums

        return B

    # =========================================================================
    # C Matrix: Preferences over observations — length 14
    # =========================================================================

    def _default_C(self) -> np.ndarray:
        """Generate preference vector over 14 observation dimensions."""
        C = []
        for modality, values in OBSERVATION_MODALITIES_V2.items():
            prefs = PREFERENCES_V2.get(modality, {})
            for obs in values:
                C.append(prefs.get(obs, 0.0))
        return np.array(C, dtype=np.float64)

    # =========================================================================
    # D Matrix: Initial prior over 48 states
    # =========================================================================

    def _default_D(self) -> np.ndarray:
        """Generate initial state belief — balanced action readiness.

        Prior:
        - Epistemic humility on phantasia (uncertain > clear)
        - Balanced assent (slight Epochē lean, not dominant)
        - Balanced horme (ready to act, not stuck in passive)
        - Uniform over Series
        """
        D = np.zeros(self.state_dim)

        for idx in range(self.state_dim):
            phantasia, assent, horme, series = index_to_state_v2(idx)

            prob = 1.0
            # Epistemic humility: prefer uncertain (humble about impressions)
            prob *= 0.6 if phantasia == "uncertain" else 0.4
            # Assent: slight lean toward withheld, but not dominant
            prob *= 0.55 if assent == "withheld" else 0.45
            # Horme: balanced — ready to act when evidence warrants it
            # (Stoic: hormē is the natural impulse toward the good)
            prob *= 0.5  # Equal for both active and passive
            # Series: uniform
            prob *= 1.0 / 6.0

            D[idx] = prob

        D = D / D.sum()
        return D

    # =========================================================================
    # Inference Cycle
    # =========================================================================

    def infer_states(self, observation: int) -> Dict[str, Any]:
        """O1 Noēsis: Update beliefs given observation."""
        obs_tuple = (
            (observation,) if isinstance(observation, int) else tuple(observation)
        )
        self.beliefs = self.agent.infer_states(obs_tuple)

        beliefs_array = self._to_beliefs_array()
        map_idx = int(np.argmax(beliefs_array))
        p, a, h, s = index_to_state_v2(map_idx)

        eps = 1e-10
        entropy = -np.sum(beliefs_array * np.log(beliefs_array + eps))

        result = {
            "beliefs": beliefs_array,
            "map_state": map_idx,
            "map_state_names": {
                "phantasia": p, "assent": a, "horme": h, "series": s,
            },
            "entropy": float(entropy),
        }
        self._history.append({"type": "infer_states", "result": result})
        return result

    def infer_policies(self) -> Tuple[np.ndarray, np.ndarray]:
        """O2 Boulēsis: Select policy minimizing EFE."""
        q_pi, neg_efe = self.agent.infer_policies()
        self._history.append({
            "type": "infer_policies", "q_pi": q_pi, "neg_efe": neg_efe,
        })
        return q_pi, neg_efe

    def sample_action(self) -> int:
        """Sample action from policy distribution."""
        action = self.agent.sample_action()
        if isinstance(action, np.ndarray):
            action = int(action[0])
        self._history.append({"type": "action", "action": action})
        return int(action)

    def step(self, observation: int) -> Dict[str, Any]:
        """Complete inference-action cycle with 7-action output.

        Returns dict with action_name in {observe, act_O, ..., act_A}
        and selected_series for act_* actions.
        """
        self._apply_precision()

        state_result = self.infer_states(observation)
        q_pi, neg_efe = self.infer_policies()

        predicted_obs = int(np.argmax(self._get_predicted_observation()))
        self.update_precision(observation, predicted_obs)

        action = self.sample_action()
        act_name = action_name_v2(action)
        selected_series = ACTION_TO_SERIES.get(act_name)

        return {
            "beliefs": state_result["beliefs"],
            "map_state_names": state_result["map_state_names"],
            "entropy": state_result["entropy"],
            "q_pi": q_pi,
            "neg_efe": neg_efe,
            "action": action,
            "action_name": act_name,
            "selected_series": selected_series,
            "precision_weights": dict(self.precision_weights),
        }

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _to_beliefs_array(self) -> np.ndarray:
        """Extract flat float64 array from pymdp beliefs."""
        b = self.beliefs
        if isinstance(b, np.ndarray):
            if b.dtype == object:
                return np.asarray(b[0], dtype=np.float64).flatten()
            return np.asarray(b, dtype=np.float64).flatten()
        if isinstance(b, list):
            return np.asarray(b[0], dtype=np.float64).flatten()
        return np.asarray(b, dtype=np.float64).flatten()

    def _get_A_matrix(self) -> np.ndarray:
        """Extract A matrix from pymdp agent."""
        A = self.agent.A
        if isinstance(A, np.ndarray) and A.dtype == object:
            return np.asarray(A[0], dtype=np.float64)
        if isinstance(A, list):
            return np.asarray(A[0], dtype=np.float64)
        return np.asarray(A, dtype=np.float64)

    def _set_A_matrix(self, A_matrix: np.ndarray) -> None:
        """Write A matrix back to pymdp agent."""
        if isinstance(self.agent.A, np.ndarray) and self.agent.A.dtype == object:
            self.agent.A[0] = A_matrix
        elif isinstance(self.agent.A, list):
            self.agent.A[0] = A_matrix
        else:
            self.agent.A = A_matrix

    def _get_predicted_observation(self) -> np.ndarray:
        """E[o] = A @ beliefs."""
        return self._get_A_matrix() @ self._to_beliefs_array()

    # =========================================================================
    # Precision Weighting
    # =========================================================================

    def update_precision(self, observed: int, predicted: int) -> None:
        """Update precision weights based on prediction error per modality."""
        obs_per_mod = self._decompose_observation(observed)
        pred_per_mod = self._decompose_observation(predicted)

        for modality in self.precision_weights:
            obs_idx = obs_per_mod.get(modality, 0)
            pred_idx = pred_per_mod.get(modality, 0)
            mod_dim = len(OBSERVATION_MODALITIES_V2[modality])

            if mod_dim <= 1:
                accuracy = 1.0
            else:
                distance = abs(obs_idx - pred_idx) / (mod_dim - 1)
                accuracy = 1.0 - distance

            old = self.precision_weights[modality]
            self.precision_weights[modality] = (
                (1 - self.precision_lr) * old + self.precision_lr * accuracy
            )

    def _apply_precision(self) -> None:
        """Apply per-modality precision scaling to A matrix."""
        A_matrix = self._get_A_matrix()
        if self._base_A is None:
            self._base_A = A_matrix.copy()

        scaled_A = self._base_A.copy()
        row_offset = 0
        for modality, obs_list in OBSERVATION_MODALITIES_V2.items():
            mod_dim = len(obs_list)
            weight = self.precision_weights.get(modality, 1.0)

            uniform = np.ones_like(scaled_A[row_offset:row_offset + mod_dim, :])
            uniform /= mod_dim
            scaled_A[row_offset:row_offset + mod_dim, :] = (
                weight * self._base_A[row_offset:row_offset + mod_dim, :]
                + (1 - weight) * uniform
            )
            row_offset += mod_dim

        col_sums = scaled_A.sum(axis=0, keepdims=True)
        col_sums[col_sums == 0] = 1
        scaled_A = scaled_A / col_sums
        self._set_A_matrix(scaled_A)

    @staticmethod
    def _decompose_observation(flat_idx: int) -> Dict[str, int]:
        """Decompose flat observation index into per-modality indices.

        Layout: context(2) + urgency(3) + confidence(3) + topic(6) = 14
        """
        # For v2, observation is passed as flat index into [0..13]
        # We need to decompose it back to per-modality
        if flat_idx < 2:
            return {"context": flat_idx, "urgency": 0, "confidence": 0, "topic": 0}
        elif flat_idx < 5:
            return {"context": 0, "urgency": flat_idx - 2, "confidence": 0, "topic": 0}
        elif flat_idx < 8:
            return {"context": 0, "urgency": 0, "confidence": flat_idx - 5, "topic": 0}
        else:
            return {"context": 0, "urgency": 0, "confidence": 0, "topic": flat_idx - 8}

    # =========================================================================
    # Learning (Dirichlet)
    # =========================================================================

    def update_A_dirichlet(
        self, observation: int, learning_rate: Optional[float] = None,
    ) -> None:
        """Dirichlet update: pA += η * outer(o, beliefs)."""
        eta = learning_rate if learning_rate is not None else self.learning_rate

        beliefs_array = self._to_beliefs_array()
        A_matrix = self._get_A_matrix()

        num_obs = A_matrix.shape[0]
        obs_idx = min(int(observation), num_obs - 1)
        obs_vector = np.zeros(num_obs)
        obs_vector[obs_idx] = 1.0

        update = eta * np.outer(obs_vector, beliefs_array)
        eps = 1e-10
        A_matrix = np.clip(A_matrix + update, eps, None)
        A_matrix = A_matrix / A_matrix.sum(axis=0, keepdims=True)

        self._set_A_matrix(A_matrix)
        self._history.append({
            "type": "dirichlet_update",
            "observation": observation,
            "learning_rate": eta,
        })

    # =========================================================================
    # Persistence
    # =========================================================================

    def save_learned_A(self, path: Optional[str] = None) -> str:
        """Save learned A matrix."""
        from .persistence import save_A
        from pathlib import Path as P

        target_path = P(path) if path else None
        saved_path = save_A(self, target_path)
        self._history.append({"type": "save_A", "path": str(saved_path)})
        return str(saved_path)

    def load_learned_A(self, path: Optional[str] = None) -> bool:
        """Load learned A matrix."""
        from .persistence import load_A, A_exists, LEARNED_A_PATH
        from pathlib import Path as P

        target_path = P(path) if path else None
        if not A_exists(target_path):
            return False

        loaded_A = load_A(target_path)
        if loaded_A is not None:
            # Validate shape before loading
            expected_shape = (self.num_obs, self.state_dim)
            if hasattr(loaded_A, 'shape'):
                actual = loaded_A.shape if not loaded_A.dtype == object else loaded_A[0].shape
                if actual != expected_shape:
                    # Shape mismatch (v1 matrix loaded into v2 agent)
                    return False

            self.agent.A = loaded_A
            self._history.append({
                "type": "load_A",
                "path": str(target_path or LEARNED_A_PATH),
            })
            return True
        return False

    def reset(self):
        """Reset to initial beliefs."""
        self.beliefs = self._default_D()
        self._history = []

    def get_history(self) -> List[Dict[str, Any]]:
        """Return inference history."""
        return self._history
