def generate_rule_based_roadmap(scores: dict) -> dict:
    """
    Deterministic fallback
    """

    ranked = sorted(
        scores.items(),
        key=lambda x: (
            x[1]["skill_relevance_score"]
            + x[1]["time_feasibility_score"]
            - x[1]["difficulty_score"]
        ),
        reverse=True
    )

    roadmap = {}
    week = 1
    for skill, _ in ranked:
        roadmap[f"week_{week}"] = [skill]
        week += 1

    return roadmap