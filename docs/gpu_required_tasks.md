# 🖥️ GPU 必須タスク (自宅 PC 移行後)

> **保存日**: 2026-02-01
> **環境**: Windows PC + GPU

---

## 1. Activation Steering PoC

| 項目 | 詳細 |
|:-----|:-----|
| **目的** | CCL 遵守率向上 (Steering Vector) |
| **工数** | 8h |
| **GPU** | T4 以上 (8GB VRAM) |
| **成果物** | `experiments/activation_steering_mvp.ipynb` |

### 実行手順

```bash
# vLLM + llm_steer
pip install vllm llm-steer transformers accelerate bitsandbytes

# Mistral 7B 4bit
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('mistralai/Mistral-7B-Instruct-v0.3', load_in_4bit=True)"
```

### フェーズ

- [ ] Phase A: 環境構築
- [ ] Phase B: Vector 抽出 (Contrastive prompt)
- [ ] Phase C: Steering 適用
- [ ] Phase D: 評価 (sel_validator)

---

## 2. OpenManus 実験

| 項目 | 詳細 |
|:-----|:-----|
| **目的** | OSS エージェント動作確認 |
| **工数** | 2h |
| **GPU** | 不要 (CPU 可) |
| **成果物** | `experiments/openmanus_mvp.ipynb` |

### 実行手順

```bash
git clone https://github.com/mannaandpoem/OpenManus.git
cd OpenManus
pip install -r requirements.txt
# config/config.toml に API キー設定
```

---

## 3. ローカル LLM 実験 (将来)

| 項目 | 詳細 |
|:-----|:-----|
| **目的** | API 依存からの脱却 |
| **GPU** | 16GB+ VRAM 推奨 |
| **候補モデル** | LLaMA 3 8B, Qwen 2.5 7B |

---

## 関連ファイル

- `activation_steering_research.md` — 調査レポート
- `activation_steering_poc_plan.md` — 詳細計画
- `activation_steering_mvp.ipynb` — Colab notebook
- `openmanus_mvp.ipynb` — OpenManus notebook

---

*Created: 2026-02-01*
