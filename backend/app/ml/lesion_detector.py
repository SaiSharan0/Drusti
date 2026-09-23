"""Lesion detector stub — supports U-Net when weights available."""
from typing import Dict, Any, List
from PIL import Image


class LesionDetector:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.available = False

    def detect(self, image: Image.Image) -> List[Dict[str, Any]]:
        return [
            {"lesion_type": "Microaneurysms", "status": "not_configured", "confidence": None},
            {"lesion_type": "Hemorrhages", "status": "not_configured", "confidence": None},
            {"lesion_type": "Hard Exudates", "status": "not_configured", "confidence": None},
            {"lesion_type": "Soft Exudates", "status": "not_configured", "confidence": None},
        ]
