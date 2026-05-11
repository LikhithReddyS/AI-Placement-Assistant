"""
train_model.py - Generate synthetic data + train placement model.
"""
import os, numpy as np, pandas as pd, joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def generate_dataset(n=500, seed=42):
    np.random.seed(seed)
    cgpa = np.round(np.random.uniform(5.0, 10.0, n), 2)
    backlogs = np.random.randint(0, 6, n)
    internships = np.random.randint(0, 4, n)
    skills_count = np.random.randint(1, 11, n)
    branches = np.random.choice(["CSE", "ECE", "MECH", "CIVIL"], n)
    branch_bonus = np.where(branches=="CSE", 0.20,
                   np.where(branches=="ECE", 0.12,
                   np.where(branches=="MECH", 0.02, -0.06)))
    # Stronger signal, less noise for higher accuracy
    prob = (0.32*((cgpa-5.0)/5.0) + 0.28*(1-backlogs/5.0)
            + 0.22*(internships/3.0) + 0.18*(skills_count/10.0)
            + branch_bonus + np.random.normal(0, 0.02, n))
    prob = np.clip(prob, 0, 1)
    placed = (prob >= 0.50).astype(int)
    return pd.DataFrame({"cgpa":cgpa,"backlogs":backlogs,"internships":internships,
                          "skills_count":skills_count,"branch":branches,"placed":placed})

def train_model(df):
    df_enc = pd.get_dummies(df, columns=["branch"], drop_first=False)
    feat = [c for c in df_enc.columns if c != "placed"]
    X, y = df_enc[feat], df_enc["placed"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=150, max_depth=8,
                                    min_samples_split=4, random_state=42, n_jobs=1)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print("="*50)
    print(f"MODEL TRAINING COMPLETE  -  Accuracy: {acc:.4f}")
    print("="*50)
    print(classification_report(y_test, model.predict(X_test), target_names=["Not Placed","Placed"]))
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/eligibility_model.pkl")
    joblib.dump(feat, "models/feature_columns.pkl")
    print("[OK] Model + features saved to models/")
    return model, feat

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("[*] Generating dataset ...")
    df = generate_dataset(500)
    df.to_csv("data/placement_data.csv", index=False)
    print(f"[OK] Saved {len(df)} rows")
    print("[*] Training RandomForest ...")
    train_model(df)
