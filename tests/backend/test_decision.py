"""Tests for the decision engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.ml.decision_engine import make_decision


def test_clear_decision():
    result = make_decision(
        quality_status="good",
        predicted_grade=0,
        probabilities={"grade_0": 0.92, "grade_1": 0.05, "grade_2": 0.02, "grade_3": 0.01, "grade_4": 0.00},
        confidence=0.92,
    )
    assert result["decision"] == "clear"


def test_refer_decision():
    result = make_decision(
        quality_status="good",
        predicted_grade=2,
        probabilities={"grade_0": 0.03, "grade_1": 0.09, "grade_2": 0.71, "grade_3": 0.13, "grade_4": 0.04},
        confidence=0.71,
    )
    assert result["decision"] == "refer"


def test_escalate_poor_quality():
    result = make_decision(
        quality_status="poor",
        predicted_grade=0,
        probabilities={"grade_0": 0.60, "grade_1": 0.20, "grade_2": 0.12, "grade_3": 0.05, "grade_4": 0.03},
        confidence=0.60,
    )
    assert result["decision"] == "escalate"


def test_escalate_low_confidence():
    result = make_decision(
        quality_status="good",
        predicted_grade=2,
        probabilities={"grade_0": 0.22, "grade_1": 0.18, "grade_2": 0.38, "grade_3": 0.14, "grade_4": 0.08},
        confidence=0.38,
    )
    assert result["decision"] == "escalate"
