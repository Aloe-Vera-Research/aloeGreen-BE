import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


TARGETS = ["temp_day_c", "humidity_pct", "rainfall_mm"]
LAGS = [1, 2, 3, 6, 12, 24, 48, 72]
WINDOWS = [6, 12, 24, 48]


class EnvironmentForecaster:
    def __init__(self):
        base_path = Path(__file__).resolve().parents[2]
        self.model_dir = base_path / "MLModels" / "weather_forecast"

        self.temp_model = joblib.load(self.model_dir / "env_temp_model.pkl")
        self.humidity_model = joblib.load(self.model_dir / "env_humidity_model.pkl")
        self.rain_model = joblib.load(self.model_dir / "env_rainfall_model.pkl")

        cfg_path = self.model_dir / "env_feature_columns.json"
        if cfg_path.exists():
            with open(cfg_path, "r") as f:
                self.feature_cols = json.load(f)
        else:
            self.feature_cols = None

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.month
        df["day"] = df["timestamp"].dt.day
        df["hour"] = df["timestamp"].dt.hour
        df["dayofweek"] = df["timestamp"].dt.dayofweek
        df["dayofyear"] = df["timestamp"].dt.dayofyear

        for col in TARGETS:
            for lag in LAGS:
                df[f"{col}_lag_{lag}"] = df[col].shift(lag)

        for col in TARGETS:
            for w in WINDOWS:
                df[f"{col}_rollmean_{w}"] = df[col].shift(1).rolling(w).mean()
                df[f"{col}_rollstd_{w}"] = df[col].shift(1).rolling(w).std()

        return df

    def forecast(self, history: list, hours_ahead: int = 24):
        working = pd.DataFrame(history).copy()
        working["timestamp"] = pd.to_datetime(working["timestamp"])
        working = working.sort_values("timestamp").reset_index(drop=True)

        if len(working) < 72:
            raise ValueError("At least 72 hourly history rows are required.")

        forecasts = []

        for _ in range(hours_ahead):
            next_ts = working["timestamp"].iloc[-1] + pd.Timedelta(hours=1)

            new_row = pd.DataFrame([{
                "timestamp": next_ts,
                "temp_day_c": np.nan,
                "humidity_pct": np.nan,
                "rainfall_mm": np.nan,
            }])

            working = pd.concat([working, new_row], ignore_index=True)

            feat_df = self.add_features(working)
            X_next = feat_df.iloc[[-1]].copy()

            if self.feature_cols is None:
                self.feature_cols = [
                    c for c in X_next.columns
                    if c not in ["timestamp", "temp_day_c", "humidity_pct", "rainfall_mm"]
                ]

            X_next = X_next[self.feature_cols]

            temp_next = float(self.temp_model.predict(X_next)[0])
            humidity_next = float(self.humidity_model.predict(X_next)[0])
            rain_next = float(self.rain_model.predict(X_next)[0])

            humidity_next = min(max(humidity_next, 0), 100)
            rain_next = max(0, rain_next)

            working.loc[working.index[-1], "temp_day_c"] = temp_next
            working.loc[working.index[-1], "humidity_pct"] = humidity_next
            working.loc[working.index[-1], "rainfall_mm"] = rain_next

            forecasts.append({
                "timestamp": next_ts.isoformat(),
                "temp_day_c": temp_next,
                "humidity_pct": humidity_next,
                "rainfall_mm": rain_next,
            })

        return forecasts

    def load_history_from_csv(self, csv_path: str, history_hours: int = 72):
        df = pd.read_csv(csv_path)
        df = df[["timestamp", "temp_day_c", "humidity_pct", "rainfall_mm"]].copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        if len(df) < history_hours:
            raise ValueError(f"CSV must contain at least {history_hours} rows.")

        history = df.tail(history_hours).copy()
        history["timestamp"] = history["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S")
        return history.to_dict(orient="records")

    def forecast_from_csv(self, csv_path: str, hours_ahead: int = 24, history_hours: int = 72):
        history = self.load_history_from_csv(csv_path, history_hours=history_hours)
        return self.forecast(history=history, hours_ahead=hours_ahead)