"""
AI Service module for interacting with the Google Gemini API.
Handles prompting, JSON extraction, validation, and error management.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Attempt importing google.genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def get_gemini_client() -> Optional[Any]:
    """
    Initializes and returns the Gemini client using GEMINI_API_KEY from environment.
    Raises ValueError if the key is missing or blank.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        raise ValueError("GEMINI_API_KEY is not configured. Please set a valid key in your .env file.")

    if not GENAI_AVAILABLE:
        raise RuntimeError("google-genai package is not installed. Please run `pip install -r requirements.txt`.")

    return genai.Client(api_key=api_key)


def _clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    Cleans markdown formatting, strips backticks, and parses JSON safely.
    """
    text = raw_text.strip()
    # Strip markdown ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    # If extra text precedes or follows JSON, try to extract first {...} block
    if not (text.startswith("{") and text.endswith("}")):
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    return json.loads(text)


def generate_learning_plan_ai(
    subject: str,
    goal: str,
    level: str,
    duration_days: int,
    daily_study_minutes: int,
    model_name: str = "gemini-3.8-flash"
) -> Dict[str, Any]:
    """
    Prompts Gemini to generate a personalized day-wise learning plan in structured JSON format.
    Validates the received response and returns the dictionary.
    """
    client = get_gemini_client()

    prompt = f"""
You are an expert AI Learning Coach. Design a structured, personalized, day-by-day learning plan.

Student Details:
- Subject: {subject}
- Learning Goal: {goal}
- Current Knowledge Level: {level}
- Target Duration: {duration_days} days
- Daily Available Study Time: {daily_study_minutes} minutes

Generate a comprehensive plan covering exactly {duration_days} days.
Each day must have a focused topic, clear learning objective, estimated time in minutes (should match or be close to {daily_study_minutes}), and an actionable practice activity.

Respond ONLY with valid JSON. Do not include introductory text or commentary outside the JSON.
Follow this exact JSON structure:
{{
  "subject": "{subject}",
  "goal": "{goal}",
  "level": "{level}",
  "duration_days": {duration_days},
  "daily_study_minutes": {daily_study_minutes},
  "days": [
    {{
      "day_number": 1,
      "topic": "Clear Topic Title",
      "objective": "What the student will understand and be able to do.",
      "estimated_minutes": {daily_study_minutes},
      "practice_activity": "Hands-on project, code exercise, or problem set."
    }}
  ]
}}
"""

    models_to_try = [model_name, "gemini-flash-latest", "gemini-pro-latest"]
    last_error = None

    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )

            raw_text = response.text or ""
            data = _clean_and_parse_json(raw_text)

            # Validate basic structure
            if "days" not in data or not isinstance(data["days"], list) or len(data["days"]) == 0:
                raise ValueError("Generated plan did not contain a valid 'days' list.")

            # Validate each day entry
            sanitized_days = []
            for i, d in enumerate(data["days"]):
                day_num = d.get("day_number", i + 1)
                topic = str(d.get("topic", "")).strip() or f"Day {day_num} Topic"
                objective = str(d.get("objective", "")).strip() or "Learn fundamental principles."
                est = d.get("estimated_minutes", daily_study_minutes)
                try:
                    est = int(est)
                except Exception:
                    est = daily_study_minutes
                act = str(d.get("practice_activity", "")).strip() or "Practice exercises and self-assessment."

                sanitized_days.append({
                    "day_number": day_num,
                    "topic": topic,
                    "objective": objective,
                    "estimated_minutes": est,
                    "practice_activity": act,
                    "status": "Pending"
                })

            data["days"] = sanitized_days
            return data

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Failed to generate learning plan with Gemini AI: {str(last_error)}")


def generate_quiz_ai(
    subject: str,
    topic: str,
    level: str,
    model_name: str = "gemini-3.8-flash"
) -> List[Dict[str, Any]]:
    """
    Generates exactly 5 multiple choice questions for the selected topic using Gemini.
    Validates that each question has options, correct_answer, and explanation.
    Never asks Gemini to calculate score.
    """
    client = get_gemini_client()

    prompt = f"""
You are an expert examiner and technical tutor. Create a 5-question multiple choice quiz.

Topic: {topic}
Subject: {subject}
Target Difficulty Level: {level}

