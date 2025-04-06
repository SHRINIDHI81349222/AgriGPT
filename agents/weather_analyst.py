import pandas as pd

DATA_FOLDER = "data"

def run_weather_analyst():
    insights = []
    df = pd.read_csv(f"{DATA_FOLDER}/weather_data.csv")

    for _, row in df.iterrows():
        comment = ""
        
        # Rainfall-based comment
        if row['Rainfall_mm'] < 50:
            comment += "⚠️ Low rainfall may affect crop growth. "
        elif row['Rainfall_mm'] > 200:
            comment += "🌧️ Heavy rainfall might cause waterlogging. "

        # Temperature-based comment
        if row['Temperature_C'] > 35:
            comment += "🔥 High temperature could stress crops."
        elif row['Temperature_C'] < 15:
            comment += "❄️ Low temperature might delay germination."

        if comment:
            insight = (
                f"Region {row['Region']} ({row['Month']}): {comment.strip()} "
                f"(Rainfall: {row['Rainfall_mm']}mm, Temp: {row['Temperature_C']}°C)"
            )
            insights.append(insight)

    return insights
