"""
Demo Engine — Deterministic demo cases for system demonstration.

IMPORTANT: All outputs from this engine are DEMO DATA.
They are NOT real model inference results.
They must always be presented with the DEMO MODE label in the UI.
"""
from typing import Any, Dict
from PIL import Image
from app.ml.interface import MLInterface

DR_LABELS = {
    0: "No DR",
    1: "Mild NPDR",
    2: "Moderate NPDR",
    3: "Severe NPDR",
    4: "Proliferative DR",
}

# Deterministic fixture cases — values are fixed and do not change across requests
DEMO_CASES: Dict[str, Dict[str, Any]] = {
    "DEMO-001": {
        "label": "No DR",
        "grade": 0,
        "probabilities": {"0": 0.92, "1": 0.05, "2": 0.02, "3": 0.01, "4": 0.00},
        "confidence": 0.92,
        "quality_status": "good",
        "quality_score": 0.91,
        "decision": "clear",
        "decision_reason": "Screening did not identify a potentially referable pattern. Continue routine clinical follow-up.",
        "evidence_status": "sufficient",
        "lesions": {
            "microaneurysms": {"status": "not_detected", "confidence": None},
            "hemorrhages": {"status": "not_detected", "confidence": None},
            "hard_exudates": {"status": "not_detected", "confidence": None},
            "soft_exudates": {"status": "not_detected", "confidence": None},
        },
    },
    "DEMO-002": {
        "label": "Mild NPDR",
        "grade": 1,
        "probabilities": {"0": 0.08, "1": 0.72, "2": 0.14, "3": 0.04, "4": 0.02},
        "confidence": 0.72,
        "quality_status": "good",
        "quality_score": 0.88,
        "decision": "clear",
        "decision_reason": "Mild pattern identified. Routine monitoring is recommended per local care protocols.",
        "evidence_status": "sufficient",
        "lesions": {
            "microaneurysms": {"status": "detected", "confidence": 0.68},
            "hemorrhages": {"status": "not_detected", "confidence": None},
            "hard_exudates": {"status": "not_detected", "confidence": None},
            "soft_exudates": {"status": "not_detected", "confidence": None},
        },
    },
    "DEMO-003": {
        "label": "Moderate NPDR",
        "grade": 2,
        "probabilities": {"0": 0.03, "1": 0.09, "2": 0.71, "3": 0.13, "4": 0.04},
        "confidence": 0.71,
        "quality_status": "good",
        "quality_score": 0.87,
        "decision": "refer",
        "decision_reason": "Potentially referable pattern identified. Specialist evaluation is recommended.",
        "evidence_status": "sufficient",
        "lesions": {
            "microaneurysms": {"status": "detected", "confidence": 0.82},
            "hemorrhages": {"status": "detected", "confidence": 0.61},
            "hard_exudates": {"status": "detected", "confidence": 0.55},
            "soft_exudates": {"status": "insufficient_evidence", "confidence": None},
        },
    },
    "DEMO-004": {
        "label": "Severe NPDR",
        "grade": 3,
        "probabilities": {"0": 0.01, "1": 0.02, "2": 0.11, "3": 0.76, "4": 0.10},
        "confidence": 0.76,
        "quality_status": "good",
        "quality_score": 0.84,
        "decision": "refer",
        "decision_reason": "Potentially referable pattern consistent with severe NPDR. Urgent specialist evaluation is recommended.",
        "evidence_status": "sufficient",
        "lesions": {
            "microaneurysms": {"status": "detected", "confidence": 0.91},
            "hemorrhages": {"status": "detected", "confidence": 0.87},
            "hard_exudates": {"status": "detected", "confidence": 0.74},
            "soft_exudates": {"status": "detected", "confidence": 0.62},
        },
    },
    "DEMO-005": {
        "label": "No DR",
        "grade": 0,
        "probabilities": {"0": 0.60, "1": 0.20, "2": 0.12, "3": 0.05, "4": 0.03},
        "confidence": 0.60,
        "quality_status": "poor",
        "quality_score": 0.31,
        "decision": "escalate",
        "decision_reason": "Image quality is insufficient for reliable screening. Please recapture or upload a clearer fundus image before proceeding.",
        "evidence_status": "insufficient",
        "lesions": {
            "microaneurysms": {"status": "insufficient_evidence", "confidence": None},
            "hemorrhages": {"status": "insufficient_evidence", "confidence": None},
            "hard_exudates": {"status": "insufficient_evidence", "confidence": None},
            "soft_exudates": {"status": "insufficient_evidence", "confidence": None},
        },
        "quality_reasons": ["blur", "low_contrast", "insufficient_retinal_field"],
    },
    "DEMO-006": {
        "label": "Moderate NPDR",
        "grade": 2,
        "probabilities": {"0": 0.22, "1": 0.18, "2": 0.38, "3": 0.14, "4": 0.08},
        "confidence": 0.38,
        "quality_status": "good",
        "quality_score": 0.75,
        "decision": "escalate",
        "decision_reason": "Screening evidence is uncertain. Model confidence is below the reliable threshold. Additional clinical assessment is recommended.",
        "evidence_status": "uncertain",
        "lesions": {
            "microaneurysms": {"status": "insufficient_evidence", "confidence": None},
            "hemorrhages": {"status": "insufficient_evidence", "confidence": None},
            "hard_exudates": {"status": "insufficient_evidence", "confidence": None},
            "soft_exudates": {"status": "insufficient_evidence", "confidence": None},
        },
    },
}


