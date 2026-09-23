from pydantic import BaseModel
from typing import Optional


class AnalyticsSummary(BaseModel):
    total_screenings: int
    today_screenings: int
    clear_count: int
    refer_count: int
    escalate_count: int
    poor_quality_count: int
    pending_review_count: int
    demo_count: int
    live_count: int
