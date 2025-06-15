import os
import openai
import pandas as pd
from utils.weather_utils import get_weather

# ✅ Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Load your datasets once
weather_df = pd.read_csv("data/weather_data.csv")
market_df = pd.read_csv("data/market_researcher_dataset.csv")
farmer_df = pd.read_csv("data/farmer_advisor_dataset.csv")

def run_agents(query, user_data=None):
    print("🔍 run_agents() received query:", query)

    if not user_data:
        return "❌ Missing user data."

    # ✅ Extract user profile
    location = user_data.get("location", "your area")
    crop_type = user_data.get("crop_type", "your crop")
    farm_size = user_data.get("land_size", "unknown size")
    language = user_data.get("language", "en")  # Ensure this is passed from app.py

    # ✅ Real-time weather
    weather_live = get_weather(location)

    # ✅ Historical Weather
    weather_info = weather_df[weather_df["Region"].str.contains(location, case=False, na=False)]
    weather_summary = "⚠️ No historical weather data found.\n"
    if not weather_info.empty:
        row = weather_info.iloc[0]
        weather_summary = f"- Rainfall: {row['Rainfall']} mm\n- Temp: {row['Temperature']}°C\n- Month: {row['Month']}"

    # ✅ Market Info
    market_info = market_df[market_df["Product"].str.contains(crop_type, case=False, na=False)]
    market_summary = "⚠️ No market data found.\n"
    if not market_info.empty:
        row = market_info.iloc[0]
        market_summary = f"- {crop_type.capitalize()} Price: ₹{row['Market_Price_per_ton']}/ton\n- Demand Index: {row['Demand_Index']}"

    # ✅ Sustainability Info
    sustainability_info = farmer_df[farmer_df["Crop_Type"].str.contains(crop_type, case=False, na=False)]
    sustainability_comment = "⚠️ Sustainability data unavailable.\n"
    if not sustainability_info.empty:
        row = sustainability_info.iloc[0]
        if row["Fertilizer_Usage_kg"] > 100:
            sustainability_comment = f"- High Fertilizer Usage: {row['Fertilizer_Usage_kg']} kg ⚠️\n- Tip: Reduce usage for soil health."
        else:
            sustainability_comment = "- Fertilizer usage is within sustainable limits ✅"

    # ✅ Prompt to OpenAI
    full_prompt = f"""
You are AgriGPT, a helpful agriculture AI built for Indian farmers.

📍 Farmer Info:
- Location: {location}
- Crop: {crop_type}
- Land Size: {farm_size} acres

📡 Live Weather:
{weather_live}

📖 Historical Weather:
{weather_summary}

📈 Market Trends:
{market_summary}

🌿 Sustainability:
{sustainability_comment}

🧑‍🌾 Question:
{query}

💡 Please give your response in {language.upper()}.
Respond in a friendly, clear, and step-by-step format that even a small farmer can understand. Avoid external suggestions. Be simple and practical.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"❌ OpenAI error: {str(e)}"
