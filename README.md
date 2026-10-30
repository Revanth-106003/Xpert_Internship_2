# 🎓 AI Personalized Learning Coach

An intelligent, adaptive web application that transforms user learning goals into personalized day-by-day study curricula, conducts dynamic knowledge check quizzes, calculates scores with Python precision, detects weak topics, and provides targeted AI coaching recommendations.

---

## 📌 1. Project Overview

Traditional education software forces every learner through identical linear pathways regardless of their background, available schedule, or learning speed. **AI Personalized Learning Coach** solves this problem by acting as an autonomous learning companion:

1. **Intakes Student Profile**: Subject, goal, current level (Beginner/Intermediate/Advanced), target duration in days, and daily time commitment.
2. **Generates Day-Wise Study Roadmap**: Leverages Google Gemini to formulate structured daily topics, learning objectives, and hands-on practice activities.
3. **Conducts Topic Quizzes**: Generates 5 high-yield multiple-choice questions on demand for any topic.
4. **Calculates Accurate Scores with Python**: Scoring is calculated strictly using deterministic Python logic—preventing LLM hallucination in grades.
5. **Detects Weak Areas**: Topics where the student scores below 70% are automatically flagged as `Needs Revision`.
6. **Recommends Next Actions**: Dynamically guides the student whether to proceed, practice edge cases, or review foundations.
7. **Tracks Progress**: Persists all learners, plans, quiz attempts, and topic progress in an SQLite database.

---

## ✨ 2. Key Features

- **Personalized Day-Wise Learning Plan**: Custom day-by-day roadmap tailored to the student's available daily minutes and target duration.
- **Dynamic Quiz Generation**: Exactly 5 conceptual questions with 4 choices, answer key, and detailed technical rationale per topic.
- **Python Deterministic Scoring**: Exact percentage calculation (`0%`, `20%`, `40%`, `60%`, `80%`, `100%`) with clear question breakdown.
- **Performance Classification**:
  - `90% – 100%`: **Strong**
  - `70% – 89%`: **Good Progress**
  - `50% – 69%`: **Needs Practice**
  - `0% – 49%`: **Needs Revision**
- **Dynamic Plan Regeneration**: Modify goals, duration, or knowledge level anytime to produce an updated plan.
- **AI Coaching & Qualitative Feedback**: Generates actionable feedback highlighting what was done well and study tips.
- **Progress Dashboard**:
  - Visual topic mastery status (`Completed`, `In Progress`, `Needs Revision`, `Pending`)
  - Overall progress bar and percentage
  - Average quiz score across all attempts
  - Current learning streak (calendar days)
  - Historical table of all past attempts
- **Persistent Storage**: All activities saved in SQLite, ensuring data remains available after restarting the application.
- **Modern Responsive UI**: Crafted with custom CSS, rounded cards, subtle shadows, and responsive layout.

---

