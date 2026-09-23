from __future__ import annotations
"""
Preprocessing — central image preprocessing pipeline for inference.
"""
import numpy as np
from PIL import Image
from typing import Tuple
try:
    import torch
    import torchvision.transforms as T
except ImportError:
    pass


# Standard ImageNet normalisation used for ResNet
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

CLASSIFIER_SIZE = (224, 224)


def preprocess_for_classifier(image: Image.Image) -> torch.Tensor:
    """
    Preprocess a PIL image for ResNet-50 inference.
    Returns: (1, 3, 224, 224) float32 tensor
    """
    transform = T.Compose([
        T.Resize(CLASSIFIER_SIZE),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    tensor = transform(image.convert("RGB"))
    return tensor.unsqueeze(0)  # add batch dimension


def load_image_from_path(path: str) -> Image.Image:
    """Load and validate a PIL image from disk."""
    img = Image.open(path)
    img.verify()  # detect corruption
    img = Image.open(path)  # reopen after verify
    return img.convert("RGB")
