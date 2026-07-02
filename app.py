from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Coordinates for some cities
cities = {
    "kolkata": (22.5726, 88.3639),
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "london": (51.5074, -0.1278),
    "newyork": (40.7128, -74.0060),
    "tokyo": (35.6762, 139.6503)
}

@app.route("/")
def home():
    return {
        "message": "Weather API is running!",
        "usage": "/weather/<city>",
        "example": "/weather/kolkata"
    }

@app.route("/weather/<city>")
def weather(city):
    city = city.lower()

    if city not in cities:
        return jsonify({
            "error": "City not found."
        }), 404

    lat, lon = cities[city]

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,"
        f"wind_speed_10m,weather_code"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Weather service unavailable"}), 500

    data = response.json()["current"]

    return jsonify({
        "city": city.title(),
        "temperature": f"{data['temperature_2m']} °C",
        "humidity": f"{data['relative_humidity_2m']} %",
        "wind_speed": f"{data['wind_speed_10m']} km/h",
        "weather_code": data["weather_code"]
    })

if __name__ == "__main__":
    app.run()
