import pandas as pd

def run_farmer_advisor():
    df = pd.read_csv("data/farmer_advisor_dataset.csv")
    insights = []

    for _, row in df.iterrows():
        farm_id = row['Farm_ID']
        crop = row['Crop_Type']
        pH = row['Soil_pH']
        moisture = row['Soil_Moisture']
        temp = row['Temperature_C']
        rain = row['Rainfall_mm']
        fert = row['Fertilizer_Usage_kg']
        pest = row['Pesticide_Usage_kg']

        if pH < 5.5:
            insights.append(f"Farm {farm_id} growing {crop} has low pH ({pH}). Consider adding lime.")
        if moisture < 30:
            insights.append(f"Farm {farm_id} has low soil moisture ({moisture}%). Recommend irrigation.")
        if temp > 35:
            insights.append(f"Farm {farm_id} is experiencing high temperature ({temp}°C).")
        if rain < 50:
            insights.append(f"Farm {farm_id} has low rainfall ({rain} mm).")
        if fert > 100:
            insights.append(f"Farm {farm_id} is using high fertilizer ({fert} kg). Consider optimizing usage.")
        if pest > 50:
            insights.append(f"Farm {farm_id} has high pesticide usage ({pest} kg). Recommend eco-friendly alternatives.")

    return insights
