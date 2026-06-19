import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from catboost import CatBoostRegressor, Pool

# Base directory for the scoring module
CURRENT_DIR = Path(__file__).resolve().parent

# Define the features exactly matching the CatBoost schema
CATEGORICAL_FEATURES = [
    "skill_category",
    "is_core_skill",
    "skill_current_usage_pct",
    "skill_future_interest_pct",
]

NUMERICAL_FEATURES = [
    "prerequisite_count",
    "difficulty_estimate",
    "avg_learning_time_hours",
    "skill_market_demand",
    "weekly_hours_available",
    "target_role_match_score",
    "weeks_to_complete",
    "demand_x_role",
    "prereq_x_difficulty",
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

# Define a comprehensive database of standard developer skills with base attributes
BASE_SKILLS = [
    # Programming
    {"skill_name": "Python", "skill_category": "Programming", "prerequisite_count": 1, "difficulty_estimate": 4, "avg_learning_time_hours": 80, "skill_market_demand": 0.95},
    {"skill_name": "JavaScript", "skill_category": "Programming", "prerequisite_count": 1, "difficulty_estimate": 4, "avg_learning_time_hours": 80, "skill_market_demand": 0.95},
    {"skill_name": "Go", "skill_category": "Programming", "prerequisite_count": 2, "difficulty_estimate": 5, "avg_learning_time_hours": 100, "skill_market_demand": 0.85},
    {"skill_name": "Rust", "skill_category": "Programming", "prerequisite_count": 3, "difficulty_estimate": 8, "avg_learning_time_hours": 150, "skill_market_demand": 0.80},
    {"skill_name": "TypeScript", "skill_category": "Programming", "prerequisite_count": 2, "difficulty_estimate": 5, "avg_learning_time_hours": 60, "skill_market_demand": 0.90},
    {"skill_name": "Java", "skill_category": "Programming", "prerequisite_count": 2, "difficulty_estimate": 6, "avg_learning_time_hours": 120, "skill_market_demand": 0.85},

    # Frontend
    {"skill_name": "HTML/CSS", "skill_category": "Frontend", "prerequisite_count": 1, "difficulty_estimate": 3, "avg_learning_time_hours": 40, "skill_market_demand": 0.90},
    {"skill_name": "React", "skill_category": "Frontend", "prerequisite_count": 2, "difficulty_estimate": 5, "avg_learning_time_hours": 80, "skill_market_demand": 0.95},
    {"skill_name": "Vue", "skill_category": "Frontend", "prerequisite_count": 2, "difficulty_estimate": 4, "avg_learning_time_hours": 60, "skill_market_demand": 0.75},
    {"skill_name": "Next.js", "skill_category": "Frontend", "prerequisite_count": 3, "difficulty_estimate": 5, "avg_learning_time_hours": 50, "skill_market_demand": 0.88},

    # Backend
    {"skill_name": "Node.js", "skill_category": "Backend", "prerequisite_count": 2, "difficulty_estimate": 5, "avg_learning_time_hours": 80, "skill_market_demand": 0.90},
    {"skill_name": "Django", "skill_category": "Backend", "prerequisite_count": 2, "difficulty_estimate": 5, "avg_learning_time_hours": 90, "skill_market_demand": 0.80},
    {"skill_name": "FastAPI", "skill_category": "Backend", "prerequisite_count": 2, "difficulty_estimate": 4, "avg_learning_time_hours": 50, "skill_market_demand": 0.85},
    {"skill_name": "Spring Boot", "skill_category": "Backend", "prerequisite_count": 3, "difficulty_estimate": 7, "avg_learning_time_hours": 140, "skill_market_demand": 0.85},

    # Database
    {"skill_name": "SQL", "skill_category": "Database", "prerequisite_count": 1, "difficulty_estimate": 3, "avg_learning_time_hours": 40, "skill_market_demand": 0.95},
    {"skill_name": "PostgreSQL", "skill_category": "Database", "prerequisite_count": 2, "difficulty_estimate": 4, "avg_learning_time_hours": 50, "skill_market_demand": 0.90},
    {"skill_name": "MongoDB", "skill_category": "Database", "prerequisite_count": 2, "difficulty_estimate": 4, "avg_learning_time_hours": 40, "skill_market_demand": 0.80},
    {"skill_name": "Redis", "skill_category": "Database", "prerequisite_count": 2, "difficulty_estimate": 4, "avg_learning_time_hours": 30, "skill_market_demand": 0.85},

    # DevOps
    {"skill_name": "Docker", "skill_category": "DevOps", "prerequisite_count": 2, "difficulty_estimate": 5, "avg_learning_time_hours": 50, "skill_market_demand": 0.90},
    {"skill_name": "Kubernetes", "skill_category": "DevOps", "prerequisite_count": 3, "difficulty_estimate": 7, "avg_learning_time_hours": 100, "skill_market_demand": 0.85},
    {"skill_name": "CI/CD", "skill_category": "DevOps", "prerequisite_count": 2, "difficulty_estimate": 5, "avg_learning_time_hours": 40, "skill_market_demand": 0.88},

    # Cloud
    {"skill_name": "AWS", "skill_category": "Cloud", "prerequisite_count": 2, "difficulty_estimate": 6, "avg_learning_time_hours": 100, "skill_market_demand": 0.92},
    {"skill_name": "Google Cloud", "skill_category": "Cloud", "prerequisite_count": 2, "difficulty_estimate": 6, "avg_learning_time_hours": 90, "skill_market_demand": 0.80},
]

# Cache loaded models
MODELS = {}

def load_models_if_needed():
    """Dynamically load and cache the models when first required."""
    targets = ["skill_relevance_score", "difficulty_score", "time_feasibility_score"]
    for t in targets:
        if t not in MODELS:
            model_path = CURRENT_DIR / f"v2_catboost_{t}.cbm"
            if not model_path.exists():
                raise FileNotFoundError(f"CatBoost model file not found: {model_path}")
            model = CatBoostRegressor()
            model.load_model(str(model_path))
            MODELS[t] = model

def engineer_features(data: pd.DataFrame) -> pd.DataFrame:
    """Derive custom interaction and decay features."""
    d = data.copy()
    d["weeks_to_complete"] = d["avg_learning_time_hours"] / d["weekly_hours_available"]
    d["demand_x_role"] = d["skill_market_demand"] * d["target_role_match_score"]
    d["prereq_x_difficulty"] = d["prerequisite_count"] * d["difficulty_estimate"]
    return d

def select_skills_to_score(goal: str) -> list[dict]:
    """
    Selects a highly relevant subset of skills based on the career path 
    and technologies mentioned in the goal.
    """
    goal_lower = goal.lower()
    selected_skills = []
    
    # 1. Identify specific skills explicitly mentioned in the user's goal
    mentioned_skills = []
    for skill in BASE_SKILLS:
        skill_name_lower = skill["skill_name"].lower()
        if skill_name_lower == "html/css":
            if "html" in goal_lower or "css" in goal_lower:
                mentioned_skills.append(skill)
        elif skill_name_lower in goal_lower:
            mentioned_skills.append(skill)

    # 2. Assign career path defaults to keep roadmaps cohesive and realistic
    defaults = []
    if "backend" in goal_lower:
        defaults = ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker"]
    elif "frontend" in goal_lower:
        defaults = ["JavaScript", "HTML/CSS", "React", "Next.js"]
    elif any(term in goal_lower for term in ["fullstack", "full stack", "full-stack"]):
        defaults = ["JavaScript", "HTML/CSS", "React", "Node.js", "SQL", "Docker"]
    elif any(term in goal_lower for term in ["devops", "sre"]):
        defaults = ["Python", "Docker", "Kubernetes", "CI/CD", "AWS"]
    elif "cloud" in goal_lower:
        defaults = ["Python", "Docker", "AWS", "Google Cloud"]
    elif any(term in goal_lower for term in ["data", "ml", "machine", "analytics"]):
        defaults = ["Python", "SQL", "PostgreSQL"]
    else:
        # Default fallback (original 3 core skills)
        defaults = ["Python", "SQL", "Docker"]
        
    # Combine career defaults and explicitly mentioned technologies
    seen_names = set()
    for skill in BASE_SKILLS:
        if skill["skill_name"] in defaults or skill in mentioned_skills:
            if skill["skill_name"] not in seen_names:
                selected_skills.append(skill.copy())
                seen_names.add(skill["skill_name"])

    # Fallback to general baseline if empty
    if not selected_skills:
        for skill in BASE_SKILLS:
            if skill["skill_name"] in ["Python", "SQL", "Docker"]:
                selected_skills.append(skill.copy())

    return selected_skills

def score_skills(goal: str, current_level: str, hours_per_week: int) -> dict:
    """
    Predicts relevance, difficulty, and feasibility scores for relevant skills 
    using pre-trained CatBoost models.
    """
    load_models_if_needed()
    
    # 1. Filter skills based on user's goal
    skills = select_skills_to_score(goal)
    goal_lower = goal.lower()
    level_lower = current_level.lower()
    
    # 2. Build feature matrix
    rows = []
    for skill in skills:
        row = skill.copy()
        
        # Determine is_core_skill and target_role_match_score
        skill_name_lower = skill["skill_name"].lower()
        if skill_name_lower in goal_lower or (skill_name_lower == "html/css" and ("html" in goal_lower or "css" in goal_lower)):
            row["is_core_skill"] = 1
            row["target_role_match_score"] = 1.0
        else:
            # Career path mapping
            category = skill["skill_category"]
            if "backend" in goal_lower:
                if category == "Backend":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.95
                elif category == "Database":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.90
                elif category == "Programming":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.85
                elif category == "DevOps":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.70
                elif category == "Cloud":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.60
                else: # Frontend
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.20
            elif "frontend" in goal_lower:
                if category == "Frontend":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.95
                elif category == "Programming":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.85
                elif category == "Backend":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.30
                elif category == "Database":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.20
                else:
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.10
            elif any(term in goal_lower for term in ["fullstack", "full stack", "full-stack"]):
                if category in ["Frontend", "Backend"]:
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.95
                elif category in ["Programming", "Database"]:
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.90
                elif category in ["DevOps", "Cloud"]:
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.70
            elif any(term in goal_lower for term in ["devops", "sre"]):
                if category in ["DevOps", "Cloud"]:
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.95
                elif category == "Programming":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.80
                elif category == "Backend":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.50
                elif category == "Database":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.40
                else:
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.10
            elif "cloud" in goal_lower:
                if category == "Cloud":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.95
                elif category == "DevOps":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.85
                elif category == "Programming":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.80
                elif category == "Backend":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.50
                else:
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.20
            elif any(term in goal_lower for term in ["data", "ml", "machine", "analytics"]):
                if category == "Programming" and skill["skill_name"] in ["Python", "SQL"]:
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.95
                elif category == "Database":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.90
                elif category == "Programming":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.70
                elif category == "Cloud":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.60
                elif category == "DevOps":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.40
                else:
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.10
            else:
                # Default general developer fallback
                if category == "Programming":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.90
                elif category == "Backend":
                    row["is_core_skill"] = 1
                    row["target_role_match_score"] = 0.80
                elif category == "Database":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.70
                elif category == "Frontend":
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.70
                else:
                    row["is_core_skill"] = 0
                    row["target_role_match_score"] = 0.50

        # Set experience level mapping
        if level_lower == "beginner":
            row["skill_current_usage_pct"] = 0
            row["skill_future_interest_pct"] = 1
        elif level_lower == "intermediate":
            row["skill_current_usage_pct"] = 1 if skill["prerequisite_count"] == 1 else 0
            row["skill_future_interest_pct"] = 1 if row["skill_current_usage_pct"] == 0 else 0
        elif level_lower == "advanced":
            row["skill_current_usage_pct"] = 1 if skill["prerequisite_count"] <= 2 else 0
            row["skill_future_interest_pct"] = 1 if row["skill_current_usage_pct"] == 0 else 0
        else:
            row["skill_current_usage_pct"] = 0
            row["skill_future_interest_pct"] = 1

        row["weekly_hours_available"] = float(hours_per_week)
        rows.append(row)

    # 3. Create DataFrame and run feature engineering
    df = pd.DataFrame(rows)
    df = engineer_features(df)

    # Make Pool object for CatBoost
    pool = Pool(data=df[ALL_FEATURES], cat_features=CATEGORICAL_FEATURES)

    # 4. Predict and clip scores to [0.0, 1.0]
    rel = np.clip(MODELS["skill_relevance_score"].predict(pool), 0.0, 1.0)
    diff = np.clip(MODELS["difficulty_score"].predict(pool), 0.0, 1.0)
    feas = np.clip(MODELS["time_feasibility_score"].predict(pool), 0.0, 1.0)

    # 5. Format results as expected by the API router and LLM
    result = {}
    for i, skill in enumerate(skills):
        name_key = skill["skill_name"].lower()
        result[name_key] = {
            "skill_relevance_score": round(float(rel[i]), 4),
            "difficulty_score": round(float(diff[i]), 4),
            "time_feasibility_score": round(float(feas[i]), 4),
        }

    return result