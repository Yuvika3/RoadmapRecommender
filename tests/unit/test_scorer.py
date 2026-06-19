import unittest
import sys
import os

# Add backend directory to sys.path so we can import ml modules
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from ml.scoring.scorer import score_skills

class TestScorer(unittest.TestCase):

    def assert_valid_scores(self, scores, expected_skills):
        self.assertIsInstance(scores, dict)
        for skill in expected_skills:
            self.assertIn(skill, scores)
            skill_scores = scores[skill]
            self.assertIn("skill_relevance_score", skill_scores)
            self.assertIn("difficulty_score", skill_scores)
            self.assertIn("time_feasibility_score", skill_scores)
            
            # Verify they are float in [0.0, 1.0] range
            for score_name, score_val in skill_scores.items():
                self.assertIsInstance(score_val, float)
                self.assertTrue(0.0 <= score_val <= 1.0, f"{score_name} ({score_val}) is out of [0, 1] range for {skill}")

    def test_backend_developer_beginner(self):
        # Test default backend skills for a beginner
        scores = score_skills("Become a Backend Developer", "beginner", 10)
        expected_skills = ["python", "fastapi", "sql", "postgresql", "docker"]
        self.assert_valid_scores(scores, expected_skills)

    def test_frontend_developer_intermediate(self):
        # Test frontend path with intermediate experience level
        scores = score_skills("Senior Frontend Developer", "intermediate", 15)
        expected_skills = ["javascript", "html/css", "react", "next.js"]
        self.assert_valid_scores(scores, expected_skills)

    def test_specific_skill_in_goal(self):
        # Test explicitly mentioned skill (Rust)
        scores = score_skills("Rust Web Programming", "advanced", 20)
        self.assertIn("rust", scores)
        self.assert_valid_scores(scores, ["rust"])

    def test_general_developer_fallback(self):
        # Test default fallback when goal has no matching career path
        scores = score_skills("Learning to program", "beginner", 5)
        expected_skills = ["python", "sql", "docker"]
        self.assert_valid_scores(scores, expected_skills)

if __name__ == "__main__":
    unittest.main()
