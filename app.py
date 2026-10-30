"""
AI Personalized Learning Coach - Main Streamlit Application
A modern, responsive, AI-powered learning companion that adapts study plans,
practice quizzes, and next steps to student goals and performance.
"""

import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import local modules
import database
import ai_service
import learning_plan
import quiz_manager

# Ensure environment variables are loaded
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="AI Personalized Learning Coach",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema on startup
database.init_db()


# ==========================================
# CUSTOM CSS & MODERN LIGHT ANIMATED UI/UX
# ==========================================

CUSTOM_CSS = """
<style>
/* Import modern geometric sans font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

/* Global Reset & Typography */
html, body, [class*="css"] {
    font-family: 'Plus+Jakarta+Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1e293b;
}

/* Light Ambient App Canvas */
.stApp {
    background: radial-gradient(circle at 10% 10%, #fbfcfe 0%, #f4f7fe 50%, #fef7fb 100%);
    background-attachment: fixed;
}

/* Keyframe Animations */
@keyframes slideUpFade {
    0% {
        opacity: 0;
        transform: translateY(14px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes floatHero {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-6px);
    }
}

@keyframes pulseGlow {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.2);
    }
    50% {
        box-shadow: 0 0 0 12px rgba(99, 102, 241, 0);
    }
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.animate-fade-in {
    animation: slideUpFade 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Glassmorphic Light Cards */
.modern-card {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(226, 232, 240, 0.85);
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px -4px rgba(99, 102, 241, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.modern-card:hover {
    border-color: #a5b4fc;
    box-shadow: 0 16px 36px -6px rgba(99, 102, 241, 0.12), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
    transform: translateY(-3px);
}

/* Hero Section with Light Mesh Gradient */
.hero-container {
    background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 35%, #eef2ff 70%, #f0fdf4 100%);
    background-size: 200% 200%;
    animation: gradientShift 12s ease infinite, slideUpFade 0.5s ease-out;
    border: 1.5px solid rgba(199, 210, 254, 0.6);
    border-radius: 24px;
    padding: 38px 42px;
    margin-bottom: 30px;
    box-shadow: 0 16px 40px -10px rgba(99, 102, 241, 0.1), 0 4px 12px -2px rgba(0, 0, 0, 0.02);
}

.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.7rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #3730a3 0%, #4f46e5 35%, #7c3aed 70%, #0284c7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: #475569;
    max-width: 820px;
    line-height: 1.65;
    margin-bottom: 24px;
}

/* Connected Visual Timeline */
.timeline-wrapper {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-top: 20px;
    padding: 14px 20px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 16px;
    box-shadow: 0 4px 14px -2px rgba(99, 102, 241, 0.06);
}

.timeline-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #ffffff;
    border: 1px solid #e0e7ff;
    color: #4338ca;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    box-shadow: 0 2px 5px rgba(99, 102, 241, 0.05);
    transition: transform 0.2s ease;
}

.timeline-chip:hover {
    transform: translateY(-2px);
    background: #f5f3ff;
}

.timeline-arrow {
    color: #94a3b8;
    font-weight: 800;
    font-size: 0.95rem;
}

/* Light Status Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.badge-completed {
    background-color: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
}

.badge-in-progress {
    background-color: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
}

.badge-needs-revision {
    background-color: #fff1f2;
    color: #be123c;
    border: 1px solid #fecdd3;
    animation: pulseGlow 3s infinite;
}

.badge-pending {
    background-color: #f8fafc;
    color: #64748b;
    border: 1px solid #e2e8f0;
}

/* Stat Box / Metric Cards */
.stat-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 22px 18px;
    text-align: center;
    box-shadow: 0 4px 16px -2px rgba(99, 102, 241, 0.06);
    transition: all 0.25s ease-in-out;
}

.stat-box:hover {
    transform: translateY(-3px);
    border-color: #c7d2fe;
    box-shadow: 0 12px 24px -4px rgba(99, 102, 241, 0.12);
}

.stat-icon {
    font-size: 1.4rem;
    margin-bottom: 6px;
    display: inline-block;
}

.stat-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0f172a;
    line-height: 1.1;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Modern Action Banners */
.action-banner {
    background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%);
    border-left: 6px solid #4f46e5;
    padding: 20px 24px;
    border-radius: 4px 16px 16px 4px;
    margin-bottom: 24px;
    box-shadow: 0 6px 18px -3px rgba(79, 70, 229, 0.08);
}

/* Form & Input Enhancements */
div[data-baseweb="input"], div[data-baseweb="select"] {
    border-radius: 12px !important;
}

/* Streamlit Button Tweaks */
div.stButton > button:first-child {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.4rem !important;
    border: none !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

/* Primary Button Styling */
button[kind="primary"], div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.3) !important;
}

button[kind="primary"]:hover, div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 22px 0 rgba(79, 70, 229, 0.45) !important;
}

/* Secondary Button Styling */
button[kind="secondary"], div.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    color: #334155 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
}

button[kind="secondary"]:hover, div.stButton > button[kind="secondary"]:hover {
    border-color: #cbd5e1 !important;
    background: #f8fafc !important;
    transform: translateY(-2px) !important;
}

/* Progress Bar Tweaks */
div.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #06b6d4 100%) !important;
    border-radius: 10px;
}

/* Sidebar Custom Styling & High-Contrast Light Theme */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #1e293b !important;
}

/* Radio button container & labels inside sidebar */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    gap: 8px !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    width: 100% !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background: #eef2ff !important;
    border-color: #a5b4fc !important;
    transform: translateX(3px) !important;
}

/* Force the text color of the radio option to deep bold indigo/slate */
section[data-testid="stSidebar"] div[data-testid="stRadio"] label p,
section[data-testid="stSidebar"] div[data-testid="stRadio"] label span,
section[data-testid="stSidebar"] div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
    color: #0f172a !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* Active / Checked Radio State */
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%) !important;
    border-color: #6366f1 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12) !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p,
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
    color: #3730a3 !important;
    font-weight: 800 !important;
}

/* Radio text in main body (quizzes, forms) */
div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] label p {
    color: #0f172a !important;
    font-weight: 600 !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

if "navigation_page" not in st.session_state:
    st.session_state.navigation_page = "Home"

if "current_learner_id" not in st.session_state:
    latest = database.get_latest_learner()
    st.session_state.current_learner_id = latest["id"] if latest else None

if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

if "selected_quiz_topic" not in st.session_state:
    st.session_state.selected_quiz_topic = None


def set_page(page_name: str):
    """Safely updates current navigation section without clearing state."""
    st.session_state.navigation_page = page_name


# ==========================================
# SIDEBAR NAVIGATION & PROFILE SUMMARY
# ==========================================

with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <span style="font-size: 1.8rem;">✨</span>
        <div>
            <div style="font-weight: 800; font-size: 1.15rem; color: #1e1b4b; letter-spacing: -0.02em;">Learning Coach</div>
            <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">AI Personalized EdTech</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    NAV_ICONS = {
        "Home": "🏠  Home",
        "Learner Setup": "🎯  Learner Setup",
        "Study Plan": "📚  Study Plan",
        "Practice Quiz": "📝  Practice Quiz",
        "Progress Dashboard": "📊  Progress Dashboard"
    }
    
    pages = ["Home", "Learner Setup", "Study Plan", "Practice Quiz", "Progress Dashboard"]
    selected_nav = st.radio(
        "Navigation",
        pages,
        format_func=lambda x: NAV_ICONS.get(x, x),
        index=pages.index(st.session_state.navigation_page) if st.session_state.navigation_page in pages else 0,
        label_visibility="collapsed"
    )

    if selected_nav != st.session_state.navigation_page:
        st.session_state.navigation_page = selected_nav
        st.rerun()

    st.markdown("---")

    # Display active learner profile summary
    current_learner = None
    if st.session_state.current_learner_id:
        current_learner = database.get_learner(st.session_state.current_learner_id)

    if current_learner:
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; margin-bottom: 14px;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Active Track</div>
            <div style="font-weight: 700; font-size: 1.05rem; color: #0f172a; margin-bottom: 8px;">{current_learner['subject']}</div>
            <div style="font-size: 0.85rem; color: #475569; margin-bottom: 8px;"><strong>Goal:</strong> {current_learner['goal']}</div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <span class="badge badge-in-progress">{current_learner['level']}</span>
                <span class="badge badge-pending">⏱️ {current_learner['daily_study_minutes']}m / day</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("➕ Create New Plan", use_container_width=True):
            st.session_state.navigation_page = "Learner Setup"
            st.rerun()
    else:
        st.info("No learner profile loaded yet. Start by setting up your learning goal!")

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.8rem;">
        ⚡ Powered by Google Gemini AI & Python
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# PAGE 1: HOME
# ==========================================

def render_home_page():
    # Hero Header with Light Animated Mesh
    st.markdown("""
    <div class="hero-container animate-fade-in">
        <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); padding: 5px 14px; border-radius: 9999px; margin-bottom: 14px;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #4f46e5; text-transform: uppercase; letter-spacing: 0.06em;">Next-Gen Adaptive Learning</span>
        </div>
        <div class="hero-title">AI Personalized Learning Coach</div>
        <div class="hero-subtitle">
            Your intelligent study companion that adapts daily roadmaps, delivers high-yield practice quizzes, identifies knowledge gaps, and calculates true mastery with precision.
        </div>
        <div class="timeline-wrapper">
            <span class="timeline-chip">1. Your Goal</span>
            <span class="timeline-arrow">→</span>
            <span class="timeline-chip">2. AI Study Plan</span>
            <span class="timeline-arrow">→</span>
            <span class="timeline-chip">3. Learn</span>
            <span class="timeline-arrow">→</span>
            <span class="timeline-chip">4. Practice</span>
            <span class="timeline-arrow">→</span>
            <span class="timeline-chip">5. 5-Q Quiz</span>
            <span class="timeline-arrow">→</span>
            <span class="timeline-chip">6. Python Scoring</span>
            <span class="timeline-arrow">→</span>
            <span class="timeline-chip">7. Next Step</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
        <div class="modern-card animate-fade-in">
            <h3 style="margin-top: 0; color: #1e1b4b; font-family: 'Outfit', sans-serif;">🎯 Intelligent, Goal-Driven Learning</h3>
            <p style="color: #475569; font-size: 1rem; line-height: 1.7;">
                Say goodbye to generic static tutorials. The <strong>AI Personalized Learning Coach</strong> crafts an adaptive educational journey custom-fit to your exact schedule and background:
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 18px 0;">
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px;">
                    <div style="font-size: 1.2rem; margin-bottom: 4px;">📅</div>
                    <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">Day-by-Day Roadmap</div>
                    <div style="font-size: 0.82rem; color: #64748b;">Structured objectives calibrated to your daily minutes.</div>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px;">
                    <div style="font-size: 1.2rem; margin-bottom: 4px;">🧠</div>
                    <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">Dynamic Quizzing</div>
                    <div style="font-size: 0.82rem; color: #64748b;">5 targeted multiple-choice questions for any topic.</div>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px;">
                    <div style="font-size: 1.2rem; margin-bottom: 4px;">⚡</div>
                    <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">Pure Python Scoring</div>
                    <div style="font-size: 0.82rem; color: #64748b;">Deterministic 0-100% calculation without AI hallucination.</div>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px;">
                    <div style="font-size: 1.2rem; margin-bottom: 4px;">🔍</div>
                    <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">Weak Topic Detection</div>
                    <div style="font-size: 0.82rem; color: #64748b;">Flags topics &lt; 70% as Needs Revision automatically.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cta_col1, cta_col2 = st.columns(2)
        with cta_col1:
            if st.button("🚀 Create My Learning Plan", type="primary", use_container_width=True):
                set_page("Learner Setup")
                st.rerun()
        with cta_col2:
            if st.session_state.current_learner_id:
                if st.button("📖 View Study Plan", use_container_width=True):
                    set_page("Study Plan")
                    st.rerun()

    with col2:
        st.markdown("""
        <div class="modern-card animate-fade-in" style="background: linear-gradient(180deg, #ffffff 0%, #fdfaff 100%);">
            <h4 style="margin-top: 0; color: #4338ca; font-size: 1.15rem; font-family: 'Outfit', sans-serif;">💡 How Your Workflow Works</h4>
            <div style="display: flex; flex-direction: column; gap: 14px; margin-top: 14px;">
                <div style="display: flex; gap: 12px; align-items: flex-start;">
                    <div style="background: #ede9fe; color: #6366f1; font-weight: 800; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.85rem;">1</div>
                    <div style="font-size: 0.92rem; color: #334155;"><strong>Setup Goals:</strong> Define your target subject, goal, knowledge level, and daily commitment.</div>
                </div>
                <div style="display: flex; gap: 12px; align-items: flex-start;">
                    <div style="background: #ede9fe; color: #6366f1; font-weight: 800; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.85rem;">2</div>
                    <div style="font-size: 0.92rem; color: #334155;"><strong>AI Curates Plan:</strong> Gemini drafts day-wise learning objectives and hands-on activities.</div>
                </div>
                <div style="display: flex; gap: 12px; align-items: flex-start;">
                    <div style="background: #ede9fe; color: #6366f1; font-weight: 800; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.85rem;">3</div>
                    <div style="font-size: 0.92rem; color: #334155;"><strong>Test Any Topic:</strong> Launch 5-question quizzes to validate comprehension.</div>
                </div>
                <div style="display: flex; gap: 12px; align-items: flex-start;">
                    <div style="background: #ede9fe; color: #6366f1; font-weight: 800; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.85rem;">4</div>
                    <div style="font-size: 0.92rem; color: #334155;"><strong>Adaptive Guidance:</strong> Receive targeted revision recommendations and build your learning streak!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# PAGE 2: LEARNER SETUP
# ==========================================

def render_learner_setup_page():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-family: 'Outfit', sans-serif; font-weight: 800; color: #1e1b4b; margin-bottom: 6px;">🎯 Create Your Learning Profile</h2>
        <div style="color: #64748b; font-size: 1.05rem;">Tell Gemini what you want to achieve, and receive a customized, day-by-day learning roadmap.</div>
    </div>
    """, unsafe_allow_html=True)

    current_learner = None
    if st.session_state.current_learner_id:
        current_learner = database.get_learner(st.session_state.current_learner_id)

    with st.form("learner_setup_form"):
        col1, col2 = st.columns(2)

        with col1:
            subject = st.text_input(
                "Subject / Skill to Master *",
                value=current_learner["subject"] if current_learner else "Python Programming",
                help="e.g. Python Programming, Machine Learning, FastAPI, SQL Data Modeling"
            )

            level_options = ["Beginner", "Intermediate", "Advanced"]
            current_level_idx = level_options.index(current_learner["level"]) if (current_learner and current_learner["level"] in level_options) else 0
            level = st.selectbox(
                "Current Knowledge Level *",
                level_options,
                index=current_level_idx,
                help="Calibrates curriculum depth and technical rigor."
            )

        with col2:
            goal = st.text_input(
                "Primary Learning Goal *",
                value=current_learner["goal"] if current_learner else "Build production-ready backend applications and APIs",
                help="What tangible capability do you want to accomplish?"
            )

            col2a, col2b = st.columns(2)
            with col2a:
                duration_days = st.number_input(
                    "Target Duration (Days) *",
                    min_value=1,
                    max_value=90,
                    value=current_learner["duration_days"] if current_learner else 7,
                    step=1,
                    help="Total number of days to complete the curriculum."
                )
            with col2b:
                daily_study_minutes = st.number_input(
                    "Daily Study Time (Minutes) *",
                    min_value=15,
                    max_value=360,
                    value=current_learner["daily_study_minutes"] if current_learner else 45,
                    step=15,
                    help="Realistic daily study commitment."
                )

        submit_btn = st.form_submit_button("✨ Generate Personalized Learning Plan", type="primary", use_container_width=True)

    if submit_btn:
        is_valid, err_msg = learning_plan.validate_learner_inputs(
            subject=subject,
            goal=goal,
            level=level,
            duration_days=duration_days,
            daily_study_minutes=daily_study_minutes
        )

        if not is_valid:
            st.error(f"⚠️ Validation Error: {err_msg}")
            return

        with st.spinner("Creating your personalized learning plan with Gemini AI..."):
            learner_id, plan_data, gen_err = learning_plan.create_and_store_learning_plan(
                subject=subject,
                goal=goal,
                level=level,
                duration_days=duration_days,
                daily_study_minutes=daily_study_minutes
            )

        if gen_err:
            st.error(f"❌ {gen_err}")
            st.info("Please verify your GEMINI_API_KEY in the `.env` file and try again.")
        else:
            st.session_state.current_learner_id = learner_id
            st.session_state.current_quiz = None
            st.session_state.quiz_result = None
            st.success("🎉 Your personalized study plan has been generated and saved!")
            set_page("Study Plan")
            st.rerun()


