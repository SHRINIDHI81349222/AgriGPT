def generate_report():
    from agents.farmer_advisor import run_farmer_advisor
    from agents.market_researcher import run_market_researcher
    from agents.weather_analyst import run_weather_analyst
    from agents.sustainability_evaluation import run_sustainability_evaluation

    # Collect all insights with their agent name
    entries = []

    for i in run_farmer_advisor():
        entries.append(("Farmer Advisor", i))

    for i in run_market_researcher():
        entries.append(("Market Researcher", i))

    for i in run_weather_analyst():
        entries.append(("Weather Analyst", i))

    for i in run_sustainability_evaluation():
        entries.append(("Sustainability Evaluator", i))

    # Build the report
    report = "\n📄 Consolidated Report:\n"
    report += "\n".join([f"[{agent}] {insight}" for agent, insight in entries])
    
    return report
