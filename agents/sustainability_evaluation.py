import sqlite3
from config.settings import DB_PATH

def run_sustainability_evaluation():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    insights = []
    cursor.execute("SELECT insight FROM memory")
    all_insights = cursor.fetchall()

    for (insight,) in all_insights:
        if "drought" in insight.lower() or "flood" in insight.lower():
            insights.append(f"Sustainability Alert: {insight}")
        elif "crop rotation" in insight.lower():
            insights.append(f"Eco-friendly Practice: {insight}")
        elif "no major sustainability issues" in insight.lower():
            insights.append(f"✅ {insight}")

    conn.close()
    return insights
