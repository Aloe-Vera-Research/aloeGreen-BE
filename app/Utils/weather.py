import requests

def detect_natural_disaster(lat: float, lon: float):

    try:

        # WEATHER API
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation&hourly=precipitation&forecast_days=1"

        response = requests.get(weather_url, timeout=10)
        weather_data = response.json()

        current = weather_data.get("current", {})

        temperature = current.get("temperature_2m", 0)
        current_precipitation = current.get("precipitation", 0)

        hourly = weather_data.get("hourly", {}).get("precipitation", [])

        if len(hourly) >= 24:
            daily_rainfall = sum(hourly[:24])
        else:
            daily_rainfall = current_precipitation * 24

        # DISASTER LOGIC
        if daily_rainfall >= 200:
            disaster = "Flood"
            advice = "Improve drainage and avoid harvesting"

        elif daily_rainfall < 5 and temperature >= 32:
            disaster = "Drought"
            advice = "Increase irrigation"

        else:
            disaster = "No disaster"
            advice = "Normal farming conditions"

        # LOCATION NAME USING REVERSE GEOCODING
        geo_url = f"https://geocoding-api.open-meteo.com/v1/reverse?latitude={lat}&longitude={lon}&language=en"

        geo_response = requests.get(geo_url, timeout=10)
        geo_data = geo_response.json()

        location_name = "Unknown"

        if "results" in geo_data and len(geo_data["results"]) > 0:
            place = geo_data["results"][0]
            city = place.get("name", "")
            country = place.get("country", "")
            location_name = f"{city}, {country}"

        return {
            "disaster": disaster,
            "advice": advice,
            "location": f"{lat:.4f}, {lon:.4f}",
            "locationName": location_name
        }

    except Exception as e:

        print("Weather API error:", e)

        return {
            "disaster": "Unknown",
            "advice": "Weather service unavailable",
            "location": f"{lat:.4f}, {lon:.4f}",
            "locationName": "Unknown"
        }