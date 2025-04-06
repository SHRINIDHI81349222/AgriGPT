import sqlite3
from config.settings import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

sample_insights = [
    ("Sustainability Evaluator", "Frequent droughts detected in the Western region."),
    ("Sustainability Evaluator", "Flood-prone area found in the East due to high rainfall."),
    ("Sustainability Evaluator", "Crop rotation observed in North region fields."),
    ("Sustainability Evaluator", "No major sustainability issues in Central region.")
]

cursor.executemany("INSERT INTO memory (agent, insight) VALUES (?, ?)", sample_insights)
conn.commit()
conn.close()
print("🌱 Sample sustainability insights inserted.")
