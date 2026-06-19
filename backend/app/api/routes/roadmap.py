import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ml.scoring.scorer import score_skills
from llm.ollama_client import generate_roadmap_with_ollama, format_roadmap_with_ollama
from ml.fallback.rule_based import generate_rule_based_roadmap
from app.db.session import get_db_connection

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

    source = None
    explanation = ""
    roadmap_dict = {}

    # 2. Try LLM roadmap
    try:
        roadmap = generate_roadmap_with_ollama(
            data.goal,
            data.current_level,
            data.hours_per_week,
            scores
        )
        source = "ollama"
        explanation = roadmap.get("explanation", "Curated learning roadmap.")
        roadmap_dict = roadmap.get("roadmap", {})

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
                    source = "ollama_fallback"
                    explanation = formatted_roadmap.get("explanation", "Formatted learning roadmap.")
                    roadmap_dict = formatted_roadmap.get("roadmap", {})
                except Exception as format_e:
                    # If LLM formatting fails, return raw rule-based roadmap
                    source = "fallback"
                    explanation = "This curated learning plan is tailored to guide you through the essential skill progression for your objective. Follow the weekly milestones to build comprehensive competence."
                    roadmap_dict = nice_roadmap
            else:
                raise ValueError("Rule-based roadmap generation failed to produce results")
        except Exception as fallback_e:
            raise HTTPException(
                status_code=500,
                detail=f"Both LLM and fallback roadmap generation failed: {str(fallback_e)}"
            )

    # Save to SQLite DB
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO roadmaps (goal, current_level, hours_per_week, scores, explanation, roadmap, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.goal,
                data.current_level,
                data.hours_per_week,
                json.dumps(scores),
                explanation,
                json.dumps(roadmap_dict),
                source
            )
        )
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        
        return {
            "id": inserted_id,
            "source": source,
            "scores": scores,
            "explanation": explanation,
            "roadmap": roadmap_dict
        }
    except Exception as db_e:
        print(f"Failed to save roadmap to database: {db_e}")
        return {
            "source": source,
            "scores": scores,
            "explanation": explanation,
            "roadmap": roadmap_dict
        }

@router.get("/roadmaps")
def get_roadmaps():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, goal, current_level, hours_per_week, source, created_at FROM roadmaps ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roadmaps/{roadmap_id}")
def get_roadmap(roadmap_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roadmaps WHERE id = ?", (roadmap_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        
        res = dict(row)
        res["scores"] = json.loads(res["scores"])
        res["roadmap"] = json.loads(res["roadmap"])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/roadmaps/{roadmap_id}")
def delete_roadmap(roadmap_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM roadmaps WHERE id = ?", (roadmap_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Roadmap deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))