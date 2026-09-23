"""
Calibration — temperature scaling for probability calibration.
"""
import json
import os
import numpy as np
from typing import Dict, Optional


DR_LABELS = {
    0: "No DR",
    1: "Mild NPDR",
    2: "Moderate NPDR",
    3: "Severe NPDR",
    4: "PDR",
}

REFERABLE_GRADES = {2, 3, 4}  # Moderate, Severe, PDR are considered referable


def load_temperature(calibration_path: str) -> Optional[float]:
    """Load temperature scaling parameter from JSON file."""
    if not os.path.exists(calibration_path):
        return None
    try:
        with open(calibration_path, "r") as f:
            data = json.load(f)
        return float(data.get("temperature", 1.0))
    except Exception:
        return None


def apply_temperature_scaling(
    logits: np.ndarray, temperature: float
) -> np.ndarray:
    """
    Apply temperature scaling to raw logits.
    Returns softmax probabilities.
    """
    scaled = logits / temperature
    exp = np.exp(scaled - scaled.max())
    return exp / exp.sum()


def softmax(logits: np.ndarray) -> np.ndarray:
    exp = np.exp(logits - logits.max())
    return exp / exp.sum()


def compute_referable_probability(probs: np.ndarray) -> float:
    """Sum probabilities of referable grades (2, 3, 4)."""
    return float(probs[2] + probs[3] + probs[4])
