from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# ==========================
# Configuration
# ==========================

API_KEY = os.getenv("API_KEY", "imon123")
DEFAULT_CITY = "Kolkata"

# ==========================
# Weather Code Mapping
# ==========================

weather_codes = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Heavy Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Rain Showers",
    81: "Heavy Rain Showers",
    95: "Thunderstorm"
}

# ==========================
# Home
# ==========================

@app.route("/")
def home():
    return jsonify({
        "name": "Imon Weather API",
        "version": "1.0",
        "default_city": DEFAULT_CITY,
        "usage": "/weather?apikey=YOUR_KEY",
        "example": "/weather?city=London&apikey=imon123"
    })

# ==========================
# Health
# ==========================

@app.route("/health")
def health():
    return jsonify({
        "status": "online"
    })

# ==========================
# Weather
# ==========================

@app.route("/weather")
def weather():

    key = request.args.get("apikey")

    if key != API_KEY:
        return jsonify({
            "success": False,
            "message": "Invalid API Key"
        }), 401

    city = request.args.get("city", DEFAULT_CITY)

    # Geocoding
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"

    geo = requests.get(geo_url).json()

    if "results" not in geo:
        return jsonify({
            "success": False,
            "message": "City not found."
        }), 404

    location = geo["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]
    timezone = location["timezone"]

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}"
        f"&longitude={longitude}"
        f"&current=temperature_2m,"
        f"relative_humidity_2m,"
        f"apparent_temperature,"
        f"weather_code,"
        f"wind_speed_10m,"
        f"wind_direction_10m,"
        f"cloud_cover,"
        f"pressure_msl,"
        f"is_day"
        f"&daily=sunrise,sunset,precipitation_probability_max"
        f"&timezone=auto"
    )

    weather = requests.get(weather_url).json()

    current = weather["current"]
    daily = weather["daily"]

    return jsonify({

        "success": True,

        "city": location["name"],

        "country": location.get("country", ""),

        "latitude": latitude,

        "longitude": longitude,

        "timezone": timezone,

        "temperature_c": current["temperature_2m"],

        "feels_like_c": current["apparent_temperature"],

        "humidity": current["relative_humidity_2m"],

        "pressure_hpa": current["pressure_msl"],

        "wind_speed_kmh": current["wind_speed_10m"],

        "wind_direction": current["wind_direction_10m"],

        "cloud_cover": current["cloud_cover"],

        "weather_code": current["weather_code"],

        "condition": weather_codes.get(
            current["weather_code"],
            "Unknown"
        ),

        "is_day": bool(current["is_day"]),

        "sunrise": daily["sunrise"][0],

        "sunset": daily["sunset"][0],

        "rain_probability": daily["precipitation_probability_max"][0]

    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
