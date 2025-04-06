from agents.farmer_advisor import run_farmer_advisor
from agents.market_researcher import run_market_researcher
from agents.weather_analyst import run_weather_analyst
from agents.sustainability_evaluation import run_sustainability_evaluation
from report_generator import generate_report

if __name__ == "__main__":
    print("\n🌱 Running Agri-GPT Multi-Agent System...\n")

    print("👨‍🌾 Farmer Advisor Insights:")
    for insight in run_farmer_advisor():
        print(f" - {insight}")

    print("\n📊 Market Researcher Insights:")
    for insight in run_market_researcher():
        print(f" - {insight}")

    print("\n🌦️ Weather Analyst Insights:")
    for insight in run_weather_analyst():
        print(f" - {insight}")

    print("\n🌍 Sustainability Evaluation:")
    for insight in run_sustainability_evaluation():
        print(f" - {insight}")

    print(generate_report())
