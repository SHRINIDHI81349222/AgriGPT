import pandas as pd

def run_market_researcher():
    insights = []
    df = pd.read_csv("data/market_researcher_dataset.csv")

    for _, row in df.iterrows():
        product = row["Product"]
        price = row["Market_Price_per_ton"]
        demand = row["Demand_Index"]
        supply = row["Supply_Index"]
        competitor_price = row["Competitor_Price_per_ton"]
        trend = row["Consumer_Trend_Index"]

        if demand > 70 and supply < 50:
            insights.append(f"📈 High demand and low supply for {product}. Market price ₹{price}/ton is favorable.")

        if competitor_price < price:
            insights.append(f"⚠️ {product} is priced above competitors (₹{price}/ton vs ₹{competitor_price}/ton). Re-evaluate pricing.")

        if trend > 75:
            insights.append(f"🌟 Strong positive consumer trend for {product}. Consider increasing market presence.")

    return insights
