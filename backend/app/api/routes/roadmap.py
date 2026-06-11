from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ml.scoring.scorer import score_skills
from llm.ollama_client import generate_roadmap_with_ollama, format_roadmap_with_ollama
from ml.fallback.rule_based import generate_rule_based_roadmap

router = APIRouter()

class RoadmapRequest(BaseModel):
    goal: str
    current_level: str
    hours_per_week: int

@router.post("/generate-roadmap")
def generate_roadmap(data: RoadmapRequest):
    # 1. ML SCORING (always runs)
    scores = score_skills(
        data.goal,
        data.current_level,
        data.hours_per_week
    )

    # 2. Try LLM roadmap
    try:
        roadmap = generate_roadmap_with_ollama(
            data.goal,
            data.current_level,
            data.hours_per_week,
            scores
        )

        return {
            "source": "ollama",
            "scores": scores,
            **roadmap
        }

    except Exception as e:
        # 3. If fail -> RULE-BASED roadmap
        try:
            fallback = generate_rule_based_roadmap(scores)
            
            # format key/value pairs nicely for standard output if we return raw fallback
            nice_roadmap = {f"Week {i+1}": v for i, (k, v) in enumerate(fallback.items())}

            # 4. If true -> get LLm to give roadmap nicely in best way
            if fallback:
                try:
                    formatted_roadmap = format_roadmap_with_ollama(
                        data.goal,
                        data.current_level,
                        data.hours_per_week,
                        fallback,
                        scores
                    )
                    return {
                        "source": "ollama_fallback",
                        "scores": scores,
                        **formatted_roadmap
                    }
                except Exception as format_e:
                    # If LLM formatting fails, return raw rule-based roadmap
                    return {
                        "source": "fallback",
                        "scores": scores,
                        "roadmap": nice_roadmap,
                        "explanation": f"Generated rule-based roadmap due to Ollama formatting issue: {str(format_e)}"
                    }
            else:
                raise ValueError("Rule-based roadmap generation failed to produce results")
        except Exception as fallback_e:
            raise HTTPException(
                status_code=500,
                detail=f"Both LLM and fallback roadmap generation failed: {str(fallback_e)}"
            )