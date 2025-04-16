from utils.weather_utils import get_weather
import requests
import json
import pandas as pd

# Load datasets once
weather_df = pd.read_csv("data/weather_data.csv")
market_df = pd.read_csv("data/market_researcher_dataset.csv")
farmer_df = pd.read_csv("data/farmer_advisor_dataset.csv")

def run_agents(query, user_data=None):
    print("🔍 run_agents() received query:", query)

    if not user_data:
        return "❌ Missing user data."

    # Extract from user_data
    location = user_data.get("location", "your area")
    crop_type = user_data.get("crop_type", "your crop")
    farm_size = user_data.get("farm_size", "unknown size")

    # Real-time weather
    weather_live = get_weather(location)

    # Historical Weather
    weather_info = weather_df[weather_df["Region"].str.contains(location, case=False, na=False)]
    weather_summary = "⚠️ No historical weather data found.\n"
    if not weather_info.empty:
        row = weather_info.iloc[0]
        weather_summary = f"🌦️ Historical Weather:\n- Rainfall: {row['Rainfall']} mm\n- Temp: {row['Temperature']}°C\n- Month: {row['Month']}\n"

    # Market Info
    market_info = market_df[market_df["Product"].str.contains(crop_type, case=False, na=False)]
    market_summary = "⚠️ No market data found.\n"
    if not market_info.empty:
        row = market_info.iloc[0]
        market_summary = f"📈 Market Insights:\n- {crop_type.capitalize()} Price: ₹{row['Market_Price_per_ton']}/ton\n- Demand Index: {row['Demand_Index']}\n"

    # Sustainability Info
    sustainability_info = farmer_df[farmer_df["Crop_Type"].str.contains(crop_type, case=False, na=False)]
    sustainability_comment = "⚠️ Sustainability data unavailable.\n"
    if not sustainability_info.empty:
        row = sustainability_info.iloc[0]
        if row["Fertilizer_Usage_kg"] > 100:
            sustainability_comment = f"🌱 Sustainability Note:\n- High Fertilizer Usage: {row['Fertilizer_Usage_kg']} kg ⚠️\n- Tip: Consider reducing usage to preserve soil health.\n"
        else:
            sustainability_comment = f"🌱 Sustainability Note:\n- Fertilizer usage is within sustainable limits. ✅\n"

    # Smart Prompt
    full_context = (
        f"🧠 You are AgriGPT, a helpful agriculture AI.\n"
        f"Help the farmer in simple terms (English, India context).\n\n"
        f"Farmer Details:\n"
        f"- Location: {location}\n"
        f"- Crop: {crop_type}\n"
        f"- Land Size: {farm_size}\n\n"
        f"📡 Real-Time Weather:\n{weather_live}\n\n"
        f"{weather_summary}"
        f"{market_summary}"
        f"{sustainability_comment}\n"
        f"Question: '{query}'\n"
        f"You are AgriGPT, an intelligent agriculture assistant.\n\n"
        f"Farmer details:\n"
        f"- Location: {location}\n"
        f"- Crop: {crop_type}\n"
        f"- Land size: {farm_size}\n\n"
        f"📡 {weather_live}\n"
        f"CSV-based historical weather: {weather_summary}\n"
        f"Market trend: {market_summary}\n"
        f"Sustainability note: {sustainability_comment}\n\n"
        f"User asked: '{query}'\n\n"
        f"💡 Respond as a trusted agricultural expert. Give precise, step-by-step, and personalized guidance. "
        f"Do not suggest consulting others or external services. Give solutions based on data, even if incomplete. "
        f"Keep the response simple, direct, and in a friendly tone."

    )

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "gemma:2b",  # or "llama2", "mistral", etc.
                "messages": [
                    {"role": "system", "content": full_context},
                    {"role": "user", "content": query}
                ],
                "stream": False
            },
            timeout=60
        )

        data = response.json()
        reply = data.get("message", {}).get("content", "").strip()
        return format_response(reply)

    except Exception as e:
        return f"❌ Ollama error: {str(e)}"

def format_response(text):
    if not text:
        return "⚠️ No response from AgriGPT."
    return text.replace("\\n", "\n").replace("**", "").strip()
