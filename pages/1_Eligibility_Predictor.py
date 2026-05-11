"""
pages/1_Eligibility_Predictor.py — Predict campus-placement eligibility.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Eligibility Predictor",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .pred-card {
        background: linear-gradient(145deg, #1a1f2e 0%, #141820 100%);
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .pred-placed {
        border-color: #48bb78;
        box-shadow: 0 0 20px rgba(72,187,120,0.15);
    }
    .pred-not-placed {
        border-color: #fc8181;
        box-shadow: 0 0 20px rgba(252,129,129,0.15);
    }
    .pred-label {
        font-size: 2rem; font-weight: 800; margin-bottom: 0.3rem;
    }
    .pred-prob {
        font-size: 1.1rem; color: #a0aec0;
    }
    .section-header {
        font-size: 1.6rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
st.markdown('<p class="section-header">📊 Eligibility Predictor</p>', unsafe_allow_html=True)
st.markdown("Enter your academic profile to predict your campus-placement likelihood.")
st.markdown("---")

# ── Load model (auto-train if missing) ──────────────────
MODEL_PATH = "models/eligibility_model.pkl"
FEATURES_PATH = "models/feature_columns.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURES_PATH):
    st.warning("⚠️  Model files not found. Training model automatically …")
    with st.spinner("Generating dataset & training model …"):
        # Run training inline
        import sys
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from train_model import generate_dataset, train_model
        os.makedirs("data", exist_ok=True)
        df = generate_dataset(500)
        df.to_csv("data/placement_data.csv", index=False)
        train_model(df)
    st.success("✅  Model trained successfully!")

model = joblib.load(MODEL_PATH)
feature_cols = joblib.load(FEATURES_PATH)

# ── Input Form ───────────────────────────────────────────
col_form, col_result = st.columns([1, 1], gap="large")

with col_form:
    st.markdown("#### 📝  Student Profile")

    cgpa = st.slider("CGPA", min_value=5.0, max_value=10.0, value=7.5, step=0.1)
    backlogs = st.selectbox("Active Backlogs", options=list(range(6)), index=0)
    internships = st.selectbox("Number of Internships", options=list(range(4)), index=1)
    skills_count = st.slider("Skills Count", min_value=1, max_value=10, value=5)
    branch = st.selectbox("Branch", options=["CSE", "ECE", "MECH", "CIVIL"])

    predict_btn = st.button("🔮  Predict Eligibility", use_container_width=True, type="primary")

# ── Prediction ───────────────────────────────────────────
with col_result:
    if predict_btn:
        with st.spinner("Running prediction …"):
            # Build input DataFrame matching training features
            input_dict = {
                "cgpa": cgpa,
                "backlogs": backlogs,
                "internships": internships,
                "skills_count": skills_count,
                "branch_CSE": 1 if branch == "CSE" else 0,
                "branch_ECE": 1 if branch == "ECE" else 0,
                "branch_MECH": 1 if branch == "MECH" else 0,
                "branch_CIVIL": 1 if branch == "CIVIL" else 0,
            }
            input_df = pd.DataFrame([input_dict])

            # Ensure column order matches training
            for col in feature_cols:
                if col not in input_df.columns:
                    input_df[col] = 0
            input_df = input_df[feature_cols]

            prediction = model.predict(input_df)[0]
            probability = model.predict_proba(input_df)[0]

        # ── Display result card ──
        if prediction == 1:
            st.markdown(f"""
            <div class="pred-card pred-placed">
                <div class="pred-label" style="color:#48bb78;">✅ Likely to be Placed</div>
                <div class="pred-prob">Confidence: <b>{probability[1]*100:.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"Placement probability: **{probability[1]*100:.1f}%**")
        else:
            st.markdown(f"""
            <div class="pred-card pred-not-placed">
                <div class="pred-label" style="color:#fc8181;">❌ Unlikely to be Placed</div>
                <div class="pred-prob">Confidence: <b>{probability[0]*100:.1f}%</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.error(f"Non-placement probability: **{probability[0]*100:.1f}%**")

        # ── Probability breakdown ──
        st.markdown("#### 📈  Probability Breakdown")
        prob_df = pd.DataFrame({
            "Outcome": ["Not Placed", "Placed"],
            "Probability": [probability[0], probability[1]],
        })
        st.bar_chart(prob_df.set_index("Outcome"), color=["#667eea"])

        # ── Feature Importance ──
        st.markdown("#### 🏆  Feature Importance")
        importances = model.feature_importances_
        feat_imp_df = (
            pd.DataFrame({"Feature": feature_cols, "Importance": importances})
            .sort_values("Importance", ascending=True)
        )

        fig, ax = plt.subplots(figsize=(7, 4))
        sns.set_style("darkgrid")
        palette = sns.color_palette("viridis", len(feat_imp_df))
        ax.barh(feat_imp_df["Feature"], feat_imp_df["Importance"], color=palette)
        ax.set_xlabel("Importance")
        ax.set_title("Random Forest Feature Importance")
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")
        ax.tick_params(colors="#a0aec0")
        ax.xaxis.label.set_color("#a0aec0")
        ax.title.set_color("#e2e8f0")
        for spine in ax.spines.values():
            spine.set_color("#2d3748")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("👈  Fill in your profile on the left and click **Predict Eligibility**.")
