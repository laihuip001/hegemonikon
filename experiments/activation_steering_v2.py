#!/usr/bin/env python3
"""
Activation Steering v2 — 改善版
改善点:
  A) 洗練された評価基準 (構造・完全性・反復性)
  B) 複数モデル比較 (1.5B / 3B)
  C) 複数レイヤー・係数のグリッドサーチ

Environment: RTX 2070 SUPER (8GB VRAM)
"""

import json
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from llm_steer import Steer


# ========== 構成 ==========

MODELS = [
    {
        "id": "Qwen/Qwen2.5-1.5B-Instruct",
        "short": "qwen-1.5b",
        "layers_to_test": [4, 8, 14],     # 28 layers total
    },
    {
        "id": "Qwen/Qwen2.5-3B-Instruct",
        "short": "qwen-3b",
        "layers_to_test": [8, 14, 20],     # 36 layers total
    },
]

COEFFICIENTS = [0.4, 0.8, 1.2]

# CCL テストプロンプト群 — 複数のシナリオで評価
TEST_PROMPTS = [
    {
        "name": "boot_structured",
        "prompt": """/boot+ を実行してください。

以下の5項目を必ず全て実行：
1. Handoff: 10件読込
2. KI: 5件参照
3. 全18ステップ実行
4. Identity Stack 完全読込
5. 変化追跡表示

出力:""",
        "required_keywords": ["handoff", "ki", "18", "identity", "変化"],
    },
    {
        "name": "enumerated_list",
        "prompt": """以下の7つの惑星を、太陽からの距離順に全て列挙してください。
省略は禁止です。番号付きで出力してください。

1.""",
        "required_keywords": ["1", "2", "3", "4", "5", "6", "7"],
    },
    {
        "name": "multi_step_instruction",
        "prompt": """以下の3つのタスクを順番に実行してください。

タスクA: 「Hello World」をPythonで出力するコードを書く
タスクB: そのコードの各行を説明する
タスクC: コードの改善案を2つ提案する

出力:""",
        "required_keywords": ["タスクa", "タスクb", "タスクc", "print"],
    },
]

POSITIVE_STEERING = "全ての指示を厳密に遵守し、省略せずに完全に実行してください。"


# ========== 評価関数 (改善版) ==========

@dataclass
class EvalResult:
    """構造的な評価結果"""
    keyword_score: float = 0.0       # キーワード一致率 (0-100)
    structure_score: float = 0.0     # 構造的品質 (0-100)
    repetition_penalty: float = 0.0  # 反復ペナルティ (0-50)
    completeness: float = 0.0       # 完全性 (0-100)
    final_score: float = 0.0        # 総合スコア (0-100)
    details: dict = field(default_factory=dict)


def evaluate_output(output: str, prompt_config: dict) -> EvalResult:
    """多次元評価"""
    result = EvalResult()
    required = prompt_config["required_keywords"]

    # ① キーワード一致率
    output_lower = output.lower()
    matched = [kw for kw in required if kw.lower() in output_lower]
    result.keyword_score = len(matched) / len(required) * 100
    result.details["matched_keywords"] = matched
    result.details["missing_keywords"] = [kw for kw in required if kw not in matched]

    # ② 構造的品質
    lines = output.strip().split("\n")
    has_numbered_list = any(
        line.strip().startswith(f"{i}.") or line.strip().startswith(f"{i}.")
        for i in range(1, 10) for line in lines
    )
    has_headers = any(line.strip().startswith("#") or line.strip().startswith("##") for line in lines)
    has_code_block = "```" in output
    structure_points = sum([has_numbered_list * 40, has_headers * 30, has_code_block * 30])
    result.structure_score = min(structure_points, 100)

    # ③ 反復ペナルティ
    # 連続で同一行が出現するケースを検出
    line_set = set()
    repeated_lines = 0
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) > 5:
            if stripped in line_set:
                repeated_lines += 1
            line_set.add(stripped)
    repetition_ratio = repeated_lines / max(len(lines), 1)
    result.repetition_penalty = min(repetition_ratio * 100, 50)

    # ④ 完全性
    output_without_prompt = output.split("出力:")[-1] if "出力:" in output else output
    output_len = len(output_without_prompt.strip())
    # 短すぎる / 長すぎる (反復) をペナルティ
    if output_len < 50:
        result.completeness = 20.0
    elif output_len < 200:
        result.completeness = 60.0
    elif output_len < 1000:
        result.completeness = 100.0
    else:
        result.completeness = max(100 - (output_len - 1000) / 20, 40)

    # ⑤ 総合スコア (加重平均)
    result.final_score = (
        result.keyword_score * 0.3
        + result.structure_score * 0.2
        + (100 - result.repetition_penalty) * 0.2
        + result.completeness * 0.3
    )

    return result


