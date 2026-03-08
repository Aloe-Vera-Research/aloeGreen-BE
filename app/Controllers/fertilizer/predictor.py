import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

clf = joblib.load(BASE_DIR / "MLModels" / "fertilizer" / "fertilizer_classifier.pkl")
reg = joblib.load(BASE_DIR / "MLModels" / "fertilizer" / "fertilizer_regressor.pkl")
pre = joblib.load(BASE_DIR / "MLModels" / "fertilizer" / "fertilizer_preprocessor.pkl")


def predict_fertilizer(data: dict):
    df = pd.DataFrame([data])
    X = pre.transform(df)

    fertilizer = clf.predict(X)[0]
    dosage = reg.predict(X)[0]

    return {
        "recommended_fertilizer": fertilizer,
        "recommended_dosage_g_per_plant": round(float(dosage), 2)
    }