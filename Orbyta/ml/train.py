from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

DATA = Path(__file__).parent / "data" / "pcos_dataset.csv"
OUT = Path(__file__).parent.parent / "backend" / "models" / "pcos_model.joblib"

TARGET_COLUMN = "PCOS"
FEATURE_MAP = {
    "age": "age",
    "bmi": "bmi",
    "cycle_regular": "cycle_regular",
    "cycle_length": "cycle_length",
    "missed_periods": "missed_periods",
    "acne": "acne",
    "excess_hair": "excess_hair",
    "hair_thinning": "hair_thinning",
    "weight_change": "weight_change",
    "dark_skin": "dark_skin",
    "fatigue": "fatigue",
    "stress": "stress",
    "sleep": "sleep",
    "activity": "activity",
}

if not DATA.exists():
    raise SystemExit(
        "Put your chosen publicly available PCOS CSV at ml/data/pcos_dataset.csv "
        "and update TARGET_COLUMN/FEATURE_MAP to match its columns."
    )

df = pd.read_csv(DATA)
missing = [c for c in FEATURE_MAP.values() if c not in df.columns]
if TARGET_COLUMN not in df.columns or missing:
    raise SystemExit(f"Dataset columns do not match configuration. Missing: {missing}, target: {TARGET_COLUMN}")

X = df[list(FEATURE_MAP.values())].apply(pd.to_numeric, errors="coerce")
y = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")

mask = y.notna()
X, y = X[mask], y[mask].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

models = {
    "LogisticRegression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000))
    ]),
    "RandomForest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(n_estimators=300, random_state=42))
    ]),
    "GradientBoosting": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", GradientBoostingClassifier(random_state=42))
    ]),
}

best_name, best_model, best_f1 = None, None, -1
metrics = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    m = {
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }
    metrics[name] = m
    print(name, m)
    if m["f1"] > best_f1:
        best_name, best_model, best_f1 = name, model, m["f1"]

OUT.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(best_model, OUT)

print(f"\nBest model: {best_name}")
print(f"Saved: {OUT}")
print("IMPORTANT: Use the printed metrics in your presentation; never invent metrics.")
