"""Train the diabetes risk model.

The app trains the model automatically, but you can also run this file
on its own to see how well the model performs:

    python train_model.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Public dataset: 768 women of Pima Indian heritage, aged 21+, from the US
# National Institute of Diabetes and Digestive and Kidney Diseases.
DATA_URL = (
    "https://raw.githubusercontent.com/jbrownlee/Datasets/master/"
    "pima-indians-diabetes.data.csv"
)
DATA_FILE = Path(__file__).parent / "data" / "diabetes.csv"

COLUMNS = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin",
    "BMI", "DiabetesPedigreeFunction", "Age", "Outcome",
]

# Only use measurements a nurse can easily take at triage
FEATURES = ["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]


def load_data():
    """Read the dataset, downloading it the first time."""
    if not DATA_FILE.exists():
        print("Downloading the Pima Indians Diabetes dataset...")
        df = pd.read_csv(DATA_URL, header=None, names=COLUMNS)
        DATA_FILE.parent.mkdir(exist_ok=True)
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)


def train():
    """Train the model and return it together with its test results."""
    df = load_data()

    # In this dataset a 0 for glucose, blood pressure or BMI means
    # "not measured", so treat it as missing instead of a real value.
    for col in ["Glucose", "BloodPressure", "BMI"]:
        df[col] = df[col].replace(0, np.nan)

    X = df[FEATURES]
    y = df["Outcome"]  # 1 = developed diabetes, 0 = did not

    # Keep 20% of patients aside to test the model on data it has never seen
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("fill_missing", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("classify", LogisticRegression(max_iter=1000)),
    ])
    model.fit(X_train, y_train)

    risk = model.predict_proba(X_test)[:, 1]
    predicted = (risk >= 0.5).astype(int)
    metrics = {
        "accuracy": accuracy_score(y_test, predicted),
        "auc": roc_auc_score(y_test, risk),
        "sensitivity": recall_score(y_test, predicted),
        "precision": precision_score(y_test, predicted),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    return model, metrics


if __name__ == "__main__":
    _, results = train()
    print(f"Trained on {results['n_train']} patients, tested on {results['n_test']}")
    print(f"Accuracy:    {results['accuracy']:.0%}")
    print(f"AUC:         {results['auc']:.2f}")
    print(f"Sensitivity: {results['sensitivity']:.0%}  (diabetics correctly flagged)")
    print(f"Precision:   {results['precision']:.0%}  (flagged patients who really had diabetes)")