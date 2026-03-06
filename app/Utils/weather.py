import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
CITY = os.getenv("WEATHER_CITY")

def detect_natural_disaster():
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={CITY}&appid={API_KEY}&units=metric"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

   
    if response.status_code != 200:
        return "No disaster"

  
    rainfall_1h = data.get("rain", {}).get("1h", 0)

  
    temperature = data.get("main", {}).get("temp", 0)

   
    daily_rainfall = rainfall_1h * 24

  
    if daily_rainfall >= 200:
        return "Flood"


    if daily_rainfall < 5 and temperature >= 32:
        return "Drought"

    return "No disaster"
