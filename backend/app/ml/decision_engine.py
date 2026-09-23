"""
Evidence-aware Decision Engine.

Produces CLEAR / REFER / ESCALATE decisions based on
image quality, classification, probabilities, and evidence agreement.

This is NOT a clinical diagnosis engine.
Outputs are screening recommendations only.
"""
from typing import Dict, Any


CONFIDENCE_THRESHOLD_CLEAR = 0.50     # Minimum confidence to consider CLEAR
CONFIDENCE_THRESHOLD_REFER = 0.45     # Minimum confidence to issue REFER rather than ESCALATE
REFERABLE_PROBABILITY_THRESHOLD = 0.50  # Sum of grade 2,3,4 probability


def make_decision(
    quality_status: str,
    predicted_grade: int,
    probabilities: Dict[str, float],
    confidence: float,
) -> Dict[str, str]:
    """
    Compute the evidence-aware screening decision.

    Rules:
    ESCALATE when:
      - quality is poor
      - confidence < threshold (uncertain output)
    REFER when:
      - quality acceptable
      - referable probability >= threshold
    CLEAR when:
      - quality acceptable
      - referable probability < threshold
      - confidence acceptable
    """
    # Map probabilities to grades 0–4
    p = {
        0: probabilities.get("grade_0", probabilities.get("0", 0.0)),
        1: probabilities.get("grade_1", probabilities.get("1", 0.0)),
        2: probabilities.get("grade_2", probabilities.get("2", 0.0)),
        3: probabilities.get("grade_3", probabilities.get("3", 0.0)),
        4: probabilities.get("grade_4", probabilities.get("4", 0.0)),
    }

    referable_prob = p[2] + p[3] + p[4]

    if quality_status == "poor":
        return {
            "decision": "escalate",
            "reason": "Additional clinical assessment is recommended because the available screening evidence is insufficient or uncertain.",
            "next_steps": "Recapture the fundus image before relying on the screening result.",
            "evidence_status": "insufficient",
        }

    if confidence < CONFIDENCE_THRESHOLD_REFER:
        return {
            "decision": "escalate",
            "reason": "Additional clinical assessment is recommended because the available screening evidence is insufficient or uncertain.",
            "next_steps": "Additional clinical assessment is recommended.",
            "evidence_status": "uncertain",
        }

    # Next steps logic based on predicted grade
    next_steps = "Continue routine diabetes and eye-care follow-up according to clinician/local screening guidance."
    if predicted_grade == 1:
        next_steps = "Clinical eye evaluation and follow-up are recommended according to the patient's diabetes and ophthalmic assessment."
    elif predicted_grade == 2:
        next_steps = "Refer for ophthalmic evaluation to assess severity and determine appropriate follow-up."
    elif predicted_grade >= 3:
        next_steps = "Prompt retina specialist evaluation is recommended."

    if referable_prob >= REFERABLE_PROBABILITY_THRESHOLD:
        return {
            "decision": "refer",
            "reason": "Potentially referable diabetic retinopathy pattern identified.",
            "next_steps": next_steps,
            "evidence_status": "sufficient",
        }

    return {
        "decision": "clear",
        "reason": "Screening did not identify a potentially referable diabetic retinopathy pattern.",
        "next_steps": next_steps,
        "evidence_status": "sufficient",
    }
