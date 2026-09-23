"""
Drusti ML Interface — Abstract contract for the analysis pipeline.

All inference implementations must conform to this interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from PIL import Image


class MLInterface(ABC):
    """Abstract ML analysis engine."""

    @abstractmethod
    def analyze_fundus(self, image: Image.Image, screening_id: int) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline on a fundus image.

        Returns a structured dict with:
            mode, quality, classification, calibration,
            explanation, lesions, decision
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether the engine is ready to produce results."""
        ...
