def score_skills(goal: str, current_level: str, hours_per_week: int) -> dict:
    """
    ML MODEL OUTPUT (CatBoost placeholder)
    Returns ONLY normalized scores
    """

    # TODO: Replace with CatBoost later
    return {
        "python": {
            "skill_relevance_score": 0.93,
            "difficulty_score": 0.40,
            "time_feasibility_score": 0.88
        },
        "sql": {
            "skill_relevance_score": 0.89,
            "difficulty_score": 0.35,
            "time_feasibility_score": 0.91
        },
        "docker": {
            "skill_relevance_score": 0.62,
            "difficulty_score": 0.70,
            "time_feasibility_score": 0.55
        }
    }