"""Train the machine learning risk models used in the app.

The app trains the models automatically when it starts. You can also run
this file on its own to see how well each model performs:

    python train_model.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_DIR = Path(__file__).parent / "data"


# ---------------------------------------------------------------
# Shared steps used by every model
# ---------------------------------------------------------------

def load_csv(file_name, url, columns, na_values=None):
    """Read a dataset from the data folder, downloading it the first time."""
    path = DATA_DIR / file_name
    if not path.exists():
        print(f"Downloading {file_name}...")
        df = pd.read_csv(url, header=None, names=columns, na_values=na_values)
        DATA_DIR.mkdir(exist_ok=True)
        df.to_csv(path, index=False)
    return pd.read_csv(path)


def build_model(numeric, categorical=()):
    """Fill missing values, put numbers on the same scale, then
    fit a logistic regression (a simple, explainable ML model)."""
    parts = [(
        "num",
        Pipeline([
            ("fill_missing", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]),
        list(numeric),
    )]
    if categorical:
        # Categories (like chest pain type) become separate yes/no columns
        parts.append((
            "cat",
            Pipeline([
                ("fill_missing", SimpleImputer(strategy="most_frequent")),
                ("one_hot", OneHotEncoder(handle_unknown="ignore")),
            ]),
            list(categorical),
        ))
    return Pipeline([
        ("prepare", ColumnTransformer(parts)),
        ("classify", LogisticRegression(max_iter=1000)),
    ])


def fit_and_test(model, X, y):
    """Keep 20% of patients aside, train on the rest, and measure
    how well the model does on the patients it has never seen."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
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


def explain(model, patient):
    """How much each measurement pushed this patient's risk up (+) or down (-)."""
    prepare = model.named_steps["prepare"]
    values = prepare.transform(patient)
    if hasattr(values, "toarray"):
        values = values.toarray()
    weights = model.named_steps["classify"].coef_[0]
    names = prepare.get_feature_names_out()

    effects = {}
    for name, value, weight in zip(names, values[0], weights):
        _, column = name.split("__", 1)
        original = next(c for c in patient.columns if column == c or column.startswith(c + "_"))
        effects[original] = effects.get(original, 0) + value * weight
    return sorted(effects.items(), key=lambda item: abs(item[1]), reverse=True)


# ---------------------------------------------------------------
# Model 1: diabetes
# 768 women of Pima Indian heritage, aged 21+, USA (NIDDK)
# ---------------------------------------------------------------

DIABETES_FEATURES = ["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]


def train_diabetes():
    df = load_csv(
        "diabetes.csv",
        "https://raw.githubusercontent.com/jbrownlee/Datasets/master/"
        "pima-indians-diabetes.data.csv",
        ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin",
         "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"],
    )
    # A 0 for glucose, blood pressure or BMI means "not measured"
    for col in ["Glucose", "BloodPressure", "BMI"]:
        df[col] = df[col].replace(0, np.nan)

    model = build_model(numeric=DIABETES_FEATURES)
    return fit_and_test(model, df[DIABETES_FEATURES], df["Outcome"])


# ---------------------------------------------------------------
# Model 2: heart disease
# 303 patients referred for coronary angiography, Cleveland Clinic, USA (UCI)
# ---------------------------------------------------------------

HEART_NUMERIC = ["Age", "Sex", "RestingBP", "Cholesterol", "FastingBS", "ExerciseAngina"]
HEART_CATEGORICAL = ["ChestPain"]
HEART_FEATURES = HEART_NUMERIC + HEART_CATEGORICAL


def train_heart():
    df = load_csv(
        "heart.csv",
        "https://archive.ics.uci.edu/ml/machine-learning-databases/"
        "heart-disease/processed.cleveland.data",
        ["Age", "Sex", "ChestPain", "RestingBP", "Cholesterol", "FastingBS",
         "RestECG", "MaxHR", "ExerciseAngina", "Oldpeak", "Slope",
         "Vessels", "Thal", "Diagnosis"],
        na_values="?",
    )
    # Diagnosis 0 = no significant artery narrowing; 1-4 = heart disease
    y = (df["Diagnosis"] > 0).astype(int)

    model = build_model(numeric=HEART_NUMERIC, categorical=HEART_CATEGORICAL)
    return fit_and_test(model, df[HEART_FEATURES], y)


# ---------------------------------------------------------------

def _report(title, metrics):
    print(f"\n{title}")
    print(f"  Trained on {metrics['n_train']} patients, tested on {metrics['n_test']}")
    print(f"  Accuracy:    {metrics['accuracy']:.0%}")
    print(f"  AUC:         {metrics['auc']:.2f}")
    print(f"  Sensitivity: {metrics['sensitivity']:.0%}  (sick patients correctly flagged)")
    print(f"  Precision:   {metrics['precision']:.0%}  (flagged patients who really were sick)")


if __name__ == "__main__":
    _report("DIABETES MODEL", train_diabetes()[1])
    _report("HEART DISEASE MODEL", train_heart()[1])