# Activation Steering PoC (Overview)

## 1. Objective

The goal of this PoC is to evaluate the effectiveness of **Activation Steering** as a mechanism for enforcing **Cognitive Algebra (CCL)** compliance in local LLMs. By modifying the internal activations of the model during inference, we aim to steer its behavior toward predefined "Beautiful" (Arche-aligned) outputs without the overhead of fine-tuning or complex RDP-heavy prompting.

## 2. Motivation

- **CCL Compliance**: Traditional prompting often fails to maintain strict CCL structure in long-context or high-complexity tasks.
- **Local Control**: Leveraging local GPU (RTX 2070 SUPER) allows for experiment-heavy iteration with vector extraction and steering.
- **Latency**: Steering vectors provide a lower-latency path to behavioral alignment compared to multi-agent reconciliation.

## 3. Scope

- **Target Model**: Mistral 7B Instruct v0.3 (4-bit quantized).
- **Tooling**: `vLLM`, `llm-steer`, `transformers`.
- **Environment**: Local Debian host with RTX 2070 SUPER (8GB VRAM).

## 4. Key Metrics

- **Compliance Rate**: Percentage of outputs passing `sel_validator`.
- **Information Density**: Maintaining high deductive resolution while being steered.
- **Compute Overhead**: Measuring the VRAM and latency impact of steering.
