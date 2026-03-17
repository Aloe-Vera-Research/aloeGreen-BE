import joblib
import pandas as pd
from pathlib import Path

# Resolve the base directory dynamically to ensure model paths work across environments
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load pre-trained classification, regression, and preprocessing models
clf = joblib.load(BASE_DIR / "MLModels" / "fertilizer" / "fertilizer_classifier.pkl")
reg = joblib.load(BASE_DIR / "MLModels" / "fertilizer" / "fertilizer_regressor.pkl")
pre = joblib.load(BASE_DIR / "MLModels" / "fertilizer" / "fertilizer_preprocessor.pkl")


def predict_fertilizer(data: dict):
    # Convert incoming input dictionary into a DataFrame and apply the same preprocessing used during training
    df = pd.DataFrame([data])
    X = pre.transform(df)

    # Generate fertilizer type (classification) and dosage (regression) predictions
    fertilizer = clf.predict(X)[0]
    dosage = reg.predict(X)[0]

    return {
        "recommended_fertilizer": fertilizer,
        "recommended_dosage_g_per_plant": round(float(dosage), 2)
    }