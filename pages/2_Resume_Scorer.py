"""
pages/2_Resume_Scorer.py — Strict ATS Resume Scorer (0-100).
Supports PDF upload + paste for both Resume and JD.
Uses TF-IDF keyword matching + Groq AI for deep ATS analysis.
"""

import streamlit as st
import re, json, io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pdfplumber
from groq import Groq

# ── Page config ──────────────────────────────────────────
st.set_page_config(page_title="ATS Resume Scorer", page_icon="📝", layout="wide")

# ── Groq setup ───────────────────────────────────────────
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    GROQ_MODEL = "llama-3.3-70b-versatile"
    ai_available = True
except Exception:
    ai_available = False

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .section-header {
        font-size: 1.6rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .score-card {
        background: linear-gradient(145deg, #1a1f2e 0%, #141820 100%);
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .score-value { font-size: 3.5rem; font-weight: 800; }
    .score-label { font-size: 1.1rem; color: #a0aec0; margin-top: 0.3rem; }
    .kw-chip {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .kw-match { background: #22543d; color: #9ae6b4; }
    .kw-miss  { background: #742a2a; color: #feb2b2; }
    .metric-card {
        background: linear-gradient(145deg, #1a1f2e, #141820);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .metric-val { font-size: 1.8rem; font-weight: 800; }
    .metric-lbl { font-size: 0.78rem; color: #a0aec0; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .breakdown-bar {
        height: 8px; border-radius: 4px; margin-top: 4px;
        background: #2d3748; overflow: hidden;
    }
    .breakdown-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
st.markdown('<p class="section-header">📝 Strict ATS Resume Scorer</p>', unsafe_allow_html=True)
st.markdown("Upload or paste your **résumé** and a **job description** for a strict ATS compatibility score out of **100**.")
st.markdown("---")


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════

def extract_pdf_text(uploaded_file) -> str:
    """Extract text from an uploaded PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def clean_text(text: str) -> str:
    """Lowercase, strip special chars, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\#\.]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_keywords_tfidf(text: str, top_n: int = 50) -> list:
    """Extract top keywords from text using TF-IDF."""
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform([text])
    except ValueError:
        return []
    features = vectorizer.get_feature_names_out()
    scores = matrix.toarray().flatten()
    ranked = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)
    return [kw for kw, sc in ranked[:top_n] if sc > 0]


# ── Strict ATS scoring breakdown ─────────────────────────

# Common ATS section headers
ATS_SECTIONS = {
    "contact": r"(email|phone|mobile|contact|address|linkedin|github|portfolio)",
    "education": r"(education|academic|qualification|degree|university|college|school|gpa|cgpa)",
    "experience": r"(experience|employment|work\s*history|professional|internship|intern)",
    "skills": r"(skills|technical\s*skills|technologies|tools|competenc|proficienc)",
    "projects": r"(project|portfolio|capstone|thesis|dissertation)",
    "certifications": r"(certif|license|credential|course|training)",
    "summary": r"(summary|objective|profile|about\s*me|overview)",
}

# Action verbs ATS scanners look for
ACTION_VERBS = [
    "developed", "implemented", "designed", "built", "created", "managed",
    "led", "analyzed", "optimized", "improved", "increased", "reduced",
    "automated", "deployed", "maintained", "collaborated", "integrated",
    "architected", "engineered", "delivered", "executed", "established",
    "streamlined", "resolved", "configured", "monitored", "achieved",
    "spearheaded", "orchestrated", "facilitated", "mentored", "trained",
]

# Metrics / quantification patterns
METRICS_PATTERN = r"\d+[\%\+]|\$\d|revenue|growth|reduction|increased\s+by|reduced\s+by|improved\s+by|\d+\s*(users|clients|projects|team|members)"


def compute_strict_ats(resume_raw: str, jd_raw: str) -> dict:
    """Compute strict ATS score (0-100) with detailed breakdown."""
    resume_lower = resume_raw.lower()
    jd_lower = jd_raw.lower()
    resume_clean = clean_text(resume_raw)
    jd_clean = clean_text(jd_raw)

    breakdown = {}

    # ─────────────────────────────────────────────────────
    # 1. KEYWORD MATCH (35 points) — strictest component
    # ─────────────────────────────────────────────────────
    jd_keywords = extract_keywords_tfidf(jd_clean, top_n=40)
    resume_keywords_set = set(extract_keywords_tfidf(resume_clean, top_n=200))

    if jd_keywords:
        matched_kw = [kw for kw in jd_keywords if kw in resume_clean or kw in resume_keywords_set]
        missing_kw = [kw for kw in jd_keywords if kw not in matched_kw]
        kw_ratio = len(matched_kw) / len(jd_keywords)
    else:
        matched_kw, missing_kw = [], []
        kw_ratio = 0

    # Strict curve: penalize heavily below 60% match
    if kw_ratio >= 0.8:
        kw_score = 35
    elif kw_ratio >= 0.6:
        kw_score = 25 + (kw_ratio - 0.6) * 50  # 25-35
    elif kw_ratio >= 0.4:
        kw_score = 15 + (kw_ratio - 0.4) * 50  # 15-25
    elif kw_ratio >= 0.2:
        kw_score = 5 + (kw_ratio - 0.2) * 50   # 5-15
    else:
        kw_score = kw_ratio * 25                # 0-5

    breakdown["keyword_match"] = {"score": round(kw_score, 1), "max": 35,
                                   "matched": matched_kw[:15], "missing": missing_kw[:15],
                                   "ratio": round(kw_ratio * 100, 1)}

    # ─────────────────────────────────────────────────────
    # 2. TF-IDF COSINE SIMILARITY (20 points)
    # ─────────────────────────────────────────────────────
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([resume_clean, jd_clean])
        cosine_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        cosine_score = 0

    sim_score = min(cosine_score * 100, 20)  # cap at 20
    # Strict: apply power curve
    sim_score = (cosine_score ** 0.8) * 20
    sim_score = min(round(sim_score, 1), 20)

    breakdown["cosine_similarity"] = {"score": sim_score, "max": 20,
                                       "raw_cosine": round(cosine_score * 100, 1)}

    # ─────────────────────────────────────────────────────
    # 3. SECTION COMPLETENESS (15 points)
    # ─────────────────────────────────────────────────────
    found_sections = []
    missing_sections = []
    for section, pattern in ATS_SECTIONS.items():
        if re.search(pattern, resume_lower):
            found_sections.append(section)
        else:
            missing_sections.append(section)

    section_ratio = len(found_sections) / len(ATS_SECTIONS) if ATS_SECTIONS else 0
    section_score = round(section_ratio * 15, 1)

    breakdown["section_completeness"] = {"score": section_score, "max": 15,
                                          "found": found_sections, "missing": missing_sections}

    # ─────────────────────────────────────────────────────
    # 4. ACTION VERBS & IMPACT (10 points)
    # ─────────────────────────────────────────────────────
    verbs_found = [v for v in ACTION_VERBS if v in resume_lower]
    verb_count = len(verbs_found)
    # Need at least 8 different action verbs for full score
    verb_score = min(verb_count / 8, 1.0) * 6

    # Check for quantified achievements
    metrics_found = len(re.findall(METRICS_PATTERN, resume_lower))
    metric_score = min(metrics_found / 3, 1.0) * 4  # need at least 3 metrics

    action_total = round(verb_score + metric_score, 1)
    breakdown["action_impact"] = {"score": action_total, "max": 10,
                                   "verbs_found": verbs_found[:10],
                                   "verb_count": verb_count,
                                   "metrics_count": metrics_found}

    # ─────────────────────────────────────────────────────
    # 5. FORMATTING & LENGTH (10 points)
    # ─────────────────────────────────────────────────────
    word_count = len(resume_raw.split())
    line_count = len(resume_raw.strip().splitlines())

    # Ideal: 400-800 words (1-2 pages)
    if 400 <= word_count <= 800:
        length_score = 5
    elif 300 <= word_count <= 1000:
        length_score = 3
    elif 200 <= word_count <= 1200:
        length_score = 1.5
    else:
        length_score = 0

    # Check for email
    has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resume_raw))
    # Check for phone
    has_phone = bool(re.search(r"(\+?\d[\d\s\-]{7,}\d)", resume_raw))
    # Check for links (linkedin/github)
    has_links = bool(re.search(r"(linkedin\.com|github\.com|http|www\.)", resume_lower))

    contact_score = (has_email * 2) + (has_phone * 1.5) + (has_links * 1.5)
    format_total = round(min(length_score + contact_score, 10), 1)

    breakdown["formatting"] = {"score": format_total, "max": 10,
                                "word_count": word_count,
                                "has_email": has_email,
                                "has_phone": has_phone,
                                "has_links": has_links}

    # ─────────────────────────────────────────────────────
    # 6. RELEVANCE PENALTY (−10 points max)
    # ─────────────────────────────────────────────────────
    # Penalize for filler / irrelevant content
    filler_phrases = [
        "hard worker", "team player", "self motivated", "detail oriented",
        "think outside the box", "go getter", "synergy", "proactive",
        "passionate about everything", "responsible for"
    ]
    filler_count = sum(1 for f in filler_phrases if f in resume_lower)
    relevance_penalty = min(filler_count * 2, 10)

    breakdown["relevance_penalty"] = {"score": -relevance_penalty, "max": -10,
                                       "filler_count": filler_count}

    # ─────────────────────────────────────────────────────
    # TOTAL
    # ─────────────────────────────────────────────────────
    raw_total = kw_score + sim_score + section_score + action_total + format_total - relevance_penalty
    final_score = max(0, min(100, round(raw_total)))

    return {
        "final_score": final_score,
        "breakdown": breakdown,
        "matched_keywords": matched_kw[:15],
        "missing_keywords": missing_kw[:15],
    }


def get_ai_suggestions(resume_text: str, jd_text: str, ats_score: int) -> str:
    """Get AI-powered improvement suggestions from Groq."""
    if not ai_available:
        return ""
    prompt = f"""You are a strict ATS (Applicant Tracking System) expert. 
A candidate's resume scored {ats_score}/100 against the following job description.

JOB DESCRIPTION:
{jd_text[:2000]}

RESUME:
{resume_text[:3000]}

Provide exactly 5 specific, actionable improvements to increase the ATS score. Be harsh and direct.
For each suggestion, explain what to add/change and why it matters for ATS parsing.
Format as numbered list. Keep each point to 2-3 sentences max."""

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════
#  INPUT — PDF upload or paste
# ══════════════════════════════════════════════════════════

col_resume, col_jd = st.columns(2, gap="large")

with col_resume:
    st.markdown("#### 📄  Your Résumé")
    resume_upload = st.file_uploader("Upload Resume PDF", type=["pdf"], key="resume_pdf",
                                      help="Upload your resume as a PDF file")
    resume_text = st.text_area(
        "Or paste résumé text",
        height=250,
        placeholder="Paste your full résumé text here …",
        label_visibility="visible",
    )
    if resume_upload:
        with st.spinner("Extracting text from PDF …"):
            try:
                extracted = extract_pdf_text(resume_upload)
                if extracted:
                    resume_text = extracted
                    st.success(f"✅ Extracted {len(extracted.split())} words from PDF")
                else:
                    st.warning("⚠️ Could not extract text. The PDF may be image-based. Please paste text instead.")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

with col_jd:
    st.markdown("#### 💼  Job Description")
    jd_upload = st.file_uploader("Upload JD PDF", type=["pdf"], key="jd_pdf",
                                  help="Upload the job description as a PDF file")
    jd_text = st.text_area(
        "Or paste job description",
        height=250,
        placeholder="Paste the full job description here …",
        label_visibility="visible",
    )
    if jd_upload:
        with st.spinner("Extracting text from PDF …"):
            try:
                extracted = extract_pdf_text(jd_upload)
                if extracted:
                    jd_text = extracted
                    st.success(f"✅ Extracted {len(extracted.split())} words from PDF")
                else:
                    st.warning("⚠️ Could not extract text. Please paste text instead.")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

st.markdown("---")
analyse_btn = st.button("🔍  Run Strict ATS Analysis", use_container_width=True, type="primary")


# ══════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════

if analyse_btn:
    if not resume_text.strip() or not jd_text.strip():
        st.error("⚠️  Please provide both a résumé and a job description (upload PDF or paste text).")
    else:
        with st.spinner("Running strict ATS analysis …"):
            result = compute_strict_ats(resume_text, jd_text)

        score = result["final_score"]
        bd = result["breakdown"]

        # ── Score colour ──
        if score >= 80:
            color = "#48bb78"
            label = "ATS Ready ✅"
        elif score >= 60:
            color = "#68d391"
            label = "Good — Needs Minor Tweaks 🔧"
        elif score >= 40:
            color = "#ecc94b"
            label = "Moderate — Significant Gaps ⚡"
        elif score >= 20:
            color = "#f6ad55"
            label = "Weak — Major Rework Needed ⚠️"
        else:
            color = "#fc8181"
            label = "Poor — Unlikely to Pass ATS ❌"

        # ── Main Score Card ──
        st.markdown(f"""
        <div class="score-card" style="border-color:{color}; box-shadow: 0 0 30px {color}33;">
            <div class="score-value" style="color:{color};">{score}/100</div>
            <div class="score-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(score / 100)

        # ── Score Breakdown Metrics ──
        st.markdown("### 📊 Score Breakdown")
        m1, m2, m3, m4, m5 = st.columns(5)

        breakdown_items = [
            (m1, "Keyword Match", bd["keyword_match"]["score"], bd["keyword_match"]["max"], "#667eea"),
            (m2, "Similarity", bd["cosine_similarity"]["score"], bd["cosine_similarity"]["max"], "#764ba2"),
            (m3, "Sections", bd["section_completeness"]["score"], bd["section_completeness"]["max"], "#48bb78"),
            (m4, "Impact", bd["action_impact"]["score"], bd["action_impact"]["max"], "#ecc94b"),
            (m5, "Format", bd["formatting"]["score"], bd["formatting"]["max"], "#f6ad55"),
        ]

        for col, name, val, mx, clr in breakdown_items:
            pct = (val / mx * 100) if mx > 0 else 0
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val" style="color:{clr};">{val}/{mx}</div>
                    <div class="metric-lbl">{name}</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width:{pct}%;background:{clr};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Penalty
        penalty = bd["relevance_penalty"]["score"]
        if penalty < 0:
            st.error(f"📉 **Relevance Penalty: {penalty} pts** — Found {bd['relevance_penalty']['filler_count']} filler phrases (e.g. 'hard worker', 'team player'). Remove generic buzzwords.")

        st.markdown("---")

        # ── Keywords ──
        col_match, col_miss = st.columns(2, gap="large")

        with col_match:
            st.markdown("#### ✅  Matched Keywords")
            if result["matched_keywords"]:
                chips = "".join(
                    f'<span class="kw-chip kw-match">{kw}</span>' for kw in result["matched_keywords"]
                )
                st.markdown(chips, unsafe_allow_html=True)
                st.caption(f"Keyword match rate: **{bd['keyword_match']['ratio']}%**")
            else:
                st.error("No significant keyword overlap found.")

        with col_miss:
            st.markdown("#### ❌  Missing Critical Keywords")
            if result["missing_keywords"]:
                chips = "".join(
                    f'<span class="kw-chip kw-miss">{kw}</span>' for kw in result["missing_keywords"]
                )
                st.markdown(chips, unsafe_allow_html=True)
                st.caption("Add these keywords naturally into your résumé.")
            else:
                st.success("All critical keywords present!")

        st.markdown("---")

        # ── Detailed Breakdown ──
        with st.expander("📋 Section Analysis", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ Sections Found:**")
                for s in bd["section_completeness"]["found"]:
                    st.markdown(f"- ✔️ {s.title()}")
            with c2:
                st.markdown("**❌ Sections Missing:**")
                if bd["section_completeness"]["missing"]:
                    for s in bd["section_completeness"]["missing"]:
                        st.markdown(f"- ❌ {s.title()}")
                else:
                    st.markdown("All key sections present!")

        with st.expander("💪 Action Verbs & Impact"):
            st.markdown(f"**Action verbs found:** {bd['action_impact']['verb_count']}")
            if bd["action_impact"]["verbs_found"]:
                st.markdown(", ".join(f"`{v}`" for v in bd["action_impact"]["verbs_found"]))
            st.markdown(f"**Quantified achievements:** {bd['action_impact']['metrics_count']}")
            if bd["action_impact"]["metrics_count"] < 3:
                st.warning("Add more numbers! e.g. 'Increased performance by 40%', 'Managed team of 5'")

        with st.expander("📐 Formatting Details"):
            f = bd["formatting"]
            st.markdown(f"- **Word count:** {f['word_count']}  {'✅' if 400 <= f['word_count'] <= 800 else '⚠️ Aim for 400-800 words'}")
            st.markdown(f"- **Email detected:** {'✅' if f['has_email'] else '❌ Add your email!'}")
            st.markdown(f"- **Phone detected:** {'✅' if f['has_phone'] else '❌ Add your phone number!'}")
            st.markdown(f"- **Links detected:** {'✅' if f['has_links'] else '❌ Add LinkedIn/GitHub/Portfolio links!'}")

        st.markdown("---")

        # ── AI Suggestions ──
        if ai_available:
            st.markdown("### 🤖 AI-Powered Improvement Suggestions")
            with st.spinner("Generating strict ATS recommendations …"):
                suggestions = get_ai_suggestions(resume_text, jd_text, score)
            if suggestions:
                st.markdown(suggestions)
            else:
                st.info("Could not generate AI suggestions at this time.")
        else:
            st.info("Configure Groq API key for AI-powered suggestions.")