Requirements:
- Exactly 5 distinct, high-quality multiple choice questions.
- Each question must have exactly 4 choices: labeled "A", "B", "C", and "D" (or prefixed as "A) ...").
- Specify the correct answer clearly as the single letter ("A", "B", "C", or "D").
- Provide a helpful, informative explanation for why the correct answer is right and why other options are incorrect.

Return ONLY a valid JSON object with a single key "questions". No additional text.

JSON Structure:
{{
  "questions": [
    {{
      "question": "What is ...?",
      "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
      "correct_answer": "B",
      "explanation": "Option B is correct because ..."
    }}
  ]
}}
"""

    models_to_try = [model_name, "gemini-flash-latest", "gemini-pro-latest"]
    last_error = None

    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )

            raw_text = response.text or ""
            parsed = _clean_and_parse_json(raw_text)

            questions = parsed.get("questions", [])
            if not isinstance(questions, list) or len(questions) < 1:
                raise ValueError("Quiz response did not contain a valid 'questions' array.")

            validated_questions = []
            for q in questions[:5]:  # Limit to exactly 5
                question_text = str(q.get("question", "")).strip()
                options = q.get("options", [])
                correct = str(q.get("correct_answer", "")).strip().upper()
                # Normalize correct answer to single letter
                if len(correct) > 1 and correct[0] in ["A", "B", "C", "D"]:
                    correct = correct[0]

                explanation = str(q.get("explanation", "")).strip() or "No explanation provided."

                if not question_text or len(options) < 2 or correct not in ["A", "B", "C", "D"]:
                    raise ValueError(f"Invalid question format: {q}")

                validated_questions.append({
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct,
                    "explanation": explanation
                })

            if len(validated_questions) != 5:
                # If less than 5, raise to let retry or handle
                if len(validated_questions) >= 3:
                    return validated_questions
                raise ValueError(f"Expected 5 questions, but validated only {len(validated_questions)}.")

            return validated_questions

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Failed to generate quiz with Gemini AI: {str(last_error)}")


def generate_feedback_ai(
    topic: str,
    level: str,
    score: int,
    total: int,
    percentage: float,
    performance_category: str,
    wrong_questions: List[Dict[str, Any]],
    model_name: str = "gemini-3.8-flash"
) -> Dict[str, str]:
    """
    Generates personalized qualitative coaching feedback from Gemini based on quiz results.
    Does NOT calculate score - score is calculated by Python and passed in.
    """
    client = get_gemini_client()

    wrong_summary = ""
    for idx, w in enumerate(wrong_questions, 1):
        wrong_summary += f"\n- Q{idx}: {w.get('question')} (Selected: {w.get('selected_answer')}, Correct: {w.get('correct_answer')})"

    prompt = f"""
You are a supportive, encouraging AI Learning Coach.
Provide personalized feedback for a student who just completed a quiz on '{topic}'.

Performance Summary:
- Level: {level}
- Score: {score} out of {total} ({percentage}%)
- Assessment: {performance_category}
{f"Areas of confusion:{wrong_summary}" if wrong_questions else "The student got every question right!"}

Provide a short, constructive assessment in JSON format with three fields:
1. "what_you_did_well": Highlight concepts they mastered or their effort.
2. "areas_to_improve": Specific technical concepts or subtopics they should review (keep encouraging).
3. "coach_tip": One clear, actionable study tip or exercise they should try today.

Respond ONLY with valid JSON:
{{
  "what_you_did_well": "...",
  "areas_to_improve": "...",
  "coach_tip": "..."
}}
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                response_mime_type="application/json"
            )
        )
        return _clean_and_parse_json(response.text or "")
    except Exception:
        # Fallback friendly coaching feedback if AI call fails
        if percentage >= 70:
            return {
                "what_you_did_well": f"Great grasp of fundamental concepts in {topic}!",
                "areas_to_improve": "Continue strengthening edge cases and advanced applications.",
                "coach_tip": "Move ahead to the next topic in your study plan while your momentum is high."
            }
        else:
            return {
                "what_you_did_well": f"Good effort testing your knowledge on {topic}.",
                "areas_to_improve": "Review the core definitions, syntax, and reasoning explained above.",
                "coach_tip": "Re-read the learning objective, review the code examples, and retake this quiz to lock in the concepts."
            }

