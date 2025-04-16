import requests

# 🔑 Paste your OpenWeatherMap API key below
API_KEY = "11a5fa45490383b26d07bd3a580ad204"

def get_weather(location):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("cod") != 200:
            return f"⚠️ Unable to fetch real-time weather for {location}."

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        return f"📍 Real-time weather in {location}: {desc}, {temp}°C, Humidity: {humidity}%, Wind: {wind} m/s"

    except Exception as e:
        return f"⚠️ Weather fetch failed: {str(e)}"
