"""
============================================================
Learning Roadmap Recommender — CatBoost Skill Scorer v2
============================================================
KEY CHANGE vs v1:
  `skill_name` is DROPPED from all features.
  The model scores any skill — Data Analysis, Rust, GenAI,
  Data Analyst, whatever — as long as you describe it via
  its attributes (difficulty, demand, learning time, etc.)

Outputs per skill:
  skill_relevance_score   float 0–1
  difficulty_score        float 0–1
  time_feasibility_score  float 0–1

Three separate CatBoostRegressor models, one per target.
============================================================
"""

import pandas as pd
import numpy as np
import json
import warnings
from pathlib import Path

from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DATA_PATH  = "/mnt/user-data/uploads/final_skill_dataset.csv"
OUTPUT_DIR = Path("/mnt/user-data/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED   = 42
TEST_SIZE     = 0.20
COMFORT_WEEKS = 12.0   # weeks threshold for feasibility decay


# ─────────────────────────────────────────────
# 1. LOAD
# ─────────────────────────────────────────────
print("=" * 60)
print("Step 1 — Loading data")
print("=" * 60)

df = pd.read_csv(DATA_PATH)
print(f"  Rows: {len(df):,}  |  Columns: {df.shape[1]}")
print(f"  Original skills in data: {sorted(df['skill_name'].unique())}")
print(f"  NOTE: skill_name is intentionally dropped from features\n")


# ─────────────────────────────────────────────
# 2. FEATURE SET  (skill_name removed)
# ─────────────────────────────────────────────
#
# skill_category  → broad domain bucket (user provides this)
#                   e.g. "Data", "Cloud", "Programming", "DevOps"
#                   CatBoost handles it natively as a categorical.
#
# is_core_skill              → is this a must-have for the target role?
# skill_current_usage_pct    → does the user already use it? (0/1)
# skill_future_interest_pct  → does the user want to learn it? (0/1)
# prerequisite_count         → how many prereqs does it have? (1–4)
# difficulty_estimate        → raw difficulty rating (3–8)
# avg_learning_time_hours    → estimated total hours to learn
# skill_market_demand        → market demand signal (0–1)
# weekly_hours_available     → how many hours/week the user can study
# target_role_match_score    → how well skill aligns with target role (0–1)
#
# Derived:
# weeks_to_complete   = avg_learning_time_hours / weekly_hours_available
# demand_x_role       = skill_market_demand × target_role_match_score
# prereq_x_difficulty = prerequisite_count × difficulty_estimate

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
    # derived below
    "weeks_to_complete",
    "demand_x_role",
    "prereq_x_difficulty",
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES


# ─────────────────────────────────────────────
# 3. FEATURE ENGINEERING + DERIVE TARGETS
# ─────────────────────────────────────────────
print("Step 2 — Feature engineering + deriving targets")

def engineer_features(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()
    d["weeks_to_complete"]   = d["avg_learning_time_hours"] / d["weekly_hours_available"]
    d["demand_x_role"]       = d["skill_market_demand"] * d["target_role_match_score"]
    d["prereq_x_difficulty"] = d["prerequisite_count"]  * d["difficulty_estimate"]
    return d

df = engineer_features(df)

# --- difficulty_score (0 = very easy, 1 = very hard) ---
# 65% weight on raw difficulty (3–8 scale normalised → 0–1)
# 35% weight on prerequisite burden (1–4 scale normalised → 0–1)
df["difficulty_score"] = (
    0.65 * (df["difficulty_estimate"] - 3) / (8 - 3)
  + 0.35 * (df["prerequisite_count"]  - 1) / (4 - 1)
).clip(0, 1)

# --- time_feasibility_score (0 = infeasible, 1 = very feasible) ---
# Exponential decay: score = exp(-weeks_needed / comfort_threshold)
# comfort = 12 weeks → score 0.37 at 12 weeks, ~0.07 at 36 weeks
df["time_feasibility_score"] = np.exp(
    -df["weeks_to_complete"] / COMFORT_WEEKS
).clip(0, 1)

TARGET_COLS = [
    "skill_relevance_score",
    "difficulty_score",
    "time_feasibility_score",
]

for t in TARGET_COLS:
    print(f"  {t:30s}  range: {df[t].min():.4f} – {df[t].max():.4f}")
print()


# ─────────────────────────────────────────────
# 4. TRAIN / TEST SPLIT
# ─────────────────────────────────────────────
# Simple random split — skill_name is no longer a feature,
# so there's no group leakage concern.
print("Step 3 — Train/test split (80/20 random)")

train_df, test_df = train_test_split(
    df, test_size=TEST_SIZE, random_state=RANDOM_SEED, shuffle=True
)
print(f"  Train: {len(train_df):,}  |  Test: {len(test_df):,}\n")


# ─────────────────────────────────────────────
# 5. CATBOOST PARAMS
# ─────────────────────────────────────────────
CATBOOST_PARAMS = dict(
    iterations            = 1000,
    learning_rate         = 0.05,
    depth                 = 6,
    l2_leaf_reg           = 3.0,
    min_data_in_leaf      = 20,
    bagging_temperature   = 1.0,
    random_strength       = 1.0,
    border_count          = 128,
    loss_function         = "RMSE",
    eval_metric           = "RMSE",
    random_seed           = RANDOM_SEED,
    verbose               = 200,
    early_stopping_rounds = 50,
    use_best_model        = True,
    task_type             = "CPU",
)


# ─────────────────────────────────────────────
# 6. TRAIN + EVALUATE
# ─────────────────────────────────────────────
print("Step 4 — Training models")

def make_pool(data, target_col):
    return Pool(
        data        = data[ALL_FEATURES],
        label       = data[target_col],
        cat_features= CATEGORICAL_FEATURES,
    )

def evaluate(model, pool, y_true, name):
    preds = np.clip(model.predict(pool), 0, 1)
    rmse  = np.sqrt(mean_squared_error(y_true, preds))
    mae   = mean_absolute_error(y_true, preds)
    r2    = r2_score(y_true, preds)
    print(f"  [{name}]  RMSE={rmse:.4f}  MAE={mae:.4f}  R²={r2:.4f}")
    return dict(model=name, RMSE=round(rmse,4), MAE=round(mae,4), R2=round(r2,4))

models  = {}
metrics = []

TARGET_NAMES = {
    "skill_relevance_score":  "Relevance",
    "difficulty_score":       "Difficulty",
    "time_feasibility_score": "Feasibility",
}

for target_col, label in TARGET_NAMES.items():
    print(f"\n  ── Training {label} model ──")
    train_pool = make_pool(train_df, target_col)
    eval_pool  = make_pool(test_df,  target_col)

    model = CatBoostRegressor(**CATBOOST_PARAMS)
    model.fit(train_pool, eval_set=eval_pool, plot=False)

    models[target_col] = model
    result = evaluate(model, eval_pool, test_df[target_col].values, label)
    metrics.append(result)


# ─────────────────────────────────────────────
# 7. FEATURE IMPORTANCE
# ─────────────────────────────────────────────
print("\n\nStep 5 — Feature importances")

for target_col, label in TARGET_NAMES.items():
    fi = pd.Series(
        models[target_col].get_feature_importance(),
        index=ALL_FEATURES
    ).sort_values(ascending=False)
    print(f"\n  [{label}] top features:")
    for feat, score in fi.head(6).items():
        print(f"    {feat:30s} {score:.2f}")


# ─────────────────────────────────────────────
# 8. SAVE MODELS + METADATA
# ─────────────────────────────────────────────
print("\n\nStep 6 — Saving")

model_paths = {}
for target_col, model in models.items():
    path = OUTPUT_DIR / f"v2_catboost_{target_col}.cbm"
    model.save_model(str(path))
    model_paths[target_col] = str(path)
    print(f"  Saved: {path}")

# save feature schema so inference always uses the right columns + cats
schema = {
    "version":             "2.0",
    "all_features":        ALL_FEATURES,
    "categorical_features":CATEGORICAL_FEATURES,
    "numerical_features":  NUMERICAL_FEATURES,
    "skill_category_values": sorted(df["skill_category"].unique().tolist()),
    "notes": {
        "skill_name": "REMOVED — model works for any skill",
        "skill_category": "broad domain bucket — user supplies this (e.g. 'Data', 'Cloud')",
    }
}
schema_path = OUTPUT_DIR / "v2_feature_schema.json"
with open(schema_path, "w") as f:
    json.dump(schema, f, indent=2)

metrics_path = OUTPUT_DIR / "v2_metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"  Saved schema:  {schema_path}")
print(f"  Saved metrics: {metrics_path}")


# ─────────────────────────────────────────────
# 9. INFERENCE FUNCTION
# ─────────────────────────────────────────────

def predict_scores(skill_rows: list[dict]) -> list[dict]:
    """
    Score any skill — including ones never seen during training.

    Each dict in skill_rows must have:
      skill_name               str   (used for output label only, NOT a model input)
      skill_category           str   broad domain: "Programming","Data","Cloud","DevOps",
                                     "Frontend","Backend","Database", or any new category
      is_core_skill            int   1 if must-have for target role, else 0
      skill_current_usage_pct  int   1 if user already uses it, else 0
      skill_future_interest_pct int  1 if user wants to learn it, else 0
      prerequisite_count       int   estimated number of prerequisites (1–4+)
      difficulty_estimate      int   difficulty rating 3–8
      avg_learning_time_hours  int   estimated total hours to become proficient
      skill_market_demand      float market demand signal 0.0–1.0
      weekly_hours_available   int   hours/week the learner can study
      target_role_match_score  float how much this skill fits the target role 0.0–1.0

    Returns:
      list of dicts — one per skill — with the 3 numeric scores.
    """
    inp = pd.DataFrame(skill_rows)
    inp = engineer_features(inp)

    pool = Pool(data=inp[ALL_FEATURES], cat_features=CATEGORICAL_FEATURES)

    rel  = np.clip(models["skill_relevance_score"].predict(pool),  0, 1)
    diff = np.clip(models["difficulty_score"].predict(pool),       0, 1)
    feas = np.clip(models["time_feasibility_score"].predict(pool), 0, 1)

    return [
        {
            "skill_name":             row["skill_name"],
            "skill_relevance_score":  round(float(rel[i]),  4),
            "difficulty_score":       round(float(diff[i]), 4),
            "time_feasibility_score": round(float(feas[i]), 4),
        }
        for i, row in enumerate(skill_rows)
    ]


# ─────────────────────────────────────────────
# 10. DEMO — skills never seen during training
# ─────────────────────────────────────────────
print("\n\nStep 7 — Demo: scoring NEW skills the model never saw")

new_skills = [
    # ── Data Analysis ──────────────────────────────────────────
    {
        "skill_name":              "Data Analysis",
        "skill_category":          "Data",
        "is_core_skill":           1,
        "skill_current_usage_pct": 0,
        "skill_future_interest_pct": 1,
        "prerequisite_count":      2,
        "difficulty_estimate":     5,
        "avg_learning_time_hours": 150,
        "skill_market_demand":     0.88,
        "weekly_hours_available":  10,
        "target_role_match_score": 0.95,
    },
    # ── Data Analyst (same domain, different profile) ──────────
    {
        "skill_name":              "Data Analyst",
        "skill_category":          "Data",
        "is_core_skill":           1,
        "skill_current_usage_pct": 0,
        "skill_future_interest_pct": 1,
        "prerequisite_count":      2,
        "difficulty_estimate":     4,
        "avg_learning_time_hours": 120,
        "skill_market_demand":     0.82,
        "weekly_hours_available":  10,
        "target_role_match_score": 0.92,
    },
    # ── Machine Learning ────────────────────────────────────────
    {
        "skill_name":              "Machine Learning",
        "skill_category":          "Data",
        "is_core_skill":           0,
        "skill_current_usage_pct": 0,
        "skill_future_interest_pct": 1,
        "prerequisite_count":      4,
        "difficulty_estimate":     8,
        "avg_learning_time_hours": 200,
        "skill_market_demand":     0.91,
        "weekly_hours_available":  10,
        "target_role_match_score": 0.70,
    },
    # ── Kubernetes (DevOps, harder, less time) ──────────────────
    {
        "skill_name":              "Kubernetes",
        "skill_category":          "DevOps",
        "is_core_skill":           0,
        "skill_current_usage_pct": 0,
        "skill_future_interest_pct": 0,
        "prerequisite_count":      3,
        "difficulty_estimate":     7,
        "avg_learning_time_hours": 160,
        "skill_market_demand":     0.78,
        "weekly_hours_available":  5,
        "target_role_match_score": 0.50,
    },
    # ── Power BI (quick + high demand for data roles) ───────────
    {
        "skill_name":              "Power BI",
        "skill_category":          "Data",
        "is_core_skill":           1,
        "skill_current_usage_pct": 0,
        "skill_future_interest_pct": 1,
        "prerequisite_count":      1,
        "difficulty_estimate":     3,
        "avg_learning_time_hours": 60,
        "skill_market_demand":     0.74,
        "weekly_hours_available":  10,
        "target_role_match_score": 0.88,
    },
]

output = predict_scores(new_skills)

print("\n  Skill scores → ready to pass to your Ollama LLM:\n")
print(json.dumps(output, indent=2))

print("\n\n✅ v2 pipeline complete.")
print("   Models saved to:", OUTPUT_DIR)
print("=" * 60)


# ─────────────────────────────────────────────
# HOW TO USE IN YOUR FASTAPI + OLLAMA SETUP
# ─────────────────────────────────────────────
USAGE = """
# ── Loading models at API startup ───────────────────────────
from catboost import CatBoostRegressor
import json, pandas as pd, numpy as np

def load_models(dir="outputs/"):
    return {
        "skill_relevance_score":   CatBoostRegressor().load_model(dir + "v2_catboost_skill_relevance_score.cbm"),
        "difficulty_score":        CatBoostRegressor().load_model(dir + "v2_catboost_difficulty_score.cbm"),
        "time_feasibility_score":  CatBoostRegressor().load_model(dir + "v2_catboost_time_feasibility_score.cbm"),
    }

# ── FastAPI endpoint ─────────────────────────────────────────
@app.post("/generate-roadmap")
async def generate_roadmap(request: RoadmapRequest):
    # 1. Score skills with CatBoost
    scores = predict_scores(request.skills)

    # 2. Build prompt for Ollama
    prompt = f\"\"\"
You are a personalized learning roadmap generator.
Use the skill scores below to create a structured learning plan.

Rules:
- Higher relevance_score → prioritize this skill
- Higher difficulty_score → spend more time on fundamentals
- Lower feasibility_score → suggest breaking it into smaller chunks

Skill scores:
{json.dumps(scores, indent=2)}

Generate a detailed week-by-week roadmap in Markdown.
\"\"\"

    # 3. Call Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5", "prompt": prompt, "stream": False}
    )
    return {"roadmap": response.json()["response"], "scores": scores}
"""
print(USAGE)

