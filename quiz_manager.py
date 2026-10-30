"""
Quiz Manager module.
Handles quiz generation, schema validation, Python-based scoring,
performance classification, weak topic detection, and persistence.
"""

from typing import Dict, Any, List, Tuple, Optional
import database
import ai_service


def get_performance_tier(percentage: float) -> Tuple[str, str, str]:
    """
    Categorizes performance based on Python-calculated percentage:
    90–100: Strong
    70–89: Good Progress
    50–69: Needs Practice
    0–49: Needs Revision
    
    Returns (category_name, badge_color, summary_statement).
    """
    if percentage >= 90.0:
        return (
            "Strong",
            "#10b981",  # emerald green
            "This quiz result indicates strong mastery of key concepts in this topic."
        )
    elif percentage >= 70.0:
        return (
            "Good Progress",
            "#3b82f6",  # blue
            "This quiz result demonstrates solid progress with a few minor areas to refine."
        )
    elif percentage >= 50.0:
        return (
            "Needs Practice",
            "#f59e0b",  # amber
            "This quiz result suggests that this topic may need additional practice."
        )
    else:
        return (
            "Needs Revision",
            "#ef4444",  # red
            "This quiz result suggests that this topic needs focused revision before moving forward."
        )


def validate_quiz_structure(questions: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """
    Validates that the questions list conforms strictly to expected schema:
    - Exactly 5 questions (or at least 3-5 valid questions)
    - Each question has non-empty text, options list of 4 choices, valid correct_answer ('A','B','C','D'), and explanation.
    """
    if not isinstance(questions, list) or len(questions) == 0:
        return False, "Quiz must contain a list of questions."

    for idx, q in enumerate(questions, 1):
        if not isinstance(q, dict):
            return False, f"Question {idx} is malformed."
        if not q.get("question") or not str(q.get("question")).strip():
            return False, f"Question {idx} is missing question text."
        options = q.get("options")
        if not isinstance(options, list) or len(options) < 2:
            return False, f"Question {idx} must have at least 2 choices."
        correct = str(q.get("correct_answer", "")).strip().upper()
        if len(correct) > 1 and correct[0] in ["A", "B", "C", "D"]:
            correct = correct[0]
        if correct not in ["A", "B", "C", "D"]:
            return False, f"Question {idx} has invalid correct_answer: {correct}."

    return True, None


def create_topic_quiz(
    learner_id: int,
    subject: str,
    topic: str,
    level: str
) -> Tuple[Optional[int], Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Generates a 5-question multiple choice quiz via Gemini AI, validates it,
    and stores it in the SQLite database.
    """
    try:
        raw_questions = ai_service.generate_quiz_ai(
            subject=subject,
            topic=topic,
            level=level
        )

        is_valid, err = validate_quiz_structure(raw_questions)
        if not is_valid:
            return None, None, f"Generated quiz validation failed: {err}"

        # Persist quiz to SQLite
        quiz_id = database.save_quiz(learner_id, topic, raw_questions)
        return quiz_id, raw_questions, None

    except Exception as e:
        return None, None, f"Something went wrong while generating your quiz. Please try again. ({str(e)})"


def evaluate_quiz(
    quiz_id: int,
    learner_id: int,
    topic: str,
    questions: List[Dict[str, Any]],
    user_answers: Dict[int, str],
    level: str = "Beginner"
) -> Dict[str, Any]:
    """
    Calculates quiz score strictly in Python. Never asks Gemini to score.
    Computes performance tier, updates topic progress & attempt history,
    and retrieves qualitative AI coaching tips.
    """
    total_questions = len(questions)
    correct_count = 0
    question_results = []
    wrong_questions = []

    for idx, q in enumerate(questions):
        expected_letter = str(q.get("correct_answer", "")).strip().upper()
        if len(expected_letter) > 1 and expected_letter[0] in ["A", "B", "C", "D"]:
            expected_letter = expected_letter[0]

        # User selected answer might be "A", "B", or "A) Option text"
        raw_selected = user_answers.get(idx, "")
        selected_letter = str(raw_selected).strip().upper()
        if len(selected_letter) > 1 and selected_letter[0] in ["A", "B", "C", "D"]:
            selected_letter = selected_letter[0]

        is_correct = (selected_letter == expected_letter)
        if is_correct:
            correct_count += 1
        else:
            wrong_questions.append({
                "question": q.get("question"),
                "selected_answer": raw_selected,
                "correct_answer": expected_letter,
                "explanation": q.get("explanation", "")
            })

        question_results.append({
            "index": idx + 1,
            "question": q.get("question"),
            "options": q.get("options", []),
            "selected_raw": raw_selected,
            "selected_letter": selected_letter,
            "correct_letter": expected_letter,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    # Calculate percentage in Python
    percentage = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0.0

    category, color, summary_note = get_performance_tier(percentage)

    # 1. Record this quiz attempt in SQLite (each attempt saved separately)
    attempt_id = database.record_quiz_attempt(
        quiz_id=quiz_id,
        learner_id=learner_id,
        score=correct_count,
        total_questions=total_questions,
        percentage=percentage
    )

    # 2. Update topic progress in SQLite
    topic_prog = database.update_topic_progress(
        learner_id=learner_id,
        topic=topic,
        score=correct_count,
        total_questions=total_questions,
        percentage=percentage
    )

    # 3. Dynamic recommendation based on performance
    if percentage >= 70.0:
        recommended_action = "Good job! You have demonstrated strong competency. You are ready to move to the next topic in your study plan or tackle an advanced project challenge."
        needs_revision = False
    else:
        recommended_action = f"Review the learning objectives for '{topic}' and take another practice quiz to solidify your understanding."
        needs_revision = True

    # 4. Generate qualitative feedback using Gemini (factual scoring logic remains in Python)
    ai_feedback = ai_service.generate_feedback_ai(
        topic=topic,
        level=level,
        score=correct_count,
        total=total_questions,
        percentage=percentage,
        performance_category=category,
        wrong_questions=wrong_questions
    )

    return {
        "attempt_id": attempt_id,
        "quiz_id": quiz_id,
        "topic": topic,
        "score": correct_count,
        "total_questions": total_questions,
        "percentage": percentage,
        "category": category,
        "color": color,
        "summary_note": summary_note,
        "question_results": question_results,
        "wrong_questions": wrong_questions,
        "needs_revision": needs_revision,
        "recommended_action": recommended_action,
        "topic_progress": topic_prog,
        "ai_feedback": ai_feedback
    }

