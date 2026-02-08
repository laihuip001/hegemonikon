#!/usr/bin/env python3
# PROOF: [L3/実験] <- scripts/
# PURPOSE: Activation Steering PoC — LLM行動制御の実験
"""Activation Steering PoC v2 — Final LayerNorm Injection.

Key Finding: Decoder layer forward hooks DON'T propagate through
transformers' residual stream. But model.model.norm (final LayerNorm)
hooks DO affect logits.

Strategy:
1. Extract contrastive hidden states from model.model.norm output
2. Compute steering vector = pos - neg
3. Inject at model.model.norm during generation
4. Works with both FP16 and 4-bit quantized models

Usage:
    python scripts/steering_poc.py [--model-size 0.5|3]
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# Contrastive Pairs
STEERING_PAIRS = [
    {
        "name": "epistemic_humility",
        "positive": "I should express uncertainty honestly: 'I'm not fully sure, but...' 'This might be wrong...' 'One possible interpretation...'",
        "negative": "I am absolutely certain. There is no doubt. This is definitively the answer.",
    },
    {
        "name": "systematic_thinking",
        "positive": "Let me think step by step. First, I need to consider... Second, I should check... Third, let me verify...",
        "negative": "The answer is obvious. No need to think deeply. Just say it.",
    },
    {
        "name": "proactive_risk",
        "positive": "I notice a potential risk here that wasn't asked about. The main concern is... Additionally, we should consider...",
        "negative": "Everything looks fine. There are no issues to worry about.",
    },
]


def extract_norm_steering(model, tokenizer, positive: str, negative: str):
    """Extract steering vector from final LayerNorm output."""
    import torch

    def get_norm_hidden(text: str):
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        captured = {}

        def hook(module, input, output):
            captured["hidden"] = output[0, -1, :].detach().clone()

        handle = model.model.norm.register_forward_hook(hook)
        with torch.no_grad():
            model(**inputs)
        handle.remove()
        return captured["hidden"]

    pos_h = get_norm_hidden(positive)
    neg_h = get_norm_hidden(negative)
    steering = pos_h - neg_h
    return steering / steering.norm()


def generate_text(model, tokenizer, prompt, max_new_tokens=120):
    """Generate text with current hooks."""
    import torch
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def main():
    import argparse
    import torch

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-size", choices=["0.5", "3"], default="0.5",
                        help="Model size: 0.5 (FP16, fast) or 3 (4bit)")
    args = parser.parse_args()

    print("=" * 60)
    print("🧭 Activation Steering PoC v2 — LayerNorm Injection")
    print("=" * 60)

    if args.model_size == "3":
        from transformers import BitsAndBytesConfig
        model_id = "Qwen/Qwen2.5-3B-Instruct"
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        load_kwargs = {"quantization_config": bnb_config, "device_map": "auto"}
    else:
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        load_kwargs = {"dtype": torch.float16, "device_map": "auto"}

    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n[1/4] Loading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)

    vram = torch.cuda.memory_allocated() / 1e6
    print(f"  {vram:.0f}MB VRAM")

    # === Extract steering vectors ===
    print("\n[2/4] Extracting steering vectors (from final LayerNorm)...")
    vectors = {}
    for pair in STEERING_PAIRS:
        sv = extract_norm_steering(model, tokenizer, pair["positive"], pair["negative"])
        vectors[pair["name"]] = sv
        print(f"  ✓ {pair['name']}")

    # === Test prompts ===
    prompts = {
        "code_review": (
            "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
            "<|im_start|>user\nWhat is the biggest risk of using AI for code review?<|im_end|>\n"
            "<|im_start|>assistant\n"
        ),
        "decision": (
            "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
            "<|im_start|>user\nShould I migrate from PostgreSQL to MongoDB?<|im_end|>\n"
            "<|im_start|>assistant\n"
        ),
    }

    uncertainty_words = [
        "may", "might", "possibly", "uncertain", "however", "but",
        "risk", "caution", "not always", "can be", "potential",
        "it depends", "important to note", "limitations", "consider",
        "trade-off", "drawback", "careful", "not necessarily",
    ]

    # === Baseline ===
    print("\n[3/4] Baseline generation...")
    baselines = {}
    for name, prompt in prompts.items():
        t0 = time.time()
        text = generate_text(model, tokenizer, prompt)
        baselines[name] = text
        u = sum(1 for w in uncertainty_words if w.lower() in text.lower())
        print(f"  [{name}] u={u} | {time.time()-t0:.1f}s")
        print(f"    {text[:150]}")

    # === Steered (α sweep at LayerNorm) ===
    print("\n[4/4] Steering sweep...")
    alphas = [1.0, 3.0, 5.0, 8.0, 12.0]

    for trait_name, sv in vectors.items():
        print(f"\n  --- {trait_name} ---")
        for prompt_name, prompt in prompts.items():
            base_text = baselines[prompt_name]
            base_u = sum(1 for w in uncertainty_words if w.lower() in base_text.lower())
            print(f"  [{prompt_name}] base u={base_u}")

            for alpha in alphas:
                _alpha = alpha  # Capture for closure

                def steer_hook(module, input, output, _a=_alpha, _sv=sv):
                    return output + _a * _sv.to(output.device)

                handle = model.model.norm.register_forward_hook(steer_hook)
                text = generate_text(model, tokenizer, prompt)
                handle.remove()

                u = sum(1 for w in uncertainty_words if w.lower() in text.lower())
                diff = "≠" if text[:80] != base_text[:80] else "≡"
                print(f"    α={alpha:5.1f} | u={u} {diff} | {text[:100]}")

            print()

    vram = torch.cuda.memory_allocated() / 1e6
    print(f"\n💾 Final VRAM: {vram:.0f}MB")
    print("✅ PoC v2 complete")


if __name__ == "__main__":
    main()
