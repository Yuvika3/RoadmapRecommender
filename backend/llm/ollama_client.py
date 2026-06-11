import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"  # use the available 1.5b model


def parse_roadmap_markdown(markdown_text: str) -> dict:
    explanation = ""
    roadmap = {}
    
    # Extract Roadmap Overview and How ML Scores Shaped This Roadmap as explanation
    overview_match = re.search(r"## Roadmap Overview\n(.*?)(?=\n##|$)", markdown_text, re.DOTALL)
    scores_match = re.search(r"## How ML Scores Shaped This Roadmap\n(.*?)(?=\n##|$)", markdown_text, re.DOTALL)
    
    parts = []
    if overview_match:
        parts.append(overview_match.group(1).strip())
    if scores_match:
        parts.append(scores_match.group(1).strip())
        
    explanation = "\n\n".join(parts)
    
    # If explanation is empty, grab the text before Phase 1 / Week 1
    if not explanation:
        pre_week_match = re.search(r"^(.*?)(?=\n### Week|\n## Phase|$)", markdown_text, re.DOTALL)
        if pre_week_match:
            explanation = pre_week_match.group(1).strip()
            
    # Find all weeks
    week_blocks = re.split(r"\n### (Week \d+.*?)\n", markdown_text)
    
    if len(week_blocks) > 1:
        for i in range(1, len(week_blocks), 2):
            week_header = week_blocks[i].strip()
            content = week_blocks[i+1]
            content = re.split(r"\n## ", content)[0]
            content = re.split(r"\n### ", content)[0]
            
            tasks = []
            
            # 1. Estimated Load
            load_match = re.search(r"Estimated load:\s*(.*)", content, re.IGNORECASE)
            if load_match:
                tasks.append(f"Estimated Load: {load_match.group(1).strip('* ')}")
                
            # 2. Skill Name
            skill_match = re.search(r"#### Skill:\s*(.*)", content, re.IGNORECASE)
            if skill_match:
                tasks.append(f"Skill: {skill_match.group(1).strip('* ')}")
                
            # 3. Bullet points from the week content
            bullet_points = re.findall(r"^\s*-\s*\*\*(.*?)\*\*:\s*(.*)", content, re.MULTILINE)
            if not bullet_points:
                bullet_points = re.findall(r"^\s*-\s*\*\*(.*?):\*\*:\s*(.*)", content, re.MULTILINE)
            if not bullet_points:
                bullet_points = re.findall(r"^\s*-\s*\*\*(.*?):\*\*\s*(.*)", content, re.MULTILINE)
            if not bullet_points:
                bullet_points = re.findall(r"^\s*-\s*\*\*(.*?)\*\*\s*:?\s*(.*)", content, re.MULTILINE)
                
            for key, val in bullet_points:
                key_clean = key.strip().rstrip(":").strip()
                val_clean = val.strip()
                if key_clean.lower() != "ml score":
                    tasks.append(f"{key_clean}: {val_clean}")
                    
            if not tasks:
                lines = [line.strip("-* ").strip() for line in content.split("\n") if line.strip()]
                tasks = [line for line in lines if not line.startswith("Estimated load:") and not line.startswith("####")]
                
            roadmap[week_header] = tasks
            
    if not explanation:
        explanation = "AI generated learning roadmap."
        
    return {
        "explanation": explanation,
        "roadmap": roadmap
    }



