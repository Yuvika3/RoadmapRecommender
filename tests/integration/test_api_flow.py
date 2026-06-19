import unittest
from unittest.mock import patch
import sys
import os

# Set testing environment variable BEFORE importing app modules
os.environ["TESTING"] = "1"

# Add backend directory to sys.path so we can import app modules
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.api.routes.roadmap import generate_roadmap, RoadmapRequest

class TestApiFlow(unittest.TestCase):

    @patch("app.api.routes.roadmap.generate_roadmap_with_ollama")
    @patch("app.api.routes.roadmap.score_skills")
    def test_direct_ollama_success(self, mock_score, mock_generate):
        # Setup mocks
        mock_score.return_value = {
            "python": {"skill_relevance_score": 0.9, "difficulty_score": 0.3, "time_feasibility_score": 0.8}
        }
        mock_generate.return_value = {
            "roadmap": {"Week 1": ["Learn Python variables"]},
            "explanation": "Direct LLM response"
        }

        # Run endpoint handler
        request_data = RoadmapRequest(goal="Python Basics", current_level="beginner", hours_per_week=5)
        response = generate_roadmap(request_data)

        # Assertions
        self.assertEqual(response["source"], "ollama")
        self.assertEqual(response["roadmap"], {"Week 1": ["Learn Python variables"]})
        self.assertEqual(response["explanation"], "Direct LLM response")
        mock_score.assert_called_once_with("Python Basics", "beginner", 5)
        mock_generate.assert_called_once()

    @patch("app.api.routes.roadmap.format_roadmap_with_ollama")
    @patch("app.api.routes.roadmap.generate_rule_based_roadmap")
    @patch("app.api.routes.roadmap.generate_roadmap_with_ollama")
    @patch("app.api.routes.roadmap.score_skills")
    def test_fallback_to_ollama_formatting(self, mock_score, mock_generate, mock_rule_based, mock_format):
        # Direct generation fails
        mock_generate.side_effect = RuntimeError("Ollama direct fail")
        
        # Fallback mocks
        mock_score.return_value = {
            "python": {"skill_relevance_score": 0.9, "difficulty_score": 0.3, "time_feasibility_score": 0.8}
        }
        mock_rule_based.return_value = {
            "week_1": ["python"]
        }
        mock_format.return_value = {
            "roadmap": {"Week 1": ["Actionable Python task"]},
            "explanation": "Formatted fallback response"
        }

        # Run
        request_data = RoadmapRequest(goal="Python Basics", current_level="beginner", hours_per_week=5)
        response = generate_roadmap(request_data)

        # Assertions
        self.assertEqual(response["source"], "ollama_fallback")
        self.assertEqual(response["roadmap"], {"Week 1": ["Actionable Python task"]})
        self.assertEqual(response["explanation"], "Formatted fallback response")
        mock_generate.assert_called_once()
        mock_rule_based.assert_called_once()
        mock_format.assert_called_once()

    @patch("app.api.routes.roadmap.format_roadmap_with_ollama")
    @patch("app.api.routes.roadmap.generate_rule_based_roadmap")
    @patch("app.api.routes.roadmap.generate_roadmap_with_ollama")
    @patch("app.api.routes.roadmap.score_skills")
    def test_complete_llm_failure_raw_fallback(self, mock_score, mock_generate, mock_rule_based, mock_format):
        # Both direct generation and formatting fail
        mock_generate.side_effect = RuntimeError("Ollama direct fail")
        mock_format.side_effect = RuntimeError("Ollama formatting fail")
        
        mock_score.return_value = {
            "python": {"skill_relevance_score": 0.9, "difficulty_score": 0.3, "time_feasibility_score": 0.8}
        }
        mock_rule_based.return_value = {
            "week_1": ["python"]
        }

        # Run
        request_data = RoadmapRequest(goal="Python Basics", current_level="beginner", hours_per_week=5)
        response = generate_roadmap(request_data)

        # Assertions
        self.assertEqual(response["source"], "fallback")
        self.assertEqual(response["roadmap"], {"Week 1": ["python"]})
        self.assertIn("curated learning plan is tailored to guide you", response["explanation"])

    @classmethod
    def tearDownClass(cls):
        # Clean up test database file if it exists
        from app.db.session import get_db_path
        db_path = get_db_path()
        if os.path.exists(db_path) and "test_roadmap.db" in db_path:
            try:
                os.remove(db_path)
            except Exception as e:
                print(f"Failed to remove test database: {e}")


if __name__ == "__main__":
    unittest.main()