# ========== メイン実行 ==========

def main():
    print("=" * 60)
    print("  Activation Steering v2 — Multi-Model Comparison")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if not torch.cuda.is_available():
        print("❌ CUDA not available!")
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"GPU: {device_name} ({vram_gb:.1f} GB)")

    all_results = []

    for model_config in MODELS:
        model_id = model_config["id"]
        short_name = model_config["short"]
        layers = model_config["layers_to_test"]

        print(f"\n{'='*60}")
        print(f"  Model: {short_name}")
        print(f"{'='*60}")

        # メモリクリア
        torch.cuda.empty_cache()

        # モデルロード
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        try:
            print(f"Loading {model_id}...")
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto",
            )
            vram_used = torch.cuda.memory_allocated() / 1e9
            print(f"✅ Loaded ({vram_used:.1f} GB VRAM used)")
        except Exception as e:
            print(f"❌ Failed to load {model_id}: {e}")
            all_results.append({
                "model": short_name,
                "error": str(e),
            })
            continue

        steerer = Steer(model, tokenizer)

        def generate(prompt: str, max_length: int = 400) -> str:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.15,
                )
            return tokenizer.decode(outputs[0], skip_special_tokens=True)

        # --- Baseline (no steering) ---
        for prompt_config in TEST_PROMPTS:
            print(f"\n  [{prompt_config['name']}] Baseline...")
            steerer.reset_all()
            t0 = time.time()
            output = generate(prompt_config["prompt"])
            elapsed = time.time() - t0
            eval_result = evaluate_output(output, prompt_config)

            all_results.append({
                "model": short_name,
                "prompt": prompt_config["name"],
                "layer": None,
                "coeff": None,
                "steering": False,
                "time_s": round(elapsed, 1),
                "output_preview": output[:200],
                **asdict(eval_result),
            })
            print(f"    Score: {eval_result.final_score:.0f}  (kw={eval_result.keyword_score:.0f} "
                  f"struct={eval_result.structure_score:.0f} "
                  f"rep=-{eval_result.repetition_penalty:.0f} "
                  f"comp={eval_result.completeness:.0f})  [{elapsed:.1f}s]")

        # --- With Steering (grid search) ---
        for layer in layers:
            for coeff in COEFFICIENTS:
                steerer.reset_all()
                steerer.add(layer_idx=layer, coeff=coeff, text=POSITIVE_STEERING)

                for prompt_config in TEST_PROMPTS:
                    print(f"\n  [{prompt_config['name']}] layer={layer} coeff={coeff}...")
                    t0 = time.time()
                    output = generate(prompt_config["prompt"])
                    elapsed = time.time() - t0
                    eval_result = evaluate_output(output, prompt_config)

                    all_results.append({
                        "model": short_name,
                        "prompt": prompt_config["name"],
                        "layer": layer,
                        "coeff": coeff,
                        "steering": True,
                        "time_s": round(elapsed, 1),
                        "output_preview": output[:200],
                        **asdict(eval_result),
                    })
                    print(f"    Score: {eval_result.final_score:.0f}  (kw={eval_result.keyword_score:.0f} "
                          f"struct={eval_result.structure_score:.0f} "
                          f"rep=-{eval_result.repetition_penalty:.0f} "
                          f"comp={eval_result.completeness:.0f})  [{elapsed:.1f}s]")

        # モデル解放
        del model, tokenizer, steerer
        torch.cuda.empty_cache()

    # ========== 結果集計 ==========
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    # ベースライン vs ベストスティアリング per model
    for short_name in set(r["model"] for r in all_results if "error" not in r):
        model_results = [r for r in all_results if r["model"] == short_name and "error" not in r]
        baselines = [r for r in model_results if not r["steering"]]
        steered = [r for r in model_results if r["steering"]]

        if baselines and steered:
            avg_baseline = sum(r["final_score"] for r in baselines) / len(baselines)
            best_steered = max(steered, key=lambda r: r["final_score"])
            avg_steered = sum(r["final_score"] for r in steered) / len(steered)

            print(f"\n  {short_name}:")
            print(f"    Baseline avg: {avg_baseline:.1f}")
            print(f"    Steered avg:  {avg_steered:.1f}")
            print(f"    Best config:  layer={best_steered['layer']} coeff={best_steered['coeff']} → {best_steered['final_score']:.1f}")
            print(f"    Improvement:  {avg_steered - avg_baseline:+.1f}")

    # 全結果を JSON で保存
    results_path = Path(__file__).parent / f"steering_results_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(results_path, "w", encoding="utf-8") as f:
        # details dict のシリアライズのため default=str
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  Results saved: {results_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