class DemoEngine(MLInterface):
    """
    Deterministic demo analysis engine.
    Produces fixed, clearly labeled demo results for system demonstration.
    """

    def __init__(self, demo_case_key: str = "DEMO-003"):
        self.demo_case_key = demo_case_key

    def is_available(self) -> bool:
        return True

    def analyze_fundus(self, image: Image.Image, screening_id: int) -> Dict[str, Any]:
        case = DEMO_CASES.get(self.demo_case_key, DEMO_CASES["DEMO-003"])
        quality_reasons = case.get("quality_reasons", [])

        return {
            "mode": "demo",
            "is_demo": True,
            "quality": {
                "status": case["quality_status"],
                "score": case["quality_score"],
                "blur_score": None,
                "brightness_score": None,
                "contrast_score": None,
                "retinal_visibility": "detected" if case["quality_status"] == "good" else "partial",
                "reasons": quality_reasons,
            },
            "classification": {
                "model_name": "ResNet-50 [DEMO]",
                "model_version": "demo-1.0",
                "predicted_grade": case["grade"],
                "predicted_label": case["label"],
                "probabilities": {
                    "grade_0": case["probabilities"]["0"],
                    "grade_1": case["probabilities"]["1"],
                    "grade_2": case["probabilities"]["2"],
                    "grade_3": case["probabilities"]["3"],
                    "grade_4": case["probabilities"]["4"],
                },
                "confidence": case["confidence"],
                "calibration_status": "demo",
                "mode": "demo",
            },
            "explanation": {
                "explanation_type": "gradcam",
                "image_url": None,
                "available": False,
                "note": "Grad-CAM visualization is available in live mode with model weights.",
            },
            "lesions": [
                {
                    "lesion_type": "Microaneurysms",
                    "status": case["lesions"]["microaneurysms"]["status"],
                    "confidence": case["lesions"]["microaneurysms"]["confidence"],
                },
                {
                    "lesion_type": "Hemorrhages",
                    "status": case["lesions"]["hemorrhages"]["status"],
                    "confidence": case["lesions"]["hemorrhages"]["confidence"],
                },
                {
                    "lesion_type": "Hard Exudates",
                    "status": case["lesions"]["hard_exudates"]["status"],
                    "confidence": case["lesions"]["hard_exudates"]["confidence"],
                },
                {
                    "lesion_type": "Soft Exudates",
                    "status": case["lesions"]["soft_exudates"]["status"],
                    "confidence": case["lesions"]["soft_exudates"]["confidence"],
                },
            ],
            "decision": {
                "decision": case["decision"],
                "reason": case["decision_reason"],
                "evidence_status": case["evidence_status"],
            },
        }


def get_demo_engine(demo_case: str = "DEMO-003") -> DemoEngine:
    return DemoEngine(demo_case_key=demo_case)
