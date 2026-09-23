"""
scripts/verify_model.py

Validates the DRUSTI ResNet-50 model checkpoint.
Run this before starting the backend server.

Usage:
    python scripts/verify_model.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np

NUM_CLASSES = 5
IMAGE_SIZE = 224
CHECKPOINT_PATH = ROOT / "models" / "classifier" / "resnet50_dr.pt"

print("="*60)
print("DRUSTI — Model Verification")
print("="*60)

# 1. Checkpoint exists
if not CHECKPOINT_PATH.exists():
    print(f"❌ FAIL: Checkpoint not found at {CHECKPOINT_PATH}")
    print("   Run: python scripts/initialize_weights.py  (or train_classifier.py)")
    sys.exit(1)
print(f"✓ Checkpoint found: {CHECKPOINT_PATH}")

# 2. Load checkpoint
checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu")
print(f"✓ Checkpoint loaded")

# 3. Metadata
arch = checkpoint.get("architecture", "unknown")
n_classes = checkpoint.get("num_classes", "unknown")
class_names = checkpoint.get("class_names", [])
print(f"✓ Architecture: {arch}")
print(f"✓ Num classes: {n_classes}")
print(f"✓ Class mapping: {checkpoint.get('class_mapping', class_names)}")

assert arch == "resnet50", f"Expected resnet50, got {arch}"
assert n_classes == NUM_CLASSES, f"Expected {NUM_CLASSES} classes, got {n_classes}"
assert len(class_names) == NUM_CLASSES, f"class_names length mismatch"

# 4. Rebuild model and load weights
model = models.resnet50(weights=None)
model.fc = nn.Sequential(
    nn.Dropout(0.3),
    nn.Linear(model.fc.in_features, NUM_CLASSES),
)

state = checkpoint.get("model_state_dict", checkpoint)
model.load_state_dict(state, strict=True)
model.eval()
print(f"✓ Weights loaded into ResNet-50 (strict=True)")

# 5. Validate output shape
with torch.inference_mode():
    test_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    output = model(test_input)
    assert output.shape == (1, NUM_CLASSES), f"Bad output shape: {output.shape}"

print(f"✓ Output shape: {output.shape} ✓")

# 6. Validate probabilities
probs = torch.softmax(output, dim=1).numpy()[0]
total = float(probs.sum())
assert abs(total - 1.0) < 1e-4, f"Probabilities don't sum to 1: {total}"
print(f"✓ Probabilities sum: {total:.6f} ✓")

# 7. CPU inference speed
import time
warmup = model(torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE))
t0 = time.perf_counter()
for _ in range(5):
    _ = model(torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE))
elapsed = (time.perf_counter() - t0) / 5
print(f"✓ CPU inference speed: {elapsed*1000:.0f}ms per image")

print()
print("="*60)
print("DRUSTI AI MODEL")
print(f"  Model:      ResNet-50")
print(f"  Classes:    {NUM_CLASSES}")
print(f"  Device:     CPU")
print(f"  Checkpoint: {CHECKPOINT_PATH.name}")
print(f"  Status:     READY")
print("="*60)
