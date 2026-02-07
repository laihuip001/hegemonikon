#!/usr/bin/env python3
"""
Activation Steering MVP — ローカル GPU 実行版
Target: CCL 遵守率向上のための Steering Vector 実験
Environment: RTX 2070 SUPER (8GB VRAM)
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from llm_steer import Steer

# ===== 1. GPU 確認 =====
print("=" * 50)
print("1. Environment Check")
print("=" * 50)
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# ===== 2. モデルロード (Qwen 2.5 1.5B - 軽量で確実に動作) =====
print("\n" + "=" * 50)
print("2. Loading Model (Qwen 2.5 1.5B)")
print("=" * 50)

# 7B は GUI 環境下で VRAM 不足のため、軽量モデルを使用
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

# BitsAndBytesConfig for 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

print(f"Loading {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
)
print("✅ Model loaded")

# ===== 3. Steering Vector 抽出 =====
print("\n" + "=" * 50)
print("3. Steering Vector Setup")
print("=" * 50)

steerer = Steer(model, tokenizer)

# Contrastive prompts for CCL compliance
POSITIVE = "全ての指示を厳密に遵守し、省略せずに完全に実行してください。"
NEGATIVE = "適当に要約して、不要な部分は省略してください。"

# Middle layer (adjust for smaller model - Qwen 1.5B has ~28 layers)
LAYER = 8
COEFF = 0.8

print(f"Positive prompt: {POSITIVE}")
print(f"Layer: {LAYER}, Coefficient: {COEFF}")

# ===== 4. 比較テスト =====
def generate(prompt: str, max_length: int = 512) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs, 
        max_length=max_length, 
        do_sample=True, 
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

CCL_PROMPT = """/boot+ を実行してください。

以下の5項目を必ず全て実行：
1. Handoff: 10件読込
2. KI: 5件参照
3. 全18ステップ実行
4. Identity Stack 完全読込
5. 変化追跡表示

出力:"""

print("\n" + "=" * 50)
print("4. WITHOUT Steering (Baseline)")
print("=" * 50)
steerer.reset_all()
result_without = generate(CCL_PROMPT)
print(result_without)

print("\n" + "=" * 50)
print("5. WITH Steering")
print("=" * 50)
steerer.add(layer_idx=LAYER, coeff=COEFF, text=POSITIVE)
result_with = generate(CCL_PROMPT)
print(result_with)

# ===== 5. 評価 =====
REQUIREMENTS = [
    "handoff",
    "ki",
    "18",      # 全18ステップ
    "identity",
    "変化",    # 変化追跡
]

def check_compliance(output: str, reqs: list) -> float:
    output_lower = output.lower()
    met = [r for r in reqs if r.lower() in output_lower]
    return len(met) / len(reqs) * 100

score_without = check_compliance(result_without, REQUIREMENTS)
score_with = check_compliance(result_with, REQUIREMENTS)

print("\n" + "=" * 50)
print("6. Evaluation Results")
print("=" * 50)
print(f"WITHOUT Steering: {score_without:.0f}%")
print(f"WITH Steering:    {score_with:.0f}%")
print(f"改善: +{score_with - score_without:.0f}%")
print("=" * 50)
