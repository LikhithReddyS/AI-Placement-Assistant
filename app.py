"""
app.py — Homepage of the AI Placement Assistant.
"""

import streamlit as st

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="AI Placement Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    /* ---------- global ---------- */
    .main { background-color: #0e1117; }
    .block-container { padding-top: 2rem; }

    /* ---------- hero ---------- */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        font-size: 1.15rem;
        color: #a0aec0;
        text-align: center;
        margin-bottom: 2.5rem;
    }

    /* ---------- module cards ---------- */
    .module-card {
        background: linear-gradient(145deg, #1a1f2e 0%, #141820 100%);
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        height: 100%;
    }
    .module-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 28px rgba(102, 126, 234, 0.18);
    }
    .module-icon { font-size: 2.8rem; margin-bottom: 0.8rem; }
    .module-title {
        font-size: 1.35rem; font-weight: 700; color: #e2e8f0;
        margin-bottom: 0.6rem;
    }
    .module-desc { font-size: 0.95rem; color: #a0aec0; line-height: 1.55; }

    /* ---------- tech badge ---------- */
    .tech-badge {
        display: inline-block;
        background: #2d3748;
        color: #e2e8f0;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* ---------- divider ---------- */
    .section-divider {
        border: none;
        border-top: 1px solid #2d3748;
        margin: 2.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ─────────────────────────────────────────
st.markdown('<p class="hero-title">🎯 AI Placement Assistant</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Your all-in-one toolkit to ace campus placements — '
    'powered by Machine Learning &amp; Generative AI</p>',
    unsafe_allow_html=True,
)

# ── Module Cards ─────────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">📊</div>
        <div class="module-title">Eligibility Predictor</div>
        <div class="module-desc">
            Enter your academic profile — CGPA, backlogs, internships, skills &amp;
            branch — and instantly see whether you're likely to get placed, along
            with the probability and the most important factors driving the
            prediction.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">📝</div>
        <div class="module-title">Resume–JD Match Scorer</div>
        <div class="module-desc">
            Paste your résumé text and a job description side-by-side. The scorer
            computes a TF-IDF cosine-similarity match percentage, highlights the
            top matching keywords, and flags important terms you're missing.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="module-card">
        <div class="module-icon">🤖</div>
        <div class="module-title">Mock Interview Bot</div>
        <div class="module-desc">
            Choose a target role and face 5 AI-generated technical interview
            questions. After each answer the Gemini-powered evaluator scores you,
            highlights strengths &amp; gaps, and provides an ideal answer summary.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Divider ──────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── How to use ───────────────────────────────────────────
st.markdown("### 🚀  How to Use")
st.markdown(
    "Use the **sidebar** on the left to navigate between modules. "
    "Each page is self-contained — just fill in the inputs and click the action button."
)

# ── Tech Stack ───────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("### 🛠️  Tech Stack")

techs = [
    "Python 3.10+", "Streamlit", "scikit-learn", "Pandas",
    "NumPy", "Matplotlib", "Seaborn", "Google Gemini API",
    "TF-IDF / Cosine Similarity", "Random Forest",
]
badges_html = "".join(f'<span class="tech-badge">{t}</span>' for t in techs)
st.markdown(f"<div style='text-align:center;'>{badges_html}</div>", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#718096; font-size:0.85rem;'>"
    "Built with ❤️ using Streamlit &amp; Python  •  AI Placement Assistant v1.0"
    "</p>",
    unsafe_allow_html=True,
)
