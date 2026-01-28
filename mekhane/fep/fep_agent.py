"""
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
    ):
        """Initialize the FEP agent.
        
        Args:
            A: Observation likelihood matrix P(o|s). Shape: (num_obs, num_states)
            B: State transition matrix P(s'|s,a). Shape: (num_states, num_states, num_actions)
            C: Preference vector over observations. Shape: (num_obs,)
            D: Initial state belief (prior). Shape: (num_states,)
            use_defaults: If True and matrices not provided, use default Hegemonikón matrices
            
        Raises:
            ImportError: If pymdp is not available
        """
        if not PYMDP_AVAILABLE:
            raise ImportError(
                "pymdp is not installed. Install with: pip install pymdp"
            )
        
        self.state_dim = get_state_dim()
        self.obs_dims = {k: len(v) for k, v in OBSERVATION_MODALITIES.items()}
        
        # Use provided matrices or generate defaults
        if use_defaults:
            A = A if A is not None else self._default_A()
            B = B if B is not None else self._default_B()
            C = C if C is not None else self._default_C()
            D = D if D is not None else self._default_D()
        
        # Initialize pymdp Agent
        self.agent = Agent(A=A, B=B, C=C, D=D)
        self.beliefs = D.copy() if D is not None else np.ones(self.state_dim) / self.state_dim
        
        # Track history for analysis
        self._history: List[Dict[str, Any]] = []
    
    def _default_A(self) -> np.ndarray:
        """Generate default observation likelihood matrix.
        
        Simple mapping: clear phantasia -> clear context observation
        """
        num_obs = sum(self.obs_dims.values())
        A = np.zeros((num_obs, self.state_dim))
        
        # Simplified: identity-like mapping for demonstration
        for i in range(self.state_dim):
            # Distribute probability across observation space
            obs_idx = i % num_obs
            A[obs_idx, i] = 0.8
            A[(obs_idx + 1) % num_obs, i] = 0.2
        
        # Normalize columns
        A = A / A.sum(axis=0, keepdims=True)
        return A
    
    def _default_B(self) -> np.ndarray:
        """Generate default state transition matrix.
        
        Actions: 0=observe, 1=act
        """
        num_actions = 2
        B = np.zeros((self.state_dim, self.state_dim, num_actions))
        
        for a in range(num_actions):
            # Default: slight tendency to stay in same state
            B[:, :, a] = np.eye(self.state_dim) * 0.7
            # Add some transition probability
            B[:, :, a] += 0.3 / self.state_dim
            # Normalize columns
            B[:, :, a] = B[:, :, a] / B[:, :, a].sum(axis=0, keepdims=True)
        
        return B
    
    def _default_C(self) -> np.ndarray:
        """Generate default preference vector.
        
        Prefers clear context, high confidence.
        """
        num_obs = sum(self.obs_dims.values())
        C = np.zeros(num_obs)
        
        # Simple preference: prefer higher observation indices
        for i in range(num_obs):
            C[i] = i * 0.5
        
        return C
    
    def _default_D(self) -> np.ndarray:
        """Generate default initial state belief.
        
        Uniform prior (maximum entropy).
        """
        return np.ones(self.state_dim) / self.state_dim
    
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
        obs_tuple = (observation,) if isinstance(observation, int) else tuple(observation)
        
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
        
        self._history.append({
            "type": "infer_policies",
            "q_pi": q_pi,
            "neg_efe": neg_efe,
        })
        
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
        action_name = action_names[action] if action < len(action_names) else f"action_{action}"
        
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
