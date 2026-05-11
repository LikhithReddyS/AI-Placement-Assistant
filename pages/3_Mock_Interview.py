"""
pages/3_Mock_Interview.py — AI-powered mock interview using Groq API.
Includes anti-cheating: fullscreen lock, tab-switch detection, copy/paste block.
"""
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import json, re

st.set_page_config(page_title="Mock Interview Bot", page_icon="🤖", layout="wide")

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
.section-header{font-size:1.6rem;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem}
.q-card{background:linear-gradient(145deg,#1a1f2e,#141820);border:1px solid #2d3748;border-radius:12px;padding:1.5rem;margin-bottom:1rem}
.q-number{font-size:.85rem;color:#667eea;font-weight:700;text-transform:uppercase}
.q-text{font-size:1.1rem;color:#e2e8f0;margin-top:.4rem}
.score-big{font-size:2.5rem;font-weight:800;text-align:center}
.final-card{background:linear-gradient(145deg,#1a1f2e,#141820);border:1px solid #667eea;border-radius:16px;padding:2rem;text-align:center;box-shadow:0 0 30px rgba(102,126,234,.12)}
</style>
""", unsafe_allow_html=True)

# ── Groq setup ───────────────────────────────────────────────
try:
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    GROQ_MODEL = "llama-3.3-70b-versatile"
except Exception as e:
    st.error(f"Could not configure Groq API: {e}")
    st.stop()

st.markdown('<p class="section-header">🤖 Mock Interview Bot</p>', unsafe_allow_html=True)
st.markdown("Practice role-specific interview questions with AI-powered evaluation.")
st.markdown("---")

# ── Session defaults ─────────────────────────────────────────
defaults = {
    "interview_started": False,
    "questions": [],
    "current_q": 0,
    "scores": [],
    "evaluations": [],
    "interview_complete": False,
    "tab_switches": 0,
    "answer_submitted": False,    # tracks if current question was answered
    "last_eval": None,            # stores last evaluation result
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

ROLES = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Analyst",
    "Data Scientist",
    "ML Engineer",
    "AI Engineer",
    "Data Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "Business Analyst",
    "Product Manager",
    "QA / Test Engineer",
    "Mobile App Developer",
    "Embedded Systems Engineer",
    "Database Administrator",
    "Network Engineer",
    "UI/UX Designer",
    "System Administrator",
    "Blockchain Developer",
    "Game Developer",
    "Technical Writer",
    "IT Support / Helpdesk",
]
role = st.selectbox("🎯 Select Target Role", ROLES, disabled=st.session_state.interview_started)


# ── AI helpers ───────────────────────────────────────────────
import random, time

# Topic pools per category to force diversity
_FOCUS_AREAS = {
    "Software Engineer": ["system design", "OOP principles", "algorithms", "databases", "concurrency", "testing", "API design", "design patterns", "microservices", "version control"],
    "Frontend Developer": ["React/Vue lifecycle", "CSS layout", "accessibility", "performance optimization", "state management", "browser APIs", "responsive design", "SEO", "web security", "build tools"],
    "Backend Developer": ["REST vs GraphQL", "database indexing", "caching strategies", "authentication", "message queues", "load balancing", "logging", "API versioning", "ORM patterns", "serverless"],
    "Full Stack Developer": ["deployment pipelines", "SSR vs CSR", "database migrations", "WebSockets", "API integration", "monolith vs microservices", "session management", "Docker", "CI/CD", "monitoring"],
    "Data Analyst": ["SQL window functions", "data visualization", "A/B testing", "ETL pipelines", "Excel pivot tables", "statistics", "data cleaning", "dashboard design", "KPI definition", "cohort analysis"],
    "Data Scientist": ["feature engineering", "model evaluation metrics", "bias/variance tradeoff", "NLP techniques", "time series", "dimensionality reduction", "Bayesian methods", "experiment design", "deep learning", "model deployment"],
    "ML Engineer": ["MLOps pipelines", "model serving", "hyperparameter tuning", "distributed training", "feature stores", "model monitoring", "transfer learning", "data augmentation", "A/B testing ML models", "edge deployment"],
    "AI Engineer": ["transformer architecture", "RAG systems", "prompt engineering", "fine-tuning LLMs", "vector databases", "reinforcement learning", "computer vision", "multi-modal AI", "AI ethics", "agentic systems"],
    "Data Engineer": ["Spark/Hadoop", "data warehousing", "schema design", "streaming vs batch", "data governance", "Airflow DAGs", "lake vs warehouse", "partitioning", "CDC patterns", "data quality"],
    "DevOps Engineer": ["CI/CD pipelines", "Kubernetes", "infrastructure as code", "monitoring/alerting", "container orchestration", "secrets management", "blue-green deployments", "incident response", "Terraform", "GitOps"],
    "Cloud Engineer": ["AWS/Azure/GCP services", "VPC networking", "auto-scaling", "cost optimization", "IAM policies", "serverless architecture", "disaster recovery", "multi-region", "cloud security", "migration strategies"],
    "Cybersecurity Analyst": ["OWASP top 10", "penetration testing", "SIEM tools", "incident response", "encryption protocols", "network forensics", "zero trust", "vulnerability assessment", "compliance frameworks", "threat modeling"],
    "Business Analyst": ["requirements gathering", "stakeholder management", "use case diagrams", "agile methodology", "gap analysis", "process mapping", "SWOT analysis", "data-driven decisions", "user stories", "feasibility study"],
    "Product Manager": ["roadmap prioritization", "user research", "OKRs/KPIs", "go-to-market strategy", "competitor analysis", "feature scoping", "cross-functional leadership", "MVP definition", "pricing strategy", "retention metrics"],
    "QA / Test Engineer": ["test automation", "regression testing", "API testing", "performance testing", "test case design", "BDD/TDD", "CI integration", "bug lifecycle", "load testing", "security testing"],
    "Mobile App Developer": ["iOS vs Android lifecycle", "state management", "push notifications", "offline storage", "app performance", "responsive layouts", "REST integration", "app store deployment", "cross-platform frameworks", "deep linking"],
    "Embedded Systems Engineer": ["RTOS concepts", "memory management", "interrupt handling", "I2C/SPI protocols", "firmware debugging", "power optimization", "bare-metal programming", "sensor integration", "bootloader design", "hardware-software co-design"],
    "Database Administrator": ["query optimization", "replication strategies", "backup/recovery", "normalization", "sharding", "stored procedures", "transaction isolation", "indexing strategies", "NoSQL vs SQL", "database security"],
    "Network Engineer": ["TCP/IP stack", "routing protocols", "firewall configuration", "DNS/DHCP", "VPN setup", "network troubleshooting", "QoS", "SDN concepts", "wireless networking", "network automation"],
    "UI/UX Designer": ["user research methods", "wireframing", "design systems", "usability testing", "information architecture", "accessibility standards", "interaction design", "prototyping tools", "color theory", "responsive design"],
    "Blockchain Developer": ["consensus mechanisms", "smart contracts", "DeFi protocols", "gas optimization", "token standards", "Layer 2 solutions", "wallet integration", "on-chain vs off-chain", "security audits", "DAO governance"],
    "Game Developer": ["game loop architecture", "physics engines", "shaders/rendering", "multiplayer networking", "AI pathfinding", "memory optimization", "asset pipelines", "level design tools", "input handling", "cross-platform builds"],
}


def gen_questions(r):
    # Pick 3 random focus areas to force topic diversity each session
    focus_pool = _FOCUS_AREAS.get(r, ["general concepts", "problem solving", "system design", "best practices", "real-world scenarios"])
    focus_picks = random.sample(focus_pool, min(3, len(focus_pool)))
    seed = random.randint(1000, 9999)

    prompt = (
        f"Generate exactly 5 unique technical interview questions for a {r} role. "
        f"Make sure to cover these topics: {', '.join(focus_picks)}. "
        f"The questions must be diverse — mix conceptual, scenario-based, and problem-solving types. "
        f"Do NOT repeat common/generic questions. Be creative and specific. "
        f"Session seed: {seed}. "
        f"Return ONLY a JSON array of 5 strings. No extra text."
    )
    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.95,
        top_p=0.95,
    )
    text = resp.choices[0].message.content.strip()
    m = re.search(r"\[.*\]", text, re.DOTALL)
    return json.loads(m.group()) if m else json.loads(text)


def eval_answer(q, a, r):
    prompt = f"""You are an expert interviewer for {r}. Question: {q}\nAnswer: {a}\nReturn ONLY JSON: {{"score":int 1-10,"good":"...","missing":"...","ideal_answer":"..."}}"""
    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = resp.choices[0].message.content.strip()
    t = re.sub(r"^```(?:json)?\s*", "", text)
    t = re.sub(r"\s*```$", "", t)
    m = re.search(r"\{.*\}", t, re.DOTALL)
    return json.loads(m.group()) if m else json.loads(t)


# ══════════════════════════════════════════════════════════════
#  ANTI-CHEAT JS — injected via components.html so it actually runs
# ══════════════════════════════════════════════════════════════
PROCTOR_JS = """
<script>
(function(){
    const parent = window.parent;
    const doc    = parent.document;

    /* ── Block copy / paste / cut on ALL textareas ── */
    function blockCopyPaste(){
        doc.querySelectorAll('textarea').forEach(function(ta){
            if(ta.dataset.proctored) return;
            ta.dataset.proctored = '1';
            ['copy','paste','cut','dragstart','drop'].forEach(function(evt){
                ta.addEventListener(evt, function(e){
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }, true);
            });
            ta.addEventListener('contextmenu', function(e){
                e.preventDefault();
                e.stopPropagation();
                return false;
            }, true);
            // Block keyboard shortcuts Ctrl+C, Ctrl+V, Ctrl+X
            ta.addEventListener('keydown', function(e){
                if((e.ctrlKey || e.metaKey) && ['c','v','x','a'].includes(e.key.toLowerCase())){
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }, true);
        });
    }

    /* ── Fullscreen helpers ── */
    function enterFS(){
        const el = doc.documentElement;
        const rfs = el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen;
        if(rfs) rfs.call(el).catch(function(){});
    }

    /* ── Create overlay in parent doc ── */
    function getOrCreateOverlay(){
        let ov = doc.getElementById('proctor-overlay');
        if(!ov){
            ov = doc.createElement('div');
            ov.id = 'proctor-overlay';
            ov.style.cssText = 'position:fixed;inset:0;z-index:999999;background:rgba(0,0,0,.94);display:none;flex-direction:column;align-items:center;justify-content:center;color:#fff;font-family:Inter,sans-serif;text-align:center;backdrop-filter:blur(12px);';
            ov.innerHTML = '<div style="font-size:4rem;margin-bottom:1rem">⚠️</div>'
                +'<div style="font-size:1.6rem;font-weight:700;color:#fc8181;margin-bottom:.5rem">Tab Switch / Fullscreen Exit Detected</div>'
                +'<div style="font-size:1rem;color:#cbd5e0;max-width:420px;line-height:1.6">Leaving fullscreen or switching tabs during the interview is not allowed.<br>Click below to return to fullscreen and continue.</div>'
                +'<button id="resume-fs-btn" style="margin-top:1.5rem;padding:.75rem 2.5rem;border:none;border-radius:8px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-size:1rem;font-weight:600;cursor:pointer;">↩ Resume Fullscreen</button>';
            doc.body.appendChild(ov);
            doc.getElementById('resume-fs-btn').addEventListener('click', function(){
                enterFS();
                ov.style.display='none';
            });
        }
        return ov;
    }

    /* ── Create badge ── */
    function getOrCreateBadge(){
        let b = doc.getElementById('tab-warn-badge');
        if(!b){
            b = doc.createElement('div');
            b.id = 'tab-warn-badge';
            b.style.cssText = 'position:fixed;top:12px;right:12px;z-index:999998;background:#742a2a;color:#feb2b2;padding:.45rem 1rem;border-radius:8px;font-size:.85rem;font-weight:600;display:none;box-shadow:0 4px 16px rgba(0,0,0,.4);';
            doc.body.appendChild(b);
        }
        return b;
    }

    let tabSwitchCount = parseInt(parent.__tabSwitchCount || '0');
    const ov = getOrCreateOverlay();
    const badge = getOrCreateBadge();

    function showOverlay(){
        ov.style.display = 'flex';
    }

    /* ── Fullscreen change ── */
    function onFSChange(){
        if(!parent.__proctorActive) return;
        const isFS = !!(doc.fullscreenElement || doc.webkitFullscreenElement);
        if(!isFS) showOverlay();
    }
    doc.removeEventListener('fullscreenchange', parent.__onFSChange);
    doc.removeEventListener('webkitfullscreenchange', parent.__onFSChange);
    parent.__onFSChange = onFSChange;
    doc.addEventListener('fullscreenchange', onFSChange);
    doc.addEventListener('webkitfullscreenchange', onFSChange);

    /* ── Tab switch ── */
    function onVisChange(){
        if(!parent.__proctorActive) return;
        if(doc.hidden){
            tabSwitchCount++;
            parent.__tabSwitchCount = tabSwitchCount;
            showOverlay();
            badge.textContent = '⚠ Tab switches: ' + tabSwitchCount;
            badge.style.display = 'block';
        }
    }
    function onBlur(){
        if(!parent.__proctorActive) return;
        tabSwitchCount++;
        parent.__tabSwitchCount = tabSwitchCount;
        showOverlay();
        badge.textContent = '⚠ Tab switches: ' + tabSwitchCount;
        badge.style.display = 'block';
    }
    doc.removeEventListener('visibilitychange', parent.__onVisChange);
    parent.removeEventListener('blur', parent.__onBlur);
    parent.__onVisChange = onVisChange;
    parent.__onBlur = onBlur;
    doc.addEventListener('visibilitychange', onVisChange);
    parent.addEventListener('blur', onBlur);

    /* ── MutationObserver to catch new textareas ── */
    if(parent.__proctorMO) parent.__proctorMO.disconnect();
    parent.__proctorMO = new MutationObserver(function(){ if(parent.__proctorActive) blockCopyPaste(); });
    parent.__proctorMO.observe(doc.body, {childList:true, subtree:true});

    /* ── Always block copy/paste when proctoring is on ── */
    if(parent.__proctorActive) blockCopyPaste();
})();
</script>
"""

START_PROCTOR_JS = """
<script>
(function(){
    const parent = window.parent;
    const doc = parent.document;
    parent.__proctorActive = true;
    parent.__tabSwitchCount = 0;
    // Enter fullscreen
    const el = doc.documentElement;
    const rfs = el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen;
    if(rfs) rfs.call(el).catch(function(){});
    // Block copy/paste on existing textareas
    doc.querySelectorAll('textarea').forEach(function(ta){
        if(ta.dataset.proctored) return;
        ta.dataset.proctored = '1';
        ['copy','paste','cut','dragstart','drop'].forEach(function(evt){
            ta.addEventListener(evt, function(e){ e.preventDefault(); e.stopPropagation(); return false; }, true);
        });
        ta.addEventListener('contextmenu', function(e){ e.preventDefault(); e.stopPropagation(); return false; }, true);
        ta.addEventListener('keydown', function(e){
            if((e.ctrlKey || e.metaKey) && ['c','v','x','a'].includes(e.key.toLowerCase())){
                e.preventDefault(); e.stopPropagation(); return false;
            }
        }, true);
    });
})();
</script>
"""

STOP_PROCTOR_JS = """
<script>
(function(){
    const parent = window.parent;
    const doc = parent.document;
    parent.__proctorActive = false;
    // Remove overlay
    const ov = doc.getElementById('proctor-overlay');
    if(ov) ov.style.display = 'none';
    // Exit fullscreen
    if(doc.fullscreenElement) doc.exitFullscreen().catch(function(){});
})();
</script>
"""


# ══════════════════════════════════════════════════════════════
#  INTERVIEW FLOW
# ══════════════════════════════════════════════════════════════

# ── Pre-interview: show rules & start button ─────────────────
if not st.session_state.interview_started and not st.session_state.interview_complete:
    st.info(
        "📋 **Interview Rules**\n"
        "- The browser will enter **fullscreen** when the interview starts.\n"
        "- **Tab switching** is monitored — each switch is recorded.\n"
        "- **Copy / Paste / Cut** are disabled in answer fields.\n"
        "- **Ctrl+C / Ctrl+V / Ctrl+X** keyboard shortcuts are blocked.\n"
        "- Right-click context menu is blocked.\n\n"
        "Click **Start Interview** when you are ready."
    )
    if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
        with st.spinner("Generating questions …"):
            try:
                st.session_state.questions = gen_questions(role)
                st.session_state.interview_started = True
                st.session_state.current_q = 0
                st.session_state.scores, st.session_state.evaluations = [], []
                st.session_state.interview_complete = False
                st.session_state.tab_switches = 0
                st.session_state.answer_submitted = False
                st.session_state.last_eval = None
                st.rerun()
            except Exception as e:
                st.error(f"Failed: {e}")

# ── Inject proctoring JS when interview is active ────────────
if st.session_state.interview_started and not st.session_state.interview_complete:
    # Main proctoring listeners (runs every rerender to re-attach)
    components.html(PROCTOR_JS, height=0, scrolling=False)
    # Trigger fullscreen + activate on first load
    components.html(START_PROCTOR_JS, height=0, scrolling=False)

# ── Question flow ────────────────────────────────────────────
if st.session_state.interview_started and not st.session_state.interview_complete:
    idx, total = st.session_state.current_q, len(st.session_state.questions)
    question = st.session_state.questions[idx]
    st.progress(idx / total, text=f"Question {idx+1} of {total}")
    st.markdown(
        f'<div class="q-card"><div class="q-number">Question {idx+1}/{total}</div>'
        f'<div class="q-text">{question}</div></div>',
        unsafe_allow_html=True,
    )

    # Show answer input only if not yet submitted for this question
    if not st.session_state.answer_submitted:
        answer = st.text_area("Your Answer", height=180, placeholder="Type your answer …", key=f"ans_{idx}")
        if st.button("📤 Submit Answer", use_container_width=True, type="primary"):
            if not answer.strip():
                st.warning("Please type an answer.")
            else:
                with st.spinner("Evaluating …"):
                    try:
                        ev = eval_answer(question, answer, role)
                    except Exception:
                        ev = {"score": 5, "good": "N/A", "missing": "N/A", "ideal_answer": "N/A"}
                score = int(ev.get("score", 5))
                st.session_state.scores.append(score)
                st.session_state.evaluations.append({"question": question, "answer": answer, **ev})
                st.session_state.last_eval = ev
                st.session_state.answer_submitted = True
                st.rerun()

    # Show evaluation & next/finish button AFTER submission
    if st.session_state.answer_submitted and st.session_state.last_eval:
        ev = st.session_state.last_eval
        score = int(ev.get("score", 5))
        sc_col = "#48bb78" if score >= 7 else "#ecc94b" if score >= 5 else "#fc8181"

        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f'<div class="score-big" style="color:{sc_col};">{score}/10</div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown(f"**✅ Good:** {ev.get('good','N/A')}")
            st.markdown(f"**❌ Missing:** {ev.get('missing','N/A')}")
        with st.expander("📖 Ideal Answer"):
            st.write(ev.get("ideal_answer", "N/A"))

        if idx + 1 < total:
            if st.button("➡️ Next Question", use_container_width=True):
                st.session_state.current_q += 1
                st.session_state.answer_submitted = False
                st.session_state.last_eval = None
                st.rerun()
        else:
            if st.button("🏁 Finish Interview", use_container_width=True, type="primary"):
                st.session_state.interview_complete = True
                st.session_state.interview_started = False
                st.session_state.answer_submitted = False
                st.session_state.last_eval = None
                st.rerun()

# ── Results ──────────────────────────────────────────────────
if st.session_state.interview_complete:
    # Stop proctoring & exit fullscreen
    components.html(STOP_PROCTOR_JS, height=0, scrolling=False)

    scores = st.session_state.scores
    avg = sum(scores) / len(scores) if scores else 0
    ac = "#48bb78" if avg >= 7 else "#ecc94b" if avg >= 5 else "#fc8181"
    st.markdown(
        f'<div class="final-card">'
        f'<div style="color:#a0aec0;margin-bottom:.5rem">OVERALL SCORE</div>'
        f'<div class="score-big" style="color:{ac};">{avg:.1f}/10</div>'
        f'<div style="color:#a0aec0;margin-top:.5rem">Based on {len(scores)} questions for <b>{role}</b></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Show tab-switch count in results
    tw = st.session_state.get("tab_switches", 0)
    if tw > 0:
        st.warning(f"⚠️ **Tab switches detected during interview: {tw}**")
    else:
        st.success("✅ No tab switches detected — great focus!")

    st.markdown("---")
    st.markdown("### 📋 Detailed Review")
    for i, ev in enumerate(st.session_state.evaluations):
        with st.expander(f"Q{i+1}: {ev['question']}"):
            st.markdown(f"**Your Answer:** {ev['answer']}")
            sc = ev.get("score", 0)
            sc_c = "#48bb78" if sc >= 7 else "#ecc94b" if sc >= 5 else "#fc8181"
            st.markdown(f"**Score:** <span style='color:{sc_c};font-weight:700'>{sc}/10</span>",
                        unsafe_allow_html=True)
            st.markdown(f"**✅ Good:** {ev.get('good','N/A')}")
            st.markdown(f"**❌ Missing:** {ev.get('missing','N/A')}")
            st.markdown(f"**📖 Ideal Answer:** {ev.get('ideal_answer','N/A')}")
    st.markdown("---")
    if st.button("🔄 Start New Interview", use_container_width=True, type="primary"):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()
