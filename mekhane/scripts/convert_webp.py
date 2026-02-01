# PROOF: [L3/ユーティリティ] O4→運用スクリプトが必要→convert_webp が担う
from PIL import Image
import sys
import os

if len(sys.argv) < 3:
    print("Usage: python convert_webp.py <input_path> <output_path>")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

try:
    img = Image.open(input_path)
    print(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")

    is_animated = getattr(img, "is_animated", False)
    print(f"Is Animated: {is_animated}")

    if is_animated:
        n_frames = img.n_frames
        print(f"Total Frames: {n_frames}")

        # 抽出するフレームのインデックス
        target_frames = [0, 10, n_frames // 2, n_frames - 1]
        target_frames = sorted(list(set([f for f in target_frames if f < n_frames])))

        base, ext = os.path.splitext(output_path)

        for i, frame_idx in enumerate(target_frames):
            img.seek(frame_idx)
            frame_path = f"{base}_{frame_idx}{ext}"
            img.save(frame_path, "PNG")
            print(f"Saved frame {frame_idx} to {frame_path}")

    else:
        # 静止画の場合
        img.save(output_path, "PNG")
        print(f"Saved static image to {output_path}")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
