"""
Database module for AI Personalized Learning Coach.
Manages SQLite database initialization, CRUD operations, and queries.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import closing
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learning_coach.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes all required database tables if they do not exist."""
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()

            # 1. LEARNERS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    level TEXT NOT NULL,
                    duration_days INTEGER NOT NULL,
                    daily_study_minutes INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 2. LEARNING_PLANS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    learner_id INTEGER NOT NULL,
                    day_number INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    estimated_minutes INTEGER NOT NULL,
                    practice_activity TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    FOREIGN KEY (learner_id) REFERENCES learners (id) ON DELETE CASCADE
                )
            """)

            # 3. QUIZZES
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    learner_id INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    questions_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (learner_id) REFERENCES learners (id) ON DELETE CASCADE
                )
            """)

            # 4. QUIZ_ATTEMPTS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_id INTEGER NOT NULL,
                    learner_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    attempted_at TEXT NOT NULL,
                    FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE,
                    FOREIGN KEY (learner_id) REFERENCES learners (id) ON DELETE CASCADE
                )
            """)

            # 5. TOPIC_PROGRESS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    learner_id INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    best_score INTEGER NOT NULL DEFAULT 0,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    needs_revision INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (learner_id) REFERENCES learners (id) ON DELETE CASCADE,
                    UNIQUE(learner_id, topic)
                )
            """)


# ==========================================
# LEARNER CRUD
# ==========================================

def create_learner(subject: str, goal: str, level: str, duration_days: int, daily_study_minutes: int) -> int:
    """Inserts a new learner and returns the learner id."""
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            created_at = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO learners (subject, goal, level, duration_days, daily_study_minutes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (subject.strip(), goal.strip(), level, int(duration_days), int(daily_study_minutes), created_at))
            return cursor.lastrowid


