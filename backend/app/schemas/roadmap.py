from pydantic import BaseModel
from typing import List

class RoadmapRequest(BaseModel):
    goal: str
    current_skills: List[str] = []
    hours_per_day: int
    days_available: int
    skill_level: str = "beginner"
    learning_style: str = "mixed"

    #input schema for roadmap generation request