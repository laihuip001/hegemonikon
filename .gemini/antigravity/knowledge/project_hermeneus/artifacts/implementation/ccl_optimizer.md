# Implementation: CCL Optimizer (DSPy Integration)

As of v0.8.0, Hermēneus incorporates an automatic prompt optimization layer using **DSPy (Declarative Self-improving Language Programs)**. This moves the system from static prompt engineering to dynamic, performance-driven optimization.

## 1. Core Architecture

The optimizer resides in `hermeneus/src/optimizer.py` and provides the `CCLOptimizer` class.

### 1.1 DSPy Teleprompter Logic

Hermēneus utilizes the **`BootstrapFewShot`** teleprompter to:

1. **Generate Demos**: Automatically run the CCL workflow on a subset of examples.
2. **Verify Outputs**: Use a specified `metric` (defaults to semantic overlap/accuracy) to filter successful runs.
3. **Synthesize Prompts**: Bootstrap successful runs as few-shot examples into the final prompt sent to the LLM.

### 1.2 The CCL Module

Optimized tasks are wrapped in a `CCLModule`, which defines a DSPy `Signature`:

- **Input**: `ccl` (the expression), `context` (background data).
- **Process**: `ChainOfThought` (reasoning step before output).
- **Output**: `output` (the refined execution result).

## 2. Optimization Config

```python
@dataclass
class OptimizationConfig:
    optimizer_type: OptimizerType = OptimizerType.BOOTSTRAP_FEWSHOT
    max_bootstrapped_demos: int = 4
    max_labeled_demos: int = 4
    num_trials: int = 10
    metric_threshold: float = 0.8
    model: str = "openai/gpt-4o-mini"
```

## 3. Usage Pattern

Users can optimize a specific CCL workflow by providing a set of `CCLExample` objects.

```python
from hermeneus.src.optimizer import CCLExample, optimize_ccl

examples = [
    CCLExample(ccl="/noe+", context="...", expected_output="...")
]

# Triggers DSPy compilation
result = optimize_ccl("/noe+", examples)
print(f"Optimized Accuracy: {result.accuracy}")
```

## 4. Grounded Impact

By utilizing the optimizer, Hermēneus solves the "Surface Analysis" problem by:

- **Example-Driven Grounding**: Providing real-world successful executions as context.
- **Metric-Based Refinement**: Automatically discarding prompts or demontrations that lead to "Airp" (shallow) or incorrect outputs.

## 5. Empirical Validation

As of 2026-02-01, the `CCLOptimizer` layer was verified with a comprehensive test suite (`test_optimizer.py`):

- **100% Success Rate**: 8/8 tests passed (Default Config, Custom Config, Mock Optimizer, DSPy Availability, Result Formatting).
- **Integration Readiness**: The system is ready to bootstrap few-shot examples for automated skill generation.

---
*Reference: hermeneus/src/optimizer.py (v0.8.0)*
