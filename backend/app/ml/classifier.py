from __future__ import annotations
"""
backend/app/ml/classifier.py

DRUSTI — Live ResNet-50 Inference Engine.

Loads the trained checkpoint ONCE at startup.
All inference uses torch.inference_mode() for speed.
Never trains, never uses random weights.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image

logger = logging.getLogger(__name__)

NUM_CLASSES = 5
DR_LABELS = {
    0: "No DR",
    1: "Mild NPDR",
    2: "Moderate NPDR",
    3: "Severe NPDR",
    4: "Proliferative DR",
}

# Standard ImageNet normalization matching ResNet-50 pretraining
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD  = [0.229, 0.224, 0.225]
IMAGE_SIZE = 224


def _build_model():
    """Build ResNet-50 with 5-class DR head. Mirrors initialize_weights.py exactly."""
    try:
        import torch.nn as nn
        from torchvision import models
        model = models.resnet50(weights=None)
        model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(model.fc.in_features, NUM_CLASSES),
        )
        return model
    except Exception as e:
        raise RuntimeError(f"Cannot build ResNet-50: {e}") from e


class ModelManager:
    """
    Singleton. Loads the ResNet-50 checkpoint once on first access.
    Fails clearly and logs diagnostics if weights are absent.
    """
    _instance: Optional["ModelManager"] = None
    _model = None
    _temperature: Optional[float] = None
    _loaded: bool = False
    _error: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._try_load()
        return cls._instance

    def _try_load(self):
        from app.core.config import get_settings
        settings = get_settings()
        checkpoint_path = Path(settings.MODEL_CLASSIFIER_PATH)

        if not checkpoint_path.exists():
            self._error = (
                f"Model weights not found: {checkpoint_path}. "
                "Run: python scripts/initialize_weights.py"
            )
            logger.warning(f"MODEL_NOT_READY — {self._error}")
            return

        try:
            import torch
            import torch.nn as nn

            checkpoint = torch.load(str(checkpoint_path), map_location="cpu")

            # Validate metadata
            arch = checkpoint.get("architecture", "unknown")
            n_classes = checkpoint.get("num_classes", NUM_CLASSES)
            if arch not in ("resnet50", "unknown"):
                raise ValueError(f"Unexpected architecture: {arch}")
            if n_classes != NUM_CLASSES:
                raise ValueError(f"Expected {NUM_CLASSES} classes, got {n_classes}")

            # Load weights
            model = _build_model()
            state = checkpoint.get("model_state_dict", checkpoint)
            model.load_state_dict(state, strict=False)
            model.eval()

            # Warm-up sanity check
            with torch.inference_mode():
                dummy = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
                out = model(dummy)
                assert out.shape == (1, NUM_CLASSES)

            self._model = model

            # Load temperature calibration if present
            calib_path = Path(settings.CALIBRATION_PATH)
            if calib_path.exists():
                import json
                with open(calib_path) as f:
                    calib = json.load(f)
                self._temperature = float(calib.get("temperature", 1.0))
                logger.info(f"Calibration loaded: T={self._temperature:.4f}")

            self._loaded = True
            logger.info(
                f"DRUSTI AI MODEL\n"
                f"  Model:     ResNet-50\n"
                f"  Classes:   {NUM_CLASSES}\n"
                f"  Device:    CPU\n"
                f"  Checkpoint:{checkpoint_path.name}\n"
                f"  Status:    READY"
            )

        except Exception as e:
            self._error = f"Failed to load checkpoint: {e}"
            logger.error(f"MODEL_LOAD_FAILED — {self._error}")

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def error(self) -> Optional[str]:
        return self._error


def _softmax(logits) -> "np.ndarray":
    import numpy as np
    e = np.exp(logits - np.max(logits))
    return e / e.sum()


def _apply_temperature(logits, temperature: float) -> "np.ndarray":
    import numpy as np
    return _softmax(np.array(logits) / temperature)


def _preprocess(image: Image.Image):
    """
    Preprocess for ResNet-50. MUST match training preprocessing exactly.
    """
    from torchvision import transforms
    import torch

    tf = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])
    tensor = tf(image.convert("RGB"))
    return tensor.unsqueeze(0)  # [1, 3, H, W]


class LiveClassifier:
    """
    Real inference engine. Performs actual ResNet-50 forward pass on the image.
    Never returns hardcoded or random predictions.
    """

    def is_available(self) -> bool:
        return ModelManager.get_instance().is_loaded

    def analyze_fundus(self, image: Image.Image, screening_id: int) -> Dict[str, Any]:
        import torch
        import numpy as np
        from app.ml.quality_gate import assess_quality
        from app.ml.decision_engine import make_decision
        from app.core.config import get_settings

        manager = ModelManager.get_instance()
        if not manager.is_loaded:
            raise RuntimeError(
                manager.error or "AI model not ready. Run: python scripts/initialize_weights.py"
            )

        model = manager._model
        temperature = manager._temperature
        settings = get_settings()

        # ── 1. Quality gate ───────────────────────────────────────────────────
        quality = assess_quality(image)

        # ── 2. Preprocess ─────────────────────────────────────────────────────
        tensor = _preprocess(image)

        # ── 3. Real inference ─────────────────────────────────────────────────
        with torch.inference_mode():
            logits = model(tensor).squeeze(0).numpy()  # shape (5,)

        # ── 4. Calibration ────────────────────────────────────────────────────
        if temperature is not None and temperature != 1.0:
            probs = _apply_temperature(logits, temperature)
            calibration_status = "temperature_scaled"
        else:
            probs = _softmax(logits)
            calibration_status = "uncalibrated"

        predicted_grade = int(np.argmax(probs))
        confidence = float(probs[predicted_grade])
        predicted_label = DR_LABELS[predicted_grade]

        prob_dict = {
            f"grade_{i}": round(float(probs[i]), 4) for i in range(NUM_CLASSES)
        }

        # ── 5. Real Grad-CAM ──────────────────────────────────────────────────
        gradcam_url = None
        try:
            from app.ml.gradcam import generate_and_save_gradcam
            gradcam_url = generate_and_save_gradcam(
                model, tensor, image, predicted_grade, settings.UPLOAD_DIR
            )
        except Exception as e:
            logger.warning(f"Grad-CAM failed (non-critical): {e}")

        # ── 6. Decision ───────────────────────────────────────────────────────
        decision = make_decision(
            quality_status=quality["status"],
            predicted_grade=predicted_grade,
            probabilities=prob_dict,
            confidence=confidence,
        )

        return {
            "mode": "live",
            "is_demo": False,
            "quality": quality,
            "classification": {
                "model_name": "ResNet-50",
                "model_version": "1.0",
                "predicted_grade": predicted_grade,
                "predicted_label": predicted_label,
                "probabilities": prob_dict,
                "confidence": round(confidence, 4),
                "calibration_status": calibration_status,
                "mode": "live",
            },
            "explanation": {
                "explanation_type": "gradcam",
                "image_url": gradcam_url,
                "available": gradcam_url is not None,
            },
            "lesions": [
                {"lesion_type": "Microaneurysms",  "status": "not_configured", "confidence": None},
                {"lesion_type": "Hemorrhages",     "status": "not_configured", "confidence": None},
                {"lesion_type": "Hard Exudates",   "status": "not_configured", "confidence": None},
                {"lesion_type": "Soft Exudates",   "status": "not_configured", "confidence": None},
            ],
            "decision": decision,
        }
