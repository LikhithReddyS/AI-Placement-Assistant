# 🎯 AI Placement Assistant

A production-ready, multi-module Streamlit web application that helps students prepare for campus placements using Machine Learning and Generative AI.

---

## 📦 Modules

### 1. 📊 Eligibility Predictor
Predicts whether a student is likely to be placed based on academic profile (CGPA, backlogs, internships, skills, branch) using a **Random Forest** classifier trained on 500 synthetic student records. Shows prediction confidence and feature importance.

### 2. 📝 Resume–JD Match Scorer
Compares a résumé against a job description using **TF-IDF vectorization** and **cosine similarity**. Displays a match percentage with a color-coded progress bar, top matching keywords, and missing important keywords from the JD.

### 3. 🤖 Mock Interview Bot
Generates 5 role-specific technical interview questions via the **Google Gemini API** (gemini-1.5-flash). After each answer the AI evaluates your response with a score, strengths, weaknesses, and an ideal answer summary. A final scorecard is shown at the end.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| scikit-learn | ML model & TF-IDF |
| Pandas / NumPy | Data processing |
| Matplotlib / Seaborn | Visualizations |
| Google Gemini API | Generative AI for interviews |
| Joblib | Model serialization |

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10 or higher
- A Google Gemini API key

### Steps

```bash
# 1. Clone / navigate to the project directory
cd ai-placement-assistant

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
#    Edit .streamlit/secrets.toml and replace the placeholder key
#    GEMINI_API_KEY = "your_key_here"

# 5. Train the ML model (one-time)
python train_model.py

# 6. Launch the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 📸 Screenshots

> _Screenshots will be added here after the first run._

---

## 📁 Project Structure

```
ai-placement-assistant/
├── app.py                          # Homepage
├── pages/
│   ├── 1_Eligibility_Predictor.py  # Module 1
│   ├── 2_Resume_Scorer.py          # Module 2
│   └── 3_Mock_Interview.py         # Module 3
├── models/                         # Auto-generated models
├── data/                           # Auto-generated dataset
├── .streamlit/
│   └── secrets.toml                # API keys
├── train_model.py                  # Data gen + model training
├── requirements.txt
└── README.md
```

---

## 👤 Author

Built with ❤️ as an AI-powered campus placement preparation toolkit.

---

## 📄 License

This project is open-source and available under the MIT License.
"# AI-Placement-Assistant" 
