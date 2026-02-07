#!/usr/bin/env python3
"""GPU vs CPU Embedding Benchmark"""
import time
import sys
import torch

print(f"CUDA available: {torch.cuda.is_available()}", flush=True)

from sentence_transformers import SentenceTransformer

texts = ['Activation Steering test'] * 32

print("Loading CPU model...", flush=True)
cpu = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cpu')
print("CPU loaded", flush=True)

# Warmup
cpu.encode(texts[:4])

t0 = time.time()
cpu.encode(texts, batch_size=32)
ct = time.time() - t0
print(f"CPU: {ct*1000:.0f}ms for 32 texts ({32/ct:.0f} t/s)", flush=True)

print("Loading GPU model...", flush=True)
gpu = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cuda')
print(f"GPU loaded (VRAM: {torch.cuda.memory_allocated()/1e6:.0f}MB)", flush=True)

# Warmup
gpu.encode(texts[:4])

t0 = time.time()
gpu.encode(texts, batch_size=32)
gt = time.time() - t0
print(f"GPU: {gt*1000:.0f}ms for 32 texts ({32/gt:.0f} t/s)", flush=True)

print(f"\nBatch Speedup: {ct/gt:.1f}x", flush=True)

# Single query latency
q = 'Activation Steering'
t0 = time.time()
for _ in range(50):
    cpu.encode([q])
cl = (time.time() - t0) / 50 * 1000

t0 = time.time()
for _ in range(50):
    gpu.encode([q])
gl = (time.time() - t0) / 50 * 1000

print(f"Single query: CPU={cl:.1f}ms GPU={gl:.1f}ms Speedup={cl/gl:.1f}x", flush=True)
print(f"VRAM total: {torch.cuda.memory_allocated()/1e6:.0f}MB", flush=True)