## 🛠️ 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend & UI** | [Streamlit](https://streamlit.io/) | Interactive, responsive web application framework |
| **Generative AI** | [Google Gemini API](https://ai.google.dev/) (`google-genai`) | Day-by-day plan creation, 5-question quizzes, and qualitative feedback |
| **Language** | Python 3.10+ | Core application logic, scoring, and data management |
| **Database** | SQLite3 | Relational storage for learners, plans, quizzes, and attempts |
| **Config** | `python-dotenv` | Secure loading of environment variables without hardcoding keys |
| **Version Control**| Git / GitHub | Clean commit history and documentation |

---

## 🏛️ 4. Architecture

```
                    ┌────────────────────────────┐
                    │      Streamlit Web UI      │
                    │         (app.py)           │
                    └─────────────┬──────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Learning Plan    │    │ Quiz Manager     │    │ SQLite Database  │
│ Manager          │    │                  │    │ (database.py)    │
│(learning_plan.py)│    │(quiz_manager.py) │    └─────────┬────────┘
└────────┬─────────┘    └────────┬─────────┘              │
         │                       │                        │
         └───────────┬───────────┘                        │
                     ▼                                    │
          ┌─────────────────────┐                         │
          │  AI Service Layer   │                         │
          │   (ai_service.py)   │                         │
          └──────────┬──────────┘                         │
                     ▼                                    │
          ┌─────────────────────┐                         │
          │  Google Gemini API  │                         │
          └─────────────────────┘                         │
                     │                                    │
                     └───────────── Persists Data ────────┘
```

---

## 📂 5. Folder Structure

```
ai-personalized-learning-coach/
│
├── app.py                     # Main Streamlit web application & UI navigation
├── ai_service.py              # Gemini API prompt orchestration & JSON validation
├── learning_plan.py           # Plan validation, creation, regeneration, next-step logic
├── quiz_manager.py            # Quiz generation, Python scoring, performance classification
├── database.py                # SQLite schema creation, CRUD operations, metric queries
├── requirements.txt           # Python package dependencies
├── .env.example               # Template for environment configuration
├── .gitignore                 # Prevents committing API keys, cache, and database files
├── README.md                  # Comprehensive project documentation
│
└── sample_data/
    └── example_learning_plan.json   # Reference structured study plan JSON
```

---

## 🚀 6. Setup Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your machine.
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### Step 1: Clone or Navigate to the Repository
```bash
git clone <your-repository-url>
cd ai-personalized-learning-coach
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# Windows (Command Prompt / PowerShell)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 7. Environment Variable Setup

1. Copy the `.env.example` file to create your `.env` file:
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt: `copy .env.example .env`)*

2. Open `.env` and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

> ⚠️ **Security Note**: Never commit `.env` to Git. The `.gitignore` file is pre-configured to ignore `.env`, `*.db`, and cache files.

---

## 💻 8. How to Run

Launch the Streamlit web application:

```bash
streamlit run app.py
```

The application will start and open automatically in your browser at:
`http://localhost:8501`

---

## 🗄️ 9. Database Explanation

The project uses SQLite for lightweight, zero-configuration local persistence (`learning_coach.db`):

- **`learners`**: Stores user profiles (id, subject, goal, level, duration_days, daily_study_minutes, created_at).
- **`learning_plans`**: Stores day-wise curriculum items (id, learner_id, day_number, topic, objective, estimated_minutes, practice_activity, status).
- **`quizzes`**: Stores generated assessment questions in JSON format (id, learner_id, topic, questions_json, created_at).
- **`quiz_attempts`**: Records every attempt separately for historical progress tracking (id, quiz_id, learner_id, score, total_questions, percentage, attempted_at).
- **`topic_progress`**: Tracks mastery per topic (id, learner_id, topic, status, best_score, attempt_count, needs_revision).

All tables are initialized automatically on application startup.

---

## 🤖 10. Gemini Integration Explanation

The application connects to Gemini using the official `google-genai` Python SDK:
- **Strict Structured Outputs**: Prompts enforce JSON schema output (`response_mime_type="application/json"`).
- **JSON Sanitization**: Defensive parsing cleans markdown code fences (` ```json `), extracts raw JSON blocks, and handles formatting edge cases.
- **Model Fallbacks**: Configured with `gemini-3.8-flash`, `gemini-flash-latest`, and `gemini-pro-latest` for optimal latency and reliability.
- **Separation of Concerns**: Gemini generates curriculum content, conceptual questions, and qualitative advice; all scoring and database state updates are handled exclusively in Python.

---

## 🎯 11. Quiz Scoring & Weak Topic Detection

### Deterministic Python Evaluation
```python
total_questions = len(questions)  # 5
correct_count = sum(1 for q in results if q["is_correct"])
percentage = (correct_count / total_questions) * 100
```

### Performance Tiers
- **90% – 100% (Strong)**: Student demonstrated high mastery. Recommended to advance to the next scheduled topic.
- **70% – 89% (Good Progress)**: Solid foundational grasp. Ready to continue with minor practice.
- **50% – 69% (Needs Practice)**: Moderate gaps. Marked for practice before advancing.
- **0% – 49% (Needs Revision)**: Significant gaps. Automatically updates topic status to `Needs Revision` in SQLite and prescribes immediate review.

---

## 🛡️ 12. Error Handling

- **Missing / Blank Input Fields**: Form inputs are validated before sending requests. Clear warning messages appear without app crashes.
- **API Key Missing**: Displays an informative message directing user to configure `.env`.
- **Malformed AI JSON Output**: Defensive regex extraction and retry fallback mechanisms prevent runtime exceptions.
- **Database Operations**: Handled within context-managed transactions with foreign key cascades.
- **No Ugly Tracebacks**: User-facing exceptions are caught and displayed via friendly `st.error()` and `st.warning()` banners.

---

## ⚠️ 13. Limitations

- **Internet Connectivity**: Requires active internet connection to communicate with Google Gemini API endpoints.
- **Single-User Local SQLite**: Suitable for single-user desktop or personal deployment. A multi-tenant SaaS environment would benefit from PostgreSQL.

---

## 🧪 14. Testing Verification

All nine core test cases specified in the project requirements are implemented and verified:

| Test Case | Scenario | Expected Result | Status |
|---|---|---|---|
| **TEST 1** | Missing subject / goal | Displays validation warning, halts submission | ✅ Verified |
| **TEST 2** | Valid learner setup | Calls Gemini, generates structured day-wise plan | ✅ Verified |
| **TEST 3** | Invalid Gemini response | Caught safely, sanitized or retried without crash | ✅ Verified |
| **TEST 4** | Quiz submission | Python accurately calculates score & percentage | ✅ Verified |
| **TEST 5** | Low quiz score (<70%) | Topic automatically marked `Needs Revision` | ✅ Verified |
| **TEST 6** | High quiz score (≥70%) | Topic marked `Completed` / `In Progress`, recommends next topic | ✅ Verified |
| **TEST 7** | Database persistence | Plan and attempts reload correctly across restarts | ✅ Verified |
| **TEST 8** | Gemini API failure | Friendly retry / error banner displayed | ✅ Verified |
| **TEST 9** | Repeated quiz attempts | Every attempt saved as a separate historical record | ✅ Verified |

---

## 🔮 15. Future Improvements

- Flashcards generator for fast interval repetition.
- Export study plan to PDF or Markdown.
- Integration with Google Calendar to block daily study time automatically.
- Code execution sandbox to run Python practice code directly within the browser.

---

## 📄 License
This project is licensed under the MIT License.

