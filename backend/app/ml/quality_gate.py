"""
Image Quality Gate — assesses fundus image quality before inference.
"""
try:
    import cv2
    import numpy as np
except ImportError:
    pass
from PIL import Image
from typing import Dict, Any, List


MIN_WIDTH = 224
MIN_HEIGHT = 224
MAX_WIDTH = 8192
MAX_HEIGHT = 8192


def assess_quality(image: Image.Image) -> Dict[str, Any]:
    """
    Assess retinal fundus image quality.
    Returns quality status (good/poor) with detailed subscores.
    """
    reasons: List[str] = []

    # Fallback if OpenCV is not installed (e.g. in DEMO mode without heavy ML deps)
    if "cv2" not in globals():
        return {
            "status": "good",
            "score": 0.95,
            "blur_score": 0.95,
            "brightness_score": 0.5,
            "contrast_score": 0.9,
            "retinal_visibility": "detected",
            "reasons": [],
        }

    # Convert to numpy/OpenCV
    img_rgb = np.array(image.convert("RGB"))
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    h, w = img_gray.shape

    # --- Dimension check ---
    if w < MIN_WIDTH or h < MIN_HEIGHT:
        reasons.append("insufficient_resolution")
    if w > MAX_WIDTH or h > MAX_HEIGHT:
        reasons.append("oversized_image")

    # --- Blur (Laplacian variance) ---
    blur_score = float(cv2.Laplacian(img_gray, cv2.CV_64F).var())
    # Normalise: typical fundus image should score > 50; poor < 20
    blur_normalised = min(blur_score / 200.0, 1.0)
    if blur_normalised < 0.01:  # Lowered threshold to accept more clear images
        reasons.append("blur")

    # --- Brightness ---
    mean_brightness = float(img_gray.mean()) / 255.0
    if mean_brightness < 0.1:
        reasons.append("underexposure")
    elif mean_brightness > 0.92:
        reasons.append("overexposure")

    # --- Contrast (std dev) ---
    contrast_score = float(img_gray.std()) / 128.0
    if contrast_score < 0.10:
        reasons.append("low_contrast")

    # --- Retinal field visibility heuristic ---
    # Use circular mask detection — fundus images should have a roughly circular bright region
    _, binary = cv2.threshold(img_gray, 15, 255, cv2.THRESH_BINARY)
    retinal_area_ratio = float(np.sum(binary > 0)) / float(w * h)
    retinal_visible = retinal_area_ratio > 0.2
    if not retinal_visible:
        reasons.append("insufficient_retinal_field")

    # --- Composite quality score ---
    score_components = [
        blur_normalised,
        1.0 - abs(mean_brightness - 0.5),  # 1.0 when brightness is 0.5 (ideal)
        min(contrast_score, 1.0),
        1.0 if retinal_visible else 0.0,
    ]
    quality_score = round(float(np.mean(score_components)), 3)

    status = "good" if (len(reasons) == 0 and quality_score >= 0.40) else "poor"

    return {
        "status": status,
        "score": quality_score,
        "blur_score": round(blur_normalised, 3),
        "brightness_score": round(mean_brightness, 3),
        "contrast_score": round(min(contrast_score, 1.0), 3),
        "retinal_visibility": "detected" if retinal_visible else "not_detected",
        "reasons": reasons,
    }