def generate_roadmap_with_ollama(goal: str, level: str, hours_per_week: int, scores: dict) -> dict:
    scores_json = json.dumps(scores, indent=2)

    prompt = f"""You are an expert learning mentor and curriculum designer.

## INPUTS

Goal: {goal}
Current Level: {level}
Available Time: {hours_per_week} hours per week

ML Skill Scores (relevance, difficulty, time_feasibility each 0-1):
{scores_json}

## TASK

Using the ML scores and your domain knowledge, generate a detailed week-by-week learning roadmap.

Rules:
- High relevance + low difficulty = teach first
- High relevance + high difficulty = split across multiple weeks
- Low time_feasibility = spread out or mark optional
- Never assign more than 2-3 new concepts per week
- Respect prerequisite order (infer from domain knowledge)
- Estimate hours per task, stay within {hours_per_week} hours/week

## OUTPUT FORMAT (Markdown only, no JSON)

# Learning Roadmap: {goal}

## Roadmap Overview
(2-3 sentences: arc of learning, total duration, key skills)

## How ML Scores Shaped This Roadmap
(4-6 sentences naming specific skills and trade-offs)

## Phase 1: Foundation

### Week 1 - [Theme]
**Estimated load:** X of {hours_per_week} hours

#### Skill: [Name]
- **Why this matters:** one sentence
- **ML Score:** Relevance: X | Difficulty: X | Time Feasibility: X
- **Topics:** subtopic 1, subtopic 2, subtopic 3
- **Common mistakes:** mistake 1, mistake 2
- **Resources:** resource name - platform - format - estimated time
- **Practice:** specific mini-project or exercise
- **Mastery criteria:** move on when you can [testable condition]

(repeat for all weeks and phases)

## Weekly Summary Table

| Week | Focus | Key Skills | Est. Hours | Milestone |
|------|-------|------------|------------|-----------|

## Deferred Skills
(list any skipped/deferred skills and why)

## Final Advice
(3-5 specific, actionable tips for this goal and level)

STRICT RULES:
- No emojis
- No vague advice like "practice regularly"
- No hallucinated URLs — name the platform instead if unsure
- Markdown only
"""

    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )

    if response.status_code != 200:
        raise RuntimeError(f"Ollama request failed with status {response.status_code}")

    result = response.json()
    raw = result.get("response", "").strip()

    if not raw:
        raise RuntimeError("Empty response from Ollama")

    return parse_roadmap_markdown(raw)


def format_roadmap_with_ollama(goal: str, level: str, hours_per_week: int, rule_based_roadmap: dict, scores: dict) -> dict:
    scores_json = json.dumps(scores, indent=2)
    roadmap_json = json.dumps(rule_based_roadmap, indent=2)

    prompt = f"""You are an expert learning mentor and curriculum designer.

## INPUTS

Goal: {goal}
Current Level: {level}
Available Time: {hours_per_week} hours per week

ML Skill Scores (relevance, difficulty, time_feasibility each 0-1):
{scores_json}

Draft Rule-Based Roadmap (system-generated ordering):
{roadmap_json}

## TASK

Enhance and expand the draft roadmap into a detailed, mentor-quality learning plan.

Rules:
- Use ML scores to justify ordering — name specific scores in your explanation
- High relevance + low difficulty = teach first
- High relevance + high difficulty = split across multiple weeks
- Low time_feasibility = spread out or mark optional
- Never assign more than 2-3 new concepts per week
- Respect prerequisite order (infer from domain knowledge)
- Estimate hours per task, stay within {hours_per_week} hours/week

## OUTPUT FORMAT (Markdown only, no JSON)

# Learning Roadmap: {goal}

## Roadmap Overview
(2-3 sentences: arc of learning, total duration, key skills)

## How ML Scores Shaped This Roadmap
(4-6 sentences naming specific skills and trade-offs)

## Phase 1: Foundation

### Week 1 - [Theme]
**Estimated load:** X of {hours_per_week} hours

#### Skill: [Name]
- **Why this matters:** one sentence
- **ML Score:** Relevance: X | Difficulty: X | Time Feasibility: X
- **Topics:** subtopic 1, subtopic 2, subtopic 3
- **Common mistakes:** mistake 1, mistake 2
- **Resources:** resource name - platform - format - estimated time
- **Practice:** specific mini-project or exercise
- **Mastery criteria:** move on when you can [testable condition]

(repeat for all weeks and phases)

## Weekly Summary Table

| Week | Focus | Key Skills | Est. Hours | Milestone |
|------|-------|------------|------------|-----------|

## Deferred Skills
(list any skipped/deferred skills and why)

## Final Advice
(3-5 specific, actionable tips for this goal and level)

STRICT RULES:
- No emojis
- No vague advice like "practice regularly"
- No hallucinated URLs — name the platform instead if unsure
- Markdown only
"""

    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )

    if response.status_code != 200:
        raise RuntimeError(f"Ollama request failed with status {response.status_code}")

    result = response.json()
    raw = result.get("response", "").strip()

    if not raw:
        raise RuntimeError("Empty response from Ollama during formatting")

    return parse_roadmap_markdown(raw)