# ==========================================
# PAGE 3: STUDY PLAN
# ==========================================

def render_study_plan_page():
    if not st.session_state.current_learner_id:
        st.warning("⚠️ No active learning plan found.")
        if st.button("🚀 Create a Learning Plan Now", type="primary"):
            set_page("Learner Setup")
            st.rerun()
        return

    learner = database.get_learner(st.session_state.current_learner_id)
    plan_items = database.get_learning_plan(st.session_state.current_learner_id)

    if not plan_items:
        st.info("No study plan days found for this profile. Please generate a plan.")
        if st.button("Generate Plan"):
            set_page("Learner Setup")
            st.rerun()
        return

    # Header section with learner summary & regeneration modal
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.05em;">Curriculum Roadmap</div>
            <h2 style="font-family: 'Outfit', sans-serif; font-weight: 800; color: #1e1b4b; margin: 0 0 6px 0;">{learner['subject']}</h2>
            <div style="color: #64748b; font-size: 0.95rem;">
                <strong>Goal:</strong> {learner['goal']} &bull; 
                <span class="badge badge-in-progress" style="font-size: 0.75rem;">{learner['level']}</span> &bull; 
                <span>{learner['duration_days']} Days ({learner['daily_study_minutes']} mins/day)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with header_col2:
        with st.popover("🔄 Regenerate Plan", use_container_width=True):
            st.markdown("#### Adjust Plan Parameters")
            new_goal = st.text_input("Goal", value=learner["goal"], key="regen_goal")
            new_level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(learner["level"]), key="regen_lvl")
            new_days = st.number_input("Days", min_value=1, max_value=90, value=learner["duration_days"], key="regen_days")
            new_mins = st.number_input("Daily Minutes", min_value=15, max_value=360, value=learner["daily_study_minutes"], key="regen_mins")
            
            if st.button("Confirm Regeneration", type="primary", use_container_width=True):
                with st.spinner("Regenerating study plan with Gemini AI..."):
                    success, _, err = learning_plan.regenerate_learning_plan(
                        learner_id=learner["id"],
                        subject=learner["subject"],
                        goal=new_goal,
                        level=new_level,
                        duration_days=new_days,
                        daily_study_minutes=new_mins
                    )
                if success:
                    st.success("Plan regenerated successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to regenerate: {err}")

    st.markdown("---")

    # Display Day/Topic Cards
    for item in plan_items:
        day_num = item["day_number"]
        topic = item["topic"]
        objective = item["objective"]
        est_min = item["estimated_minutes"]
        activity = item["practice_activity"]
        status = item["status"]

        badge_cls = {
            "Completed": "badge-completed",
            "In Progress": "badge-in-progress",
            "Needs Revision": "badge-needs-revision",
            "Pending": "badge-pending"
        }.get(status, "badge-pending")

        with st.container():
            st.markdown(f"""
            <div class="modern-card animate-fade-in">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 0.95rem; color: #4f46e5; background: #eef2ff; border: 1px solid #c7d2fe; padding: 4px 12px; border-radius: 8px; letter-spacing: 0.05em;">DAY {day_num:02d}</span>
                        <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">⏱️ {est_min} mins</span>
                    </div>
                    <span class="badge {badge_cls}">{status}</span>
                </div>
                <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 1.35rem; color: #0f172a; font-family: 'Outfit', sans-serif;">{topic}</h3>
                
                <div style="background: #f8fafc; border-left: 4px solid #6366f1; padding: 12px 16px; border-radius: 0 10px 10px 0; margin-bottom: 12px;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Learning Objective</div>
                    <div style="color: #334155; font-size: 0.95rem; line-height: 1.5;">{objective}</div>
                </div>

                <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 12px 16px; border-radius: 0 10px 10px 0; margin-bottom: 14px;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Practice Activity</div>
                    <div style="color: #334155; font-size: 0.95rem; line-height: 1.5;">{activity}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            bcol1, bcol2, bcol3 = st.columns([2, 2, 4])
            with bcol1:
                if st.button(f"📝 Quiz on Topic", key=f"quiz_btn_{item['id']}"):
                    st.session_state.selected_quiz_topic = topic
                    set_page("Practice Quiz")
                    st.rerun()

            with bcol2:
                next_status = "Completed" if status != "Completed" else "Pending"
                btn_label = "Mark Completed" if status != "Completed" else "Mark Pending"
                if st.button(btn_label, key=f"status_toggle_{item['id']}"):
                    database.update_plan_status(item["id"], next_status)
                    database.update_topic_progress(
                        learner_id=learner["id"],
                        topic=topic,
                        score=5 if next_status == "Completed" else 0,
                        total_questions=5,
                        percentage=100.0 if next_status == "Completed" else 0.0
                    )
                    st.rerun()

            st.write("")


# ==========================================
# PAGE 4: PRACTICE QUIZ & RESULTS
# ==========================================

def render_practice_quiz_page():
    if not st.session_state.current_learner_id:
        st.warning("⚠️ Please create a learning plan before taking a quiz.")
        if st.button("🚀 Create Learning Plan"):
            set_page("Learner Setup")
            st.rerun()
        return

    learner = database.get_learner(st.session_state.current_learner_id)
    plan_items = database.get_learning_plan(st.session_state.current_learner_id)

    if not plan_items:
        st.info("No study plan topics found. Please generate a study plan first.")
        return

    topic_names = [item["topic"] for item in plan_items]

    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-family: 'Outfit', sans-serif; font-weight: 800; color: #1e1b4b; margin-bottom: 6px;">📝 Practice Quiz</h2>
        <div style="color: #64748b; font-size: 1rem;">Select any curriculum topic to generate a 5-question multiple choice knowledge check.</div>
    </div>
    """, unsafe_allow_html=True)

    top_col1, top_col2 = st.columns([3, 1])

    with top_col1:
        default_index = 0
        if st.session_state.selected_quiz_topic in topic_names:
            default_index = topic_names.index(st.session_state.selected_quiz_topic)

        selected_topic = st.selectbox(
            "Select Topic to Test",
            topic_names,
            index=default_index,
            key="quiz_topic_selector"
        )

    with top_col2:
        st.write("")
        st.write("")
        generate_clicked = st.button("✨ Generate Quiz", type="primary", use_container_width=True)

    # Handle Quiz Generation
    if generate_clicked:
        with st.spinner(f"Generating 5-question quiz for '{selected_topic}' with Gemini..."):
            quiz_id, questions, err = quiz_manager.create_topic_quiz(
                learner_id=learner["id"],
                subject=learner["subject"],
                topic=selected_topic,
                level=learner["level"]
            )

        if err:
            st.error(f"❌ {err}")
        else:
            st.session_state.current_quiz = {
                "quiz_id": quiz_id,
                "topic": selected_topic,
                "questions": questions
            }
            st.session_state.quiz_answers = {}
            st.session_state.quiz_result = None
            st.success("✅ Quiz generated successfully! Answer the 5 questions below.")

    st.markdown("---")

    # Render Current Quiz
    quiz_data = st.session_state.current_quiz
    if quiz_data and "questions" in quiz_data:
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e0e7ff; border-radius: 16px; padding: 18px 24px; margin-bottom: 22px; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.05);">
            <div style="font-size: 0.8rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.05em;">Current Assessment</div>
            <h3 style="font-family: 'Outfit', sans-serif; color: #1e1b4b; margin: 4px 0 0 0;">{quiz_data['topic']}</h3>
        </div>
        """, unsafe_allow_html=True)

        with st.form("quiz_submission_form"):
            user_choices = {}
            questions = quiz_data["questions"]

            for idx, q in enumerate(questions, 1):
                st.markdown(f"""
                <div class="modern-card" style="padding: 20px 24px; margin-bottom: 18px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 800; color: #6366f1; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;">Question {idx} of 5</span>
                    </div>
                    <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 14px; color: #0f172a; line-height: 1.4;">{q['question']}</div>
                </div>
                """, unsafe_allow_html=True)

                options = q.get("options", [])
                selected_opt = st.radio(
                    f"Select answer for Q{idx}:",
                    options,
                    index=None,
                    key=f"q_{idx}_{quiz_data['quiz_id']}",
                    label_visibility="collapsed"
                )
                user_choices[idx - 1] = selected_opt
                st.write("")

            submit_quiz_btn = st.form_submit_button("🚀 Submit Quiz for Scoring", type="primary", use_container_width=True)

        if submit_quiz_btn:
            unanswered = [i + 1 for i, ans in user_choices.items() if not ans]
            if unanswered:
                st.warning(f"⚠️ Please answer all questions before submitting. Unanswered: {', '.join(map(str, unanswered))}")
                return

            with st.spinner("Scoring answers with Python & preparing personalized coach feedback..."):
                result = quiz_manager.evaluate_quiz(
                    quiz_id=quiz_data["quiz_id"],
                    learner_id=learner["id"],
                    topic=quiz_data["topic"],
                    questions=questions,
                    user_answers=user_choices,
                    level=learner["level"]
                )
                st.session_state.quiz_result = result
                st.rerun()

    # RENDER QUIZ RESULTS
    if st.session_state.quiz_result:
        res = st.session_state.quiz_result
        st.markdown("## 📊 Quiz Results & Feedback")

        score_col1, score_col2, score_col3 = st.columns([1, 1, 2])
        with score_col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-icon">🎯</div>
                <div class="stat-value">{res['score']} / {res['total_questions']}</div>
                <div class="stat-label">Your Score</div>
            </div>
            """, unsafe_allow_html=True)

        with score_col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-icon">📈</div>
                <div class="stat-value">{res['percentage']}%</div>
                <div class="stat-label">Accuracy</div>
            </div>
            """, unsafe_allow_html=True)

        with score_col3:
            st.markdown(f"""
            <div class="stat-box" style="border-top: 4px solid {res['color']};">
                <div class="stat-icon">🏆</div>
                <div class="stat-value" style="color: {res['color']}; font-size: 1.8rem;">{res['category']}</div>
                <div class="stat-label">{res['summary_note']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="action-banner">
            <h4 style="margin: 0 0 6px 0; color: #3730a3; font-family: 'Outfit', sans-serif;">🎯 Recommended Next Step</h4>
            <p style="margin: 0; font-size: 1.05rem; color: #1e1b4b;">{res['recommended_action']}</p>
        </div>
        """, unsafe_allow_html=True)

        ai_fb = res.get("ai_feedback", {})
        if ai_fb:
            fb_col1, fb_col2 = st.columns(2)
            with fb_col1:
                st.markdown("""
                <div class="modern-card">
                    <h4 style="color: #047857; margin-top: 0; font-family: 'Outfit', sans-serif;">✨ What You Did Well</h4>
                """ + f"<p style='color: #334155; line-height: 1.6;'>{ai_fb.get('what_you_did_well', 'Good effort tackling this topic!')}</p></div>", unsafe_allow_html=True)

            with fb_col2:
                st.markdown("""
                <div class="modern-card">
                    <h4 style="color: #b45309; margin-top: 0; font-family: 'Outfit', sans-serif;">🔍 Areas to Practice</h4>
                """ + f"<p style='color: #334155; line-height: 1.6;'>{ai_fb.get('areas_to_improve', 'Focus on tricky edge cases.')}</p></div>", unsafe_allow_html=True)

        st.markdown("### 📝 Detailed Question Breakdown")
        for item in res["question_results"]:
            icon = "✅" if item["is_correct"] else "❌"
            status_text = "Correct" if item["is_correct"] else "Incorrect"

            with st.expander(f"{icon} Question {item['index']}: {status_text} (Selected: {item['selected_raw']})", expanded=not item["is_correct"]):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Your Choice:** `{item['selected_raw']}`")
                st.markdown(f"**Correct Answer Key:** `{item['correct_letter']}`")
                st.info(f"💡 **Explanation:** {item['explanation']}")

        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("🔄 Retake This Quiz", use_container_width=True):
                st.session_state.quiz_result = None
                st.rerun()

        with btn_col2:
            if st.button("📖 Return to Study Plan", use_container_width=True):
                set_page("Study Plan")
                st.rerun()

        with btn_col3:
            if st.button("📈 View Full Dashboard", type="primary", use_container_width=True):
                set_page("Progress Dashboard")
                st.rerun()


# ==========================================
# PAGE 5: PROGRESS DASHBOARD
# ==========================================

def render_progress_dashboard_page():
    if not st.session_state.current_learner_id:
        st.warning("⚠️ No active learner profile found. Create your learning plan to view progress.")
        if st.button("🚀 Get Started"):
            set_page("Learner Setup")
            st.rerun()
        return

    learner = database.get_learner(st.session_state.current_learner_id)
    metrics = database.get_dashboard_metrics(learner["id"])
    plan_items = database.get_learning_plan(learner["id"])
    history = database.get_quiz_attempts_history(learner["id"], limit=10)
    next_rec = learning_plan.get_next_recommended_topic(learner["id"])

    st.markdown(f"""
    <div style="margin-bottom: 22px;">
        <div style="font-size: 0.8rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.05em;">Performance Analytics</div>
        <h2 style="font-family: 'Outfit', sans-serif; font-weight: 800; color: #1e1b4b; margin: 0 0 6px 0;">{learner['subject']} Dashboard</h2>
        <div style="color: #64748b; font-size: 0.95rem;">Goal: {learner['goal']} &bull; Level: <span class="badge badge-in-progress" style="font-size: 0.75rem;">{learner['level']}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 1. Top Metric Cards with pastel accents
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="stat-box" style="border-bottom: 4px solid #6366f1;">
            <div class="stat-icon">📊</div>
            <div class="stat-value" style="color: #4f46e5;">{metrics['overall_progress_percentage']}%</div>
            <div class="stat-label">Progress</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="stat-box" style="border-bottom: 4px solid #10b981;">
            <div class="stat-icon">✅</div>
            <div class="stat-value" style="color: #059669;">{metrics['completed_topics']}/{metrics['total_topics']}</div>
            <div class="stat-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="stat-box" style="border-bottom: 4px solid #f59e0b;">
            <div class="stat-icon">🎯</div>
            <div class="stat-value" style="color: #d97706;">{metrics['average_quiz_score']}%</div>
            <div class="stat-label">Avg Quiz Score</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        rev_color = "#ef4444" if metrics['needs_revision_topics'] > 0 else "#10b981"
        st.markdown(f"""
        <div class="stat-box" style="border-bottom: 4px solid {rev_color};">
            <div class="stat-icon">⚠️</div>
            <div class="stat-value" style="color: {rev_color};">
                {metrics['needs_revision_topics']}
            </div>
            <div class="stat-label">Needs Revision</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class="stat-box" style="border-bottom: 4px solid #06b6d4;">
            <div class="stat-icon">🔥</div>
            <div class="stat-value" style="color: #0284c7;">{metrics['streak_days']}d</div>
            <div class="stat-label">Study Streak</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.progress(metrics['overall_progress_percentage'] / 100.0)

    # 2. Next Recommended Action Card
    rec_type = next_rec.get("type", "none")
    rec_border_color = "#ef4444" if rec_type == "revision" else "#6366f1"
    st.markdown(f"""
    <div class="modern-card" style="border-left: 6px solid {rec_border_color}; margin-top: 18px;">
        <h4 style="margin-top: 0; color: #1e1b4b; font-family: 'Outfit', sans-serif;">🎯 AI Coach Recommended Next Action</h4>
        <p style="font-size: 1.05rem; color: #334155; margin-bottom: 4px;">{next_rec['message']}</p>
    </div>
    """, unsafe_allow_html=True)

    dash_col1, dash_col2 = st.columns([1, 1])

    with dash_col1:
        st.markdown("### 📋 Topic Mastery Map")
        if plan_items:
            for item in plan_items:
                status = item["status"]
                topic_title = item["topic"]

                if status == "Completed":
                    icon = "✅"
                    badge_str = "<span class='badge badge-completed'>Completed</span>"
                elif status == "In Progress":
                    icon = "⏳"
                    badge_str = "<span class='badge badge-in-progress'>In Progress</span>"
                elif status == "Needs Revision":
                    icon = "⚠️"
                    badge_str = "<span class='badge badge-needs-revision'>Needs Revision</span>"
                else:
                    icon = "⚪"
                    badge_str = "<span class='badge badge-pending'>Pending</span>"

                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span>{icon}</span>
                        <div>
                            <span style="font-size: 0.75rem; font-weight: 700; color: #6366f1; text-transform: uppercase;">Day {item['day_number']:02d}</span>
                            <div style="font-weight: 600; color: #0f172a; font-size: 0.95rem;">{topic_title}</div>
                        </div>
                    </div>
                    <div>{badge_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No topics recorded yet.")

    with dash_col2:
        st.markdown("### 🕒 Recent Quiz Attempts")
        if history:
            history_rows = []
            for h in history:
                try:
                    dt = datetime.fromisoformat(h["attempted_at"]).strftime("%b %d, %H:%M")
                except Exception:
                    dt = h["attempted_at"]
                
                score_str = f"{h['score']}/{h['total_questions']} ({h['percentage']}%)"
                history_rows.append({
                    "Date": dt,
                    "Topic": h["topic"],
                    "Score": score_str,
                    "Result": "Pass" if h['percentage'] >= 70 else "Needs Practice"
                })

            st.dataframe(history_rows, use_container_width=True, hide_index=True)
        else:
            st.info("No quiz attempts recorded yet. Head over to **Practice Quiz** to test your knowledge!")

        if st.button("📝 Start a Practice Quiz Now", type="primary", use_container_width=True):
            set_page("Practice Quiz")
            st.rerun()


# ==========================================
# ROUTER DISPATCHER
# ==========================================

if st.session_state.navigation_page == "Home":
    render_home_page()
elif st.session_state.navigation_page == "Learner Setup":
    render_learner_setup_page()
elif st.session_state.navigation_page == "Study Plan":
    render_study_plan_page()
elif st.session_state.navigation_page == "Practice Quiz":
    render_practice_quiz_page()
elif st.session_state.navigation_page == "Progress Dashboard":
    render_progress_dashboard_page()
else:
    render_home_page()