def get_learner(learner_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a learner by id."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learners WHERE id = ?", (learner_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_latest_learner() -> Optional[Dict[str, Any]]:
    """Retrieves the most recent learner from database."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learners ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None


def update_learner(learner_id: int, subject: str, goal: str, level: str, duration_days: int, daily_study_minutes: int):
    """Updates learner profile details."""
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE learners
                SET subject = ?, goal = ?, level = ?, duration_days = ?, daily_study_minutes = ?
                WHERE id = ?
            """, (subject.strip(), goal.strip(), level, int(duration_days), int(daily_study_minutes), learner_id))


# ==========================================
# LEARNING PLAN CRUD
# ==========================================

def save_learning_plan(learner_id: int, days_data: List[Dict[str, Any]]) -> bool:
    """
    Saves or replaces the learning plan for a learner.
    Also initializes topic_progress records for newly introduced topics.
    """
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM learning_plans WHERE learner_id = ?", (learner_id,))

            for item in days_data:
                day_num = int(item.get("day_number", 1))
                topic = str(item.get("topic", "")).strip()
                objective = str(item.get("objective", "")).strip()
                est_min = int(item.get("estimated_minutes", 30))
                activity = str(item.get("practice_activity", "")).strip()
                status = item.get("status", "Pending")

                cursor.execute("""
                    INSERT INTO learning_plans (learner_id, day_number, topic, objective, estimated_minutes, practice_activity, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (learner_id, day_num, topic, objective, est_min, activity, status))

                cursor.execute("""
                    INSERT OR IGNORE INTO topic_progress (learner_id, topic, status, best_score, attempt_count, needs_revision)
                    VALUES (?, ?, 'Pending', 0, 0, 0)
                """, (learner_id, topic))

            return True


def get_learning_plan(learner_id: int) -> List[Dict[str, Any]]:
    """Retrieves all day items of a learner's learning plan."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM learning_plans
            WHERE learner_id = ?
            ORDER BY day_number ASC
        """, (learner_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def update_plan_status(plan_id: int, status: str):
    """Updates the status of a single day's plan."""
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE learning_plans SET status = ? WHERE id = ?", (status, plan_id))


def update_plan_status_by_topic(learner_id: int, topic: str, status: str):
    """Updates the status of plan items matching a topic."""
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE learning_plans
                SET status = ?
                WHERE learner_id = ? AND LOWER(topic) = LOWER(?)
            """, (status, learner_id, topic.strip()))


# ==========================================
# QUIZ & ATTEMPTS CRUD
# ==========================================

def save_quiz(learner_id: int, topic: str, questions: List[Dict[str, Any]]) -> int:
    """Saves a generated quiz to database and returns quiz_id."""
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            created_at = datetime.now().isoformat()
            q_json = json.dumps(questions)
            cursor.execute("""
                INSERT INTO quizzes (learner_id, topic, questions_json, created_at)
                VALUES (?, ?, ?, ?)
            """, (learner_id, topic.strip(), q_json, created_at))
            return cursor.lastrowid


def get_quiz(quiz_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a quiz by id with parsed questions_json."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        try:
            res["questions"] = json.loads(res["questions_json"])
        except Exception:
            res["questions"] = []
        return res


def record_quiz_attempt(quiz_id: int, learner_id: int, score: int, total_questions: int, percentage: float) -> int:
    """
    Saves a completed quiz attempt.
    Each attempt is recorded separately to preserve attempt history.
    """
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            attempted_at = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO quiz_attempts (quiz_id, learner_id, score, total_questions, percentage, attempted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (quiz_id, learner_id, int(score), int(total_questions), float(percentage), attempted_at))
            return cursor.lastrowid


def get_quiz_attempts_history(learner_id: int, limit: int = 15) -> List[Dict[str, Any]]:
    """Returns recent quiz attempts with topic information."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                qa.id,
                qa.quiz_id,
                qa.score,
                qa.total_questions,
                qa.percentage,
                qa.attempted_at,
                q.topic
            FROM quiz_attempts qa
            JOIN quizzes q ON qa.quiz_id = q.id
            WHERE qa.learner_id = ?
            ORDER BY qa.id DESC
            LIMIT ?
        """, (learner_id, limit))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


# ==========================================
# TOPIC PROGRESS & MASTERY
# ==========================================

def update_topic_progress(learner_id: int, topic: str, score: int, total_questions: int, percentage: float) -> Dict[str, Any]:
    """
    Updates or inserts topic progress based on a quiz attempt.
    """
    with closing(get_db_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM topic_progress WHERE learner_id = ? AND LOWER(topic) = LOWER(?)", 
                           (learner_id, topic.strip()))
            row = cursor.fetchone()

            current_best = 0
            attempts = 0
            if row:
                current_best = row["best_score"]
                attempts = row["attempt_count"]

            new_best = max(current_best, score)
            new_attempts = attempts + 1
            needs_rev = 1 if percentage < 70.0 else 0

            if percentage >= 90.0:
                status = "Completed"
            elif percentage >= 70.0:
                status = "In Progress"
            else:
                status = "Needs Revision"

            if row:
                cursor.execute("""
                    UPDATE topic_progress
                    SET status = ?, best_score = ?, attempt_count = ?, needs_revision = ?
                    WHERE id = ?
                """, (status, new_best, new_attempts, needs_rev, row["id"]))
            else:
                cursor.execute("""
                    INSERT INTO topic_progress (learner_id, topic, status, best_score, attempt_count, needs_revision)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (learner_id, topic.strip(), status, new_best, new_attempts, needs_rev))

            cursor.execute("""
                UPDATE learning_plans
                SET status = ?
                WHERE learner_id = ? AND LOWER(topic) = LOWER(?)
            """, (status, learner_id, topic.strip()))

            return {
                "topic": topic,
                "status": status,
                "best_score": new_best,
                "attempt_count": new_attempts,
                "needs_revision": bool(needs_rev)
            }


def get_all_topic_progress(learner_id: int) -> List[Dict[str, Any]]:
    """Retrieves all topic progress items for a learner."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM topic_progress
            WHERE learner_id = ?
            ORDER BY id ASC
        """, (learner_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


# ==========================================
# DASHBOARD METRICS
# ==========================================

def get_dashboard_metrics(learner_id: int) -> Dict[str, Any]:
    """Computes real metrics from SQLite for the learner."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM learning_plans WHERE learner_id = ?", (learner_id,))
        plans = [r["status"] for r in cursor.fetchall()]

        total_topics = len(plans)
        completed = sum(1 for s in plans if s == "Completed")
        needs_revision = sum(1 for s in plans if s == "Needs Revision")
        in_progress = sum(1 for s in plans if s == "In Progress")
        pending = sum(1 for s in plans if s == "Pending")

        overall_progress = round((completed / total_topics * 100), 1) if total_topics > 0 else 0.0

        cursor.execute("""
            SELECT score, total_questions, percentage, attempted_at
            FROM quiz_attempts
            WHERE learner_id = ?
            ORDER BY attempted_at DESC
        """, (learner_id,))
        attempts = [dict(r) for r in cursor.fetchall()]

        total_attempts = len(attempts)
        avg_score = round(sum(a["percentage"] for a in attempts) / total_attempts, 1) if total_attempts > 0 else 0.0

        distinct_days = set()
        for a in attempts:
            try:
                dt = datetime.fromisoformat(a["attempted_at"])
                distinct_days.add(dt.date())
            except Exception:
                pass
        streak_days = len(distinct_days) if distinct_days else (1 if total_topics > 0 else 0)

        return {
            "total_topics": total_topics,
            "completed_topics": completed,
            "in_progress_topics": in_progress,
            "pending_topics": pending,
            "needs_revision_topics": needs_revision,
            "overall_progress_percentage": overall_progress,
            "average_quiz_score": avg_score,
            "total_attempts": total_attempts,
            "streak_days": streak_days
        }
