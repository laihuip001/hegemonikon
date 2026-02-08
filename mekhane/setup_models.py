# PROOF: [L2/インフラ] <- mekhane/ A0→品質管理が必要→setup_models が担う

import os
from pathlib import Path
import shutil
from huggingface_hub import hf_hub_download

# Configuration
MODEL_ID = "Xenova/bge-small-en-v1.5"
DEST_DIR = Path(__file__).parent / "anamnesis" / "models" / "bge-small"


# PURPOSE: 関数: setup_models
def setup_models():
    print(f"Setting up models in {DEST_DIR}...")
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    files_to_download = [
        ("onnx/model.onnx", "model.onnx"),
        ("tokenizer.json", "tokenizer.json"),
        ("config.json", "config.json"),
        ("special_tokens_map.json", "special_tokens_map.json"),
        ("vocab.txt", "vocab.txt"),
    ]

    for remote_path, local_name in files_to_download:
        print(f"Downloading {remote_path} as {local_name}...")
        try:
            downloaded = hf_hub_download(
                repo_id=MODEL_ID,
                filename=remote_path,
                local_dir=DEST_DIR,
                local_dir_use_symlinks=False,
            )

            # If the file was downloaded to a subdirectory (e.g. onnx/), move it
            downloaded_path = Path(downloaded)
            target_path = DEST_DIR / local_name

            if downloaded_path != target_path:
                shutil.move(downloaded_path, target_path)
                print(f"Moved to {target_path}")

            # Cleanup subdirectories if empty
            if remote_path.startswith("onnx/"):
                onnx_dir = DEST_DIR / "onnx"
                if onnx_dir.exists() and not any(onnx_dir.iterdir()):
                    onnx_dir.rmdir()

        except Exception as e:
            print(f"Failed to download {remote_path}: {e}")

    print("Model setup complete.")


if __name__ == "__main__":
    setup_models()
