"""
Learning Plan Manager module.
Handles validation, creation, regeneration, and lifecycle of personalized study plans.
"""

from typing import Dict, Any, List, Tuple, Optional
import database
import ai_service


def validate_learner_inputs(
    subject: str,
    goal: str,
    level: str,
    duration_days: Any,
    daily_study_minutes: Any
) -> Tuple[bool, Optional[str]]:
    """
    Validates input parameters for creating or regenerating a study plan.
    Returns (is_valid, error_message).
    """
    if not subject or not subject.strip():
        return False, "Subject cannot be empty. Please enter what you want to learn."

    if len(subject.strip()) < 2:
        return False, "Subject is too short. Please provide a clear subject name."

    if not goal or not goal.strip():
        return False, "Learning goal cannot be empty. Please describe what you want to achieve."

    valid_levels = ["Beginner", "Intermediate", "Advanced"]
    if level not in valid_levels:
        return False, f"Level must be one of: {', '.join(valid_levels)}"

    try:
        days = int(duration_days)
        if days < 1 or days > 90:
            return False, "Target duration must be between 1 and 90 days."
    except (ValueError, TypeError):
        return False, "Target duration must be a valid positive whole number of days."

    try:
        minutes = int(daily_study_minutes)
        if minutes < 10 or minutes > 600:
            return False, "Daily study time must be between 10 and 600 minutes."
    except (ValueError, TypeError):
        return False, "Daily study time must be a valid positive whole number of minutes."

    return True, None


def create_and_store_learning_plan(
    subject: str,
    goal: str,
    level: str,
    duration_days: int,
    daily_study_minutes: int,
    existing_learner_id: Optional[int] = None
) -> Tuple[Optional[int], Optional[Dict[str, Any]], Optional[str]]:
    """
    Validates inputs, generates learning plan via Gemini AI, stores learner & plan in SQLite.
    Returns (learner_id, plan_data, error_message).
    """
    is_valid, err = validate_learner_inputs(subject, goal, level, duration_days, daily_study_minutes)
    if not is_valid:
        return None, None, err

    try:
        # 1. Generate plan using AI
        plan_data = ai_service.generate_learning_plan_ai(
            subject=subject.strip(),
            goal=goal.strip(),
            level=level,
            duration_days=int(duration_days),
            daily_study_minutes=int(daily_study_minutes)
        )

        # 2. Persist learner
        if existing_learner_id:
            database.update_learner(
                existing_learner_id,
                subject=subject.strip(),
                goal=goal.strip(),
                level=level,
                duration_days=int(duration_days),
                daily_study_minutes=int(daily_study_minutes)
            )
            learner_id = existing_learner_id
        else:
            learner_id = database.create_learner(
                subject=subject.strip(),
                goal=goal.strip(),
                level=level,
                duration_days=int(duration_days),
                daily_study_minutes=int(daily_study_minutes)
            )

        # 3. Persist plan items
        database.save_learning_plan(learner_id, plan_data["days"])

        return learner_id, plan_data, None

    except Exception as e:
        return None, None, f"Failed to generate study plan: {str(e)}"


def regenerate_learning_plan(
    learner_id: int,
    subject: str,
    goal: str,
    level: str,
    duration_days: int,
    daily_study_minutes: int
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Regenerates a learning plan for an existing learner with updated preferences.
    """
    lid, plan_data, err = create_and_store_learning_plan(
        subject=subject,
        goal=goal,
        level=level,
        duration_days=duration_days,
        daily_study_minutes=daily_study_minutes,
        existing_learner_id=learner_id
    )
    if err:
        return False, None, err
    return True, plan_data, None


def get_current_plan(learner_id: int) -> List[Dict[str, Any]]:
    """Fetches the latest structured learning plan for a learner from SQLite."""
    return database.get_learning_plan(learner_id)


def get_next_recommended_topic(learner_id: int) -> Dict[str, Any]:
    """
    Determines the next topic the learner should focus on:
    1. Topics that need revision (scored < 70% in quiz)
    2. In Progress topics
    3. Next pending topic in sequential order
    4. Plan completion congratulation
    """
    plan = database.get_learning_plan(learner_id)
    if not plan:
        return {
            "type": "none",
            "message": "No active study plan found. Please create a plan to get started.",
            "topic": None
        }

    # Check for topics needing revision first
    for item in plan:
        if item.get("status") == "Needs Revision":
            return {
                "type": "revision",
                "message": f"Review '{item['topic']}' and take another practice quiz to strengthen your understanding.",
                "topic": item["topic"],
                "day_number": item["day_number"]
            }

    # Check for in-progress topics
    for item in plan:
        if item.get("status") == "In Progress":
            return {
                "type": "continue",
                "message": f"Continue practicing '{item['topic']}' (Day {item['day_number']}).",
                "topic": item["topic"],
                "day_number": item["day_number"]
            }

    # Check for next pending topic
    for item in plan:
        if item.get("status") == "Pending":
            return {
                "type": "next",
                "message": f"Proceed to Day {item['day_number']}: '{item['topic']}'.",
                "topic": item["topic"],
                "day_number": item["day_number"]
            }

    # All completed
    return {
        "type": "completed",
        "message": "Congratulations! You have completed all topics in your plan. Retake quizzes for any topic to retain mastery.",
        "topic": plan[0]["topic"] if plan else None
    }

