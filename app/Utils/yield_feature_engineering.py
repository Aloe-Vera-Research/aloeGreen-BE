from datetime import datetime
from typing import Optional


def calculate_derived_features(data: dict) -> dict:
    data["water_stress_index"] = (
        data["soil_moisture_pct"] / (data["temp_day_c"] + 1)
    )
    data["heat_stress_index"] = (
        data["temp_day_c"] * data["humidity_pct"]
    )
    return data


def extract_time_features(timestamp: Optional[str] = None) -> dict:
    if timestamp is None:
        ts = datetime.now()
    else:
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            ts = datetime.now()

    return {
        "hour": ts.hour,
        "day": ts.day,
        "month": ts.month,
    }