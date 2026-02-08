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


# PURPOSE: 48-state Active Inference Agent with Series integration
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
        epsilon: Optional[Dict[str, float]] = None,
    ):
        if not PYMDP_AVAILABLE:
            raise ImportError("pymdp is not installed. Install with: pip install pymdp")

        self.state_dim = NUM_STATES_V2  # 48
        self.num_obs = NUM_OBS_V2       # 14
        self.num_actions = NUM_ACTIONS_V2  # 7
        self.obs_dims = {k: len(v) for k, v in OBSERVATION_MODALITIES_V2.items()}

        # Epsilon Architecture: M = (1-ε) × structure + ε × uniform
        # These are the ONLY free parameters in the generative model.
        # All other values derive from domain structure (Stoic philosophy).
        self.epsilon: Dict[str, float] = {
            "A": 0.25,           # observation noise (/dia+ reviewed)
            "B_observe": 0.10,   # state persistence under observation
            "B_act": 0.15,       # transition noise under action
            "D": 0.15,           # prior uncertainty
        }
        if epsilon:
            self.epsilon.update(epsilon)

        # Prediction tracking for Meta-ε learning
        self._prediction_errors: List[float] = []

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
        self._prev_beliefs: Optional[np.ndarray] = None  # For B learning
        self._history: List[Dict[str, Any]] = []

    # =========================================================================
    # A Matrix: P(observation | hidden_state) — 14 × 48
    # =========================================================================

    def _default_A(self) -> np.ndarray:
        """Generate 48-state observation likelihood matrix.

        Architecture: A(obs|state) = (1 - ε_A) × categorical_mapping + ε_A × uniform

        ε_A = observation noise parameter.
        Higher than ε_B because observations are noisier than transitions.
        /dia+ review: ε_A=0.25 prevents overconfidence in 3-value modalities.

        Categorical mapping (Stoic epistemic structure):
          phantasia → context:    clear→clear, uncertain→ambiguous
          horme    → urgency:    active→high, passive→low
          assent   → confidence: granted→high, withheld→low
          series   → topic:      X→X (identity)

        Rows 0-1:   context (2 values)
        Rows 2-4:   urgency (3 values)
        Rows 5-7:   confidence (3 values)
        Rows 8-13:  topic (6 values)
        """
        EPS_A = self.epsilon["A"]  # observation noise — higher than EPS_B (transitions)

        # Categorical mapping: hidden state factor → observation index
        # Each entry: (target_obs_index_within_modality, modality_size)
        CATEGORICAL = {
            # phantasia → context
            "context": {"clear": 1, "uncertain": 0},        # 2 values
            # horme → urgency
            "urgency": {"active": 2, "passive": 0},         # 3 values: low=0, med=1, high=2
            # assent → confidence
            "confidence": {"granted": 2, "withheld": 0},    # 3 values: low=0, med=1, high=2
        }

        MODALITY_SIZES = {"context": 2, "urgency": 3, "confidence": 3, "topic": 6}

        A = np.zeros((self.num_obs, self.state_dim))

        for s_idx in range(self.state_dim):
            phantasia, assent, horme, series = index_to_state_v2(s_idx)
            row = 0

            # --- Context (rows 0-1): phantasia ---
            n = MODALITY_SIZES["context"]
            target = CATEGORICAL["context"][phantasia]
            for i in range(n):
                A[row + i, s_idx] = (1 - EPS_A) * (1.0 if i == target else 0.0) + EPS_A / n
            row += n

            # --- Urgency (rows 2-4): horme ---
            n = MODALITY_SIZES["urgency"]
            target = CATEGORICAL["urgency"][horme]
            for i in range(n):
                A[row + i, s_idx] = (1 - EPS_A) * (1.0 if i == target else 0.0) + EPS_A / n
            row += n

            # --- Confidence (rows 5-7): assent ---
            n = MODALITY_SIZES["confidence"]
            target = CATEGORICAL["confidence"][assent]
            for i in range(n):
                A[row + i, s_idx] = (1 - EPS_A) * (1.0 if i == target else 0.0) + EPS_A / n
            row += n

            # --- Topic (rows 8-13): series ---
            n = MODALITY_SIZES["topic"]
            series_idx = SERIES_STATES.index(series)
            for i in range(n):
                A[row + i, s_idx] = (1 - EPS_A) * (1.0 if i == series_idx else 0.0) + EPS_A / n

        # Normalize columns (should already sum to 1, but safety)
        col_sums = A.sum(axis=0, keepdims=True)
        col_sums[col_sums == 0] = 1
        A = A / col_sums
        return A

    # =========================================================================
    # B Matrix: P(s' | s, a) — 48 × 48 × 7
    # =========================================================================

    def _default_B(self) -> np.ndarray:
        """Generate 48-state transition matrix for 7 actions.

        Architecture: B(a) = (1 - ε_a) × stoic_necessity + ε_a × uniform

        ε_a (epsilon per action) = method uncertainty parameter.
        Only 2 free parameters instead of ~20 magic numbers.

        Stoic necessity defines deterministic transitions:
          observe → identity (state preservation)
          act_X   → clear phantasia, granted assent, active horme, target series

        References:
          /sop: Perplexity research (2026-02-08)
          C3: "Identity + noise" structure (Da Costa et al. 2020)
          Hegemonikón /noe: σ one-parameter family analysis
        """
        # === ε parameters: the ONLY tunable values ===
        EPS_OBSERVE = self.epsilon["B_observe"]  # state-preserving under observation
        EPS_ACT = self.epsilon["B_act"]            # Stoic necessity under action

        B = np.zeros((self.state_dim, self.state_dim, self.num_actions))
        uniform = 1.0 / self.state_dim  # Uniform noise floor

        for from_idx in range(self.state_dim):
            from_p, from_a, from_h, from_s = index_to_state_v2(from_idx)

            for to_idx in range(self.state_dim):
                to_p, to_a, to_h, to_s = index_to_state_v2(to_idx)

                # --- Action 0: observe ---
                # Stoic necessity: identity (nothing changes when you wait)
                is_identity = (
                    to_p == from_p and to_a == from_a
                    and to_h == from_h and to_s == from_s
                )
                if is_identity:
                    B[to_idx, from_idx, 0] = (1 - EPS_OBSERVE) + EPS_OBSERVE * uniform
                else:
                    B[to_idx, from_idx, 0] = EPS_OBSERVE * uniform

                # --- Actions 1-6: act_O..act_A ---
                for act_idx in range(1, 7):
                    target_series = SERIES_STATES[act_idx - 1]

                    # Stoic necessity: acting implies these transitions
                    #   phantasia → clear (engagement reveals truth)
                    #   assent → granted (acting IS assenting)
                    #   horme → active (acting IS the impulse)
                    #   series → target (acting on X means committing to X)
                    is_stoic_target = (
                        to_p == "clear"
                        and to_a == "granted"
                        and to_h == "active"
                        and to_s == target_series
                    )
                    if is_stoic_target:
                        B[to_idx, from_idx, act_idx] = (
                            (1 - EPS_ACT) + EPS_ACT * uniform
                        )
                    else:
                        B[to_idx, from_idx, act_idx] = EPS_ACT * uniform

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
        """Generate initial state belief.

        Architecture: D(state) = (1 - ε_D) × stoic_prior + ε_D × uniform

        ε_D = prior uncertainty parameter.

        Stoic prior (natural cognitive stance before evidence):
          phantasia: uncertain (epistemic humility — don't assume clarity)
          assent:    withheld (Epochē — suspend judgment until evidence)
          horme:     passive  (wait for warranted action)
          series:    uniform  (no prior preference for any Series)
        """
        EPS_D = self.epsilon["D"]  # prior uncertainty

        # Stoic prior: the natural state before any evidence
        STOIC_PRIOR = {
            "phantasia": "uncertain",  # epistemic humility
            "assent":    "withheld",   # Epochē
            "horme":     "passive",    # wait for evidence
        }

        D = np.zeros(self.state_dim)

        for idx in range(self.state_dim):
            phantasia, assent, horme, series = index_to_state_v2(idx)

            # Stoic necessity: 1.0 if state matches prior, 0.0 otherwise
            stoic = 1.0
            stoic *= 1.0 if phantasia == STOIC_PRIOR["phantasia"] else 0.0
            stoic *= 1.0 if assent == STOIC_PRIOR["assent"] else 0.0
            stoic *= 1.0 if horme == STOIC_PRIOR["horme"] else 0.0
            # Series: always uniform (no prior knowledge)
            stoic *= 1.0 / len(SERIES_STATES)

            # ε decomposition
            uniform = 1.0 / self.state_dim
            D[idx] = (1 - EPS_D) * stoic + EPS_D * uniform

        D = D / D.sum()
        return D

    # =========================================================================
    # Inference Cycle
    # =========================================================================

    # PURPOSE: O1 Noēsis: Update beliefs given observation
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

    # PURPOSE: O2 Boulēsis: Select policy minimizing EFE
    def infer_policies(self) -> Tuple[np.ndarray, np.ndarray]:
        """O2 Boulēsis: Select policy minimizing EFE."""
        q_pi, neg_efe = self.agent.infer_policies()
        self._history.append({
            "type": "infer_policies", "q_pi": q_pi, "neg_efe": neg_efe,
        })
        return q_pi, neg_efe

    # PURPOSE: Sample action from policy distribution
    def sample_action(self) -> int:
        """Sample action from policy distribution."""
        action = self.agent.sample_action()
        if isinstance(action, np.ndarray):
            action = int(action[0])
        self._history.append({"type": "action", "action": action})
        return int(action)

    # PURPOSE: Complete inference-action cycle with 7-action output
    def step(self, observation: int) -> Dict[str, Any]:
        """Complete inference-action cycle with 7-action output.

        Returns dict with action_name in {observe, act_O, ..., act_A}
        and selected_series for act_* actions.
        """
        # Store beliefs BEFORE this step (for B learning)
        self._prev_beliefs = self._to_beliefs_array().copy()

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

    # PURPOSE: Explain the last step decision in natural language
    def explain(self, step_result: Optional[Dict[str, Any]] = None) -> str:
        """Explain the last step decision in natural language.

        Aggregates EFE by first-action, ranks alternatives, and
        produces a human-readable explanation of WHY this action
        was chosen over alternatives.

        Args:
            step_result: Output of step(). If None, uses last history.

        Returns:
            Japanese explanation string.
        """
        if step_result is None:
            # Try to reconstruct from history
            return "（説明不可: step() の結果が提供されていません）"

        q_pi = step_result.get("q_pi")
        neg_efe = step_result.get("neg_efe")
        if q_pi is None or neg_efe is None:
            return "（説明不可: EFE データが不足）"

        action = step_result["action"]
        act_name = step_result["action_name"]
        entropy = step_result["entropy"]
        map_state = step_result.get("map_state_names", {})
        selected_series = step_result.get("selected_series")

        # Aggregate EFE by first-action
        policies = self.agent.policies
        if isinstance(policies, list):
            policies = np.array(policies)
        first_actions = policies[:, 0, 0].astype(int)

        efe_by_action: Dict[str, float] = {}
        prob_by_action: Dict[str, float] = {}
        for act_idx in range(self.num_actions):
            name = action_name_v2(act_idx)
            mask = first_actions == act_idx
            if mask.any():
                efe_by_action[name] = float(neg_efe[mask].max())
                prob_by_action[name] = float(q_pi[mask].sum())

        # Rank by probability
        ranked = sorted(prob_by_action.items(), key=lambda x: -x[1])

        # Build explanation
        lines = []

        # 1. What was chosen and why
        prob_pct = int(prob_by_action.get(act_name, 0) * 100)
        if act_name == "observe":
            lines.append(
                f"選択: observe ({prob_pct}%) — 不確実性が高く行動を保留"
            )
            lines.append(f"  entropy={entropy:.2f} → まだ確信が持てない")
        else:
            lines.append(
                f"選択: {act_name} ({prob_pct}%) — "
                f"Series {selected_series} での行動が最も期待自由エネルギーを下げる"
            )

        # 2. State interpretation
        p = map_state.get("phantasia", "?")
        a = map_state.get("assent", "?")
        h = map_state.get("horme", "?")
        s = map_state.get("series", "?")
        state_desc = {
            ("clear", "granted", "active"): "明瞭な印象、確信あり、行動意欲あり",
            ("clear", "withheld", "passive"): "明瞭だが判断保留、静観中",
            ("uncertain", "withheld", "passive"): "不確実、Epochē 維持",
            ("clear", "granted", "passive"): "確信はあるが衝動なし",
            ("clear", "withheld", "active"): "明瞭で意欲あるが確信不足",
            ("uncertain", "granted", "active"): "不確実だが行動に傾いている",
        }
        desc = state_desc.get(
            (p, a, h),
            f"phantasia={p}, assent={a}, horme={h}"
        )
        lines.append(f"  内部状態: {desc} (Series={s})")

        # 3. Top 3 alternatives
        lines.append("  代替候補:")
        for name, prob in ranked[:3]:
            pct = int(prob * 100)
            marker = " ←" if name == act_name else ""
            lines.append(f"    {name:8s} {pct:3d}%{marker}")

        return "\n".join(lines)

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

    def _get_B_matrix(self) -> np.ndarray:
        """Extract B matrix from pymdp agent."""
        B = self.agent.B
        if isinstance(B, np.ndarray) and B.dtype == object:
            return np.asarray(B[0], dtype=np.float64)
        if isinstance(B, list):
            return np.asarray(B[0], dtype=np.float64)
        return np.asarray(B, dtype=np.float64)

    def _set_B_matrix(self, B_matrix: np.ndarray) -> None:
        """Write B matrix back to pymdp agent."""
        if isinstance(self.agent.B, np.ndarray) and self.agent.B.dtype == object:
            self.agent.B[0] = B_matrix
        elif isinstance(self.agent.B, list):
            self.agent.B[0] = B_matrix
        else:
            self.agent.B = B_matrix

    def _get_predicted_observation(self) -> np.ndarray:
        """E[o] = A @ beliefs."""
        return self._get_A_matrix() @ self._to_beliefs_array()

    # =========================================================================
    # Precision Weighting
    # =========================================================================

    # PURPOSE: Update precision weights based on prediction error per modality
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

    # PURPOSE: Dirichlet update: pA += η * outer(o, beliefs)
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

    # PURPOSE: Dirichlet B update: pB[:,:,a] += η * outer(beliefs_next, beliefs_prev)
    def update_B_dirichlet(
        self, action: int, learning_rate: Optional[float] = None,
    ) -> None:
        """Dirichlet B update: pB[:,:,a] += η * outer(beliefs_next, beliefs_prev).

        Learn state transitions from experience.
        Requires step() to have been called first (stores _prev_beliefs).

        Args:
            action: Integer action index (0=observe, 1-6=act_O..act_A)
            learning_rate: Optional override (default: self.learning_rate * 0.1)

        References:
            Da Costa et al. 2020, Eq. 2.18: Action-conditional B learning
            /sop Perplexity research: Dirichlet B学習理論式
        """
        if self._prev_beliefs is None:
            return  # No previous step to learn from

        # B learning uses lower rate than A (transitions are slower to learn)
        eta = learning_rate if learning_rate is not None else self.learning_rate * 0.1

        beliefs_next = self._to_beliefs_array()
        beliefs_prev = self._prev_beliefs
        B_matrix = self._get_B_matrix()

        action_idx = min(int(action), self.num_actions - 1)

        # Sufficient statistic: outer product of posterior beliefs
        # This is the empirical transition count for Dirichlet update
        update = eta * np.outer(beliefs_next, beliefs_prev)
        eps = 1e-10
        B_matrix[:, :, action_idx] = np.clip(
            B_matrix[:, :, action_idx] + update, eps, None
        )

        # Normalize columns per action (each column = transition dist from a state)
        col_sums = B_matrix[:, :, action_idx].sum(axis=0, keepdims=True)
        col_sums[col_sums == 0] = 1
        B_matrix[:, :, action_idx] = B_matrix[:, :, action_idx] / col_sums

        self._set_B_matrix(B_matrix)
        self._history.append({
            "type": "dirichlet_B_update",
            "action": action_idx,
            "learning_rate": eta,
        })

    # =========================================================================
    # Meta-ε Learning
    # =========================================================================
    #
    # FEP precision weighting applied to the ε parameters themselves.
    # "How much should I trust my domain structure vs empirical data?"
    #
    # ε ∈ [0.01, 0.50]:
    #   ε → 0.01: almost fully trust domain structure (rigid)
    #   ε → 0.50: half structure, half data (maximally uncertain)
    #
    # update_epsilon() adjusts ε based on prediction accuracy:
    #   accurate predictions → lower ε (trust structure more)
    #   inaccurate predictions → raise ε (trust data more)
    #

    # PURPOSE: Track prediction error for Meta-ε
    def track_prediction(self, observation: int, predicted: int) -> float:
        """Track prediction accuracy for Meta-ε learning.

        Call this after each step to record whether the Agent's
        predicted observation matched the actual observation.

        Returns:
            error: 0.0 (correct) or 1.0 (incorrect)
        """
        error = 0.0 if observation == predicted else 1.0
        self._prediction_errors.append(error)
        return error

    # PURPOSE: Meta-ε update — adjust ε based on prediction accuracy
    def update_epsilon(
        self,
        window: int = 20,
        adaptation_rate: float = 0.05,
        eps_min: float = 0.01,
        eps_max: float = 0.50,
    ) -> Dict[str, float]:
        """Update ε values based on accumulated prediction errors.

        Law: ε_new = ε_old + adaptation_rate × (error_rate - ε_old)
        This is an exponential moving average toward the error rate.

        Intuition:
        - If error_rate ≈ 0 (predictions correct): ε decreases → trust structure
        - If error_rate ≈ 0.5 (random): ε increases → trust data
        - ε converges toward the "true" noise level of the environment

        Args:
            window: Number of recent predictions to consider
            adaptation_rate: Speed of ε adaptation (EMA coefficient)
            eps_min: Floor for ε (never fully trust structure)
            eps_max: Ceiling for ε (never fully abandon structure)

        Returns:
            Dict of updated ε values with deltas
        """
        if len(self._prediction_errors) < 5:
            return {k: 0.0 for k in self.epsilon}  # Not enough data

        recent = self._prediction_errors[-window:]
        error_rate = sum(recent) / len(recent)

        deltas: Dict[str, float] = {}
        for key in self.epsilon:
            old_val = self.epsilon[key]
            # EMA toward error_rate: ε approaches the "true" noise level
            new_val = old_val + adaptation_rate * (error_rate - old_val)
            new_val = max(eps_min, min(eps_max, new_val))
            deltas[key] = new_val - old_val
            self.epsilon[key] = new_val

        self._history.append({
            "type": "meta_epsilon_update",
            "error_rate": error_rate,
            "window": len(recent),
            "epsilon": dict(self.epsilon),
            "deltas": deltas,
        })

        return deltas

    # PURPOSE: Get Meta-ε diagnostic summary
    def epsilon_summary(self) -> Dict[str, Any]:
        """Return diagnostic summary of ε state."""
        error_rate = None
        if self._prediction_errors:
            recent = self._prediction_errors[-20:]
            error_rate = sum(recent) / len(recent)
        return {
            "epsilon": dict(self.epsilon),
            "prediction_count": len(self._prediction_errors),
            "error_rate": error_rate,
            "total_errors": sum(self._prediction_errors) if self._prediction_errors else 0,
        }

    # =========================================================================
    # Persistence
    # =========================================================================

    # PURPOSE: Save learned A matrix
    def save_learned_A(self, path: Optional[str] = None) -> str:
        """Save learned A matrix."""
        from .persistence import save_A
        from pathlib import Path as P

        target_path = P(path) if path else None
        saved_path = save_A(self, target_path)
        self._history.append({"type": "save_A", "path": str(saved_path)})
        return str(saved_path)

    # PURPOSE: Load learned A matrix
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

    # PURPOSE: Save learned B matrix
    def save_learned_B(self, path: Optional[str] = None) -> str:
        """Save learned B matrix."""
        from .persistence import LEARNED_A_PATH
        from pathlib import Path as P

        default_path = LEARNED_A_PATH.parent / "learned_B.npy"
        target_path = P(path) if path else default_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        np.save(str(target_path), self.agent.B)
        self._history.append({"type": "save_B", "path": str(target_path)})
        return str(target_path)

    # PURPOSE: Load learned B matrix
    def load_learned_B(self, path: Optional[str] = None) -> bool:
        """Load learned B matrix."""
        from .persistence import LEARNED_A_PATH
        from pathlib import Path as P

        default_path = LEARNED_A_PATH.parent / "learned_B.npy"
        target_path = P(path) if path else default_path

        if not target_path.exists():
            return False

        loaded_B = np.load(str(target_path), allow_pickle=True)
        if loaded_B is not None:
            # Validate shape
            expected_shape = (self.state_dim, self.state_dim, self.num_actions)
            if hasattr(loaded_B, 'shape'):
                actual = (
                    loaded_B.shape if loaded_B.dtype != object
                    else loaded_B[0].shape
                )
                if actual != expected_shape:
                    return False

            self.agent.B = loaded_B
            self._history.append({
                "type": "load_B",
                "path": str(target_path),
            })
            return True
        return False

    # PURPOSE: Reset to initial beliefs
    def reset(self):
        """Reset to initial beliefs."""
        self.beliefs = self._default_D()
        self._history = []

    # PURPOSE: Return inference history
    def get_history(self) -> List[Dict[str, Any]]:
        """Return inference history."""
        return self._history
