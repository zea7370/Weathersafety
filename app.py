from flask import Flask, render_template, request, jsonify
import requests
import sqlite3
import time

app = Flask(__name__)

# NOTE: You MUST fill this key for the app to work.
OPENWEATHER_KEY = "81b1bc3af77dbc7bfbe1cf94aec59198"


# -----------------------------
#  DATABASE SETUP
# -----------------------------
def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            city TEXT,
            temp REAL,
            safety TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# -----------------------------
#  WELCOME PAGE (NEW HOME) 🏡
# -----------------------------
@app.route("/")
def welcome():
    # This is the new landing page with the app description.
    return render_template("welcome.html")


# -----------------------------
#  SEARCH PAGE (FORM PAGE) 🔍
# -----------------------------
@app.route("/search")
def search_page():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    # Fetch the last 5 searches to display on the search page
    c.execute("SELECT city, temp, safety, timestamp FROM history ORDER BY rowid DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()

    # The original "index.html" is now used here
    return render_template("index.html", history=rows)


# -----------------------------
#  RESULTS PAGE (FORM SUBMIT)
# -----------------------------
@app.route("/results", methods=["POST"])
def results():
    city = request.form.get("city")

    if not city:
        # Redirect back to the search page if no city is provided
        return render_template("results.html", error="No city provided")

    # --- WEATHER API ---
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    res = requests.get(url).json()

    if "main" not in res:
        return render_template("results.html", error=f"City '{city}' not found or API error.")

    weather = {
        "city": city.title(),
        "temp": res["main"]["temp"],
        "desc": res["weather"][0]["description"],
        "lat": res["coord"]["lat"],
        "lon": res["coord"]["lon"]
    }

    # --- SAFETY LOGIC ---
    temp = weather["temp"]

    if temp < 10:
        safety = {
            "level": "Cold",
            "message": "Wear warm clothes, consider frostbite risk.",
            "hydration": "Low hydration needed, but monitor closely."
        }
    elif temp < 30:
        safety = {
            "level": "Moderate",
            "message": "Weather is pleasant. Enjoy outdoor activities.",
            "hydration": "Normal hydration recommended."
        }
    else:
        safety = {
            "level": "Hot",
            "message": "Avoid prolonged outdoor exposure. Seek shade.",
            "hydration": "Drink extra water! High risk of dehydration."
        }

    # --- AQI API ---
    lat, lon = weather["lat"], weather["lon"]
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
    aqi_res = requests.get(aqi_url).json()

    # Handle potential missing AQI data structure gracefully
    if "list" in aqi_res and len(aqi_res["list"]) > 0:
        aqi_data = aqi_res["list"][0]
        aqi = {
            "aqi": aqi_data["main"]["aqi"],
            "pm2_5": aqi_data["components"]["pm2_5"],
            "pm10": aqi_data["components"]["pm10"]
        }
    else:
        aqi = None

    # --- FORECAST API (7-DAY) ---
    # NOTE: OpenWeather's free 'forecast' API provides 5-day / 3-hour data.
    # To get 7 distinct days, we'll extract one entry per day (mid-day if possible).
    f_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    forecast_json = requests.get(f_url).json()

    forecast = []
    # Use a dictionary to store one entry per day
    daily_forecasts = {}
    if "list" in forecast_json:
        for entry in forecast_json["list"]:
            date_only = entry["dt_txt"].split(" ")[0]
            # Only record the first entry for each day to keep the list short and unique
            if date_only not in daily_forecasts:
                daily_forecasts[date_only] = {
                    "date": date_only,
                    "temp": round(entry["main"]["temp"]),
                    "humidity": entry["main"]["humidity"],
                    "description": entry["weather"][0]["main"]
                }

        # Convert the dictionary values back to a list, limit to 7 days
        forecast = list(daily_forecasts.values())[:7]

    # --- SAVE HISTORY ---
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("INSERT INTO history (city, temp, safety, timestamp) VALUES (?, ?, ?, ?)",
              (weather["city"], temp, safety["level"], time.ctime()))
    conn.commit()
    conn.close()

    return render_template(
        "results.html",
        weather=weather,
        safety=safety,
        aqi=aqi,
        forecast=forecast,
        openweather_key=OPENWEATHER_KEY
    )


# -----------------------------
# API ENDPOINT (OPTIONAL)
# -----------------------------
@app.route("/api_weather")
def api_weather():
    city = request.args.get("city")
    return jsonify({"msg": "API working", "city": city})


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)