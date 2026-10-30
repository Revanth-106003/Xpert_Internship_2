"""
Unit and Integration Test Suite for AI Personalized Learning Coach.
Validates all 9 critical test cases defined in the project specification.
"""

import os
import unittest
from unittest.mock import patch
import database
import ai_service
import learning_plan
import quiz_manager


class TestAIPersonalizedLearningCoach(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize test database
        database.init_db()

    def test_01_validation_missing_subject_or_goal(self):
        """TEST 1: Missing subject or goal displays validation error."""
        # Missing subject
        valid, err = learning_plan.validate_learner_inputs("", "Learn Python", "Beginner", 5, 30)
        self.assertFalse(valid)
        self.assertIn("Subject cannot be empty", err)

        # Missing goal
        valid, err = learning_plan.validate_learner_inputs("Python", "", "Beginner", 5, 30)
        self.assertFalse(valid)
        self.assertIn("Learning goal cannot be empty", err)

        # Invalid duration
        valid, err = learning_plan.validate_learner_inputs("Python", "Learn basics", "Beginner", 0, 30)
        self.assertFalse(valid)
        self.assertIn("Target duration", err)

        # Invalid daily study time
        valid, err = learning_plan.validate_learner_inputs("Python", "Learn basics", "Beginner", 5, 0)
        self.assertFalse(valid)
        self.assertIn("Daily study time", err)

    def test_02_database_persistence_learner_and_plan(self):
        """TEST 7 & TEST 2: Learner & Plan creation and SQLite persistence."""
        lid = database.create_learner("Python Testing", "Master unit tests", "Intermediate", 3, 40)
        self.assertIsInstance(lid, int)
        self.assertGreater(lid, 0)

        learner = database.get_learner(lid)
        self.assertEqual(learner["subject"], "Python Testing")
        self.assertEqual(learner["goal"], "Master unit tests")

        sample_days = [
            {
                "day_number": 1,
                "topic": "Unit Test Basics",
                "objective": "Understand assert and test cases",
                "estimated_minutes": 40,
                "practice_activity": "Write test cases for calculator",
                "status": "Pending"
            },
            {
                "day_number": 2,
                "topic": "Mocking & Fixtures",
                "objective": "Use unittest.mock and setup fixtures",
                "estimated_minutes": 40,
                "practice_activity": "Mock API calls in service layer",
                "status": "Pending"
            }
        ]
        saved = database.save_learning_plan(lid, sample_days)
        self.assertTrue(saved)

        fetched_plan = database.get_learning_plan(lid)
        self.assertEqual(len(fetched_plan), 2)
        self.assertEqual(fetched_plan[0]["topic"], "Unit Test Basics")

    def test_03_invalid_json_handling(self):
        """TEST 3: Safely handles malformed AI response text without crashing."""
        malformed_texts = [
            "```json\n{\"subject\": \"Python\", \"days\": []}\n```",
            "Random text before {\"subject\": \"Python\", \"days\": [{\"day_number\": 1, \"topic\": \"Loops\"}]} text after",
            "This is completely invalid non-json string",
        ]
        
        # Testing parsing helper
        parsed1 = ai_service._clean_and_parse_json(malformed_texts[0])
        self.assertIn("days", parsed1)

        parsed2 = ai_service._clean_and_parse_json(malformed_texts[1])
        self.assertEqual(len(parsed2["days"]), 1)

        with self.assertRaises(Exception):
            ai_service._clean_and_parse_json(malformed_texts[2])

    @patch("ai_service.generate_feedback_ai")
    def test_04_python_scoring_exactness(self, mock_feedback):
        """TEST 4: Python calculates score and percentages accurately."""
        mock_feedback.return_value = {
            "what_you_did_well": "Good progress",
            "areas_to_improve": "Keep practicing",
            "coach_tip": "Review edge cases"
        }

        # 5 mock questions
        questions = [
            {"question": "Q1", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E1"},
            {"question": "Q2", "options": ["A", "B", "C", "D"], "correct_answer": "B", "explanation": "E2"},
            {"question": "Q3", "options": ["A", "B", "C", "D"], "correct_answer": "C", "explanation": "E3"},
            {"question": "Q4", "options": ["A", "B", "C", "D"], "correct_answer": "D", "explanation": "E4"},
            {"question": "Q5", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "E5"},
        ]

        lid = database.create_learner("Scoring Test", "Test math", "Beginner", 5, 30)
        qid = database.save_quiz(lid, "Test Math", questions)

        # 5/5 = 100%
        ans_all_correct = {0: "A", 1: "B", 2: "C", 3: "D", 4: "A"}
        res100 = quiz_manager.evaluate_quiz(qid, lid, "Test Math", questions, ans_all_correct)
        self.assertEqual(res100["score"], 5)
        self.assertEqual(res100["percentage"], 100.0)
        self.assertEqual(res100["category"], "Strong")

        # 3/5 = 60%
        ans_3 = {0: "A", 1: "B", 2: "C", 3: "A", 4: "B"}
        res60 = quiz_manager.evaluate_quiz(qid, lid, "Test Math", questions, ans_3)
        self.assertEqual(res60["score"], 3)
        self.assertEqual(res60["percentage"], 60.0)
        self.assertEqual(res60["category"], "Needs Practice")

        # 1/5 = 20%
        ans_1 = {0: "A", 1: "A", 2: "A", 3: "A", 4: "B"}
        res20 = quiz_manager.evaluate_quiz(qid, lid, "Test Math", questions, ans_1)
        self.assertEqual(res20["score"], 1)
        self.assertEqual(res20["percentage"], 20.0)
        self.assertEqual(res20["category"], "Needs Revision")

    @patch("ai_service.generate_feedback_ai")
    def test_05_weak_topic_detection_and_revision(self, mock_feedback):
        """TEST 5: Low quiz score marks topic for revision and advises review."""
        mock_feedback.return_value = {"what_you_did_well": "Tried hard", "areas_to_improve": "All", "coach_tip": "Review"}

        lid = database.create_learner("Python Control Flow", "Master loops", "Beginner", 3, 30)
        questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_answer": "A", "explanation": "Exp"}
        ]
        qid = database.save_quiz(lid, "While Loops", questions)

        # Score 0% (wrong answer)
        res = quiz_manager.evaluate_quiz(qid, lid, "While Loops", questions, {0: "B"})
        self.assertEqual(res["score"], 0)
        self.assertTrue(res["needs_revision"])
        self.assertIn("Needs Revision", res["category"])
        self.assertIn("Review the learning objectives", res["recommended_action"])

        # Check in DB
        tp = database.get_all_topic_progress(lid)
        found = [t for t in tp if t["topic"] == "While Loops"]
        self.assertTrue(len(found) > 0)
        self.assertEqual(found[0]["needs_revision"], 1)

    @patch("ai_service.generate_feedback_ai")
    def test_06_high_score_recommendation(self, mock_feedback):
        """TEST 6: High quiz score recommends next topic or harder practice."""
        mock_feedback.return_value = {"what_you_did_well": "All", "areas_to_improve": "None", "coach_tip": "Advance"}

        lid = database.create_learner("Python Advanced", "Decorators", "Advanced", 3, 45)
        questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_answer": "A", "explanation": "Exp"}
        ]
        qid = database.save_quiz(lid, "Decorators", questions)

        # Score 100%
        res = quiz_manager.evaluate_quiz(qid, lid, "Decorators", questions, {0: "A"})
        self.assertEqual(res["score"], 1)
        self.assertFalse(res["needs_revision"])
        self.assertIn("Strong", res["category"])
        self.assertIn("move to the next topic", res["recommended_action"])

    @patch("ai_service.generate_feedback_ai")
    def test_07_repeated_quiz_attempts_saved_separately(self, mock_feedback):
        """TEST 9: Repeated quiz attempts are saved separately in database."""
        mock_feedback.return_value = {"what_you_did_well": "A", "areas_to_improve": "B", "coach_tip": "C"}

        lid = database.create_learner("Repeated Quiz", "Test history", "Beginner", 2, 30)
        questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_answer": "A", "explanation": "Exp"}
        ]
        qid = database.save_quiz(lid, "History Topic", questions)

        # Attempt 1: 0%
        quiz_manager.evaluate_quiz(qid, lid, "History Topic", questions, {0: "B"})
        # Attempt 2: 100%
        quiz_manager.evaluate_quiz(qid, lid, "History Topic", questions, {0: "A"})
        # Attempt 3: 100%
        quiz_manager.evaluate_quiz(qid, lid, "History Topic", questions, {0: "A"})

        history = database.get_quiz_attempts_history(lid)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["percentage"], 100.0)
        self.assertEqual(history[2]["percentage"], 0.0)

    def test_08_gemini_api_key_error_handling(self):
        """TEST 8: Graceful error when API key is missing or invalid."""
        orig_key = os.environ.get("GEMINI_API_KEY")
        try:
            os.environ["GEMINI_API_KEY"] = ""
            with self.assertRaises(ValueError) as ctx:
                ai_service.get_gemini_client()
            self.assertIn("GEMINI_API_KEY is not configured", str(ctx.exception))
        finally:
            if orig_key:
                os.environ["GEMINI_API_KEY"] = orig_key


if __name__ == "__main__":
    unittest.main()
