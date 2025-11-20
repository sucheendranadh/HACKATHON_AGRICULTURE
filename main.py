from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import json
import smart_planner


def run_chat_loop():
    try:
        model = OllamaLLM(model="llama3.2")
        template = """
You are an expert in agriculture and crop disease detection.

Here are some relevant agricultural data and observations: {observations}

Here is the question to answer: {question}
"""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | model
    except Exception as e:
        print("Warning: could not initialize Ollama LLM:", e)
        chain = None

    while True:
        print("\n\n-------------------------------")
        question = input("Ask your agriculture/crop disease question (type 'plan' for Smart Planner, 'soil' for soil analysis, 'q' to quit): ")
        print("\n\n")
        if question == "q":
            break

        if question.strip().lower() == "plan":
            img = input("Image path (or leave empty): ").strip()
            area = input("Area in acres (default 1): ").strip()
            area = float(area) if area else 1.0
            water = input("Water budget L/day (optional): ").strip()
            water = float(water) if water else None
            result = smart_planner.analyze_and_suggest(image_path=img if img else None, area_acres=area, water_budget=water)
            print(json.dumps(result, indent=2))
            continue

        if question.strip().lower() == "soil":
            print("\n--- Manual Soil Analysis ---")
            soil_type = input("Soil type (loam, sandy, clay, silty): ").strip() or "loam"
            texture = input("Texture (fine, balanced, coarse) [optional]: ").strip() or None
            moisture = input("Moisture % (optional, e.g., 15): ").strip() or None
            ph = input("pH (optional, e.g., 6.5): ").strip() or None
            area = input("Area in acres (default 1): ").strip()
            area = float(area) if area else 1.0
            water = input("Water budget L/day (optional): ").strip()
            water = float(water) if water else None
            
            soil = smart_planner.analyze_soil_from_params(
                soil_type=soil_type,
                texture=texture,
                moisture_pct=moisture,
                pH=ph
            )
            crops = smart_planner.select_crops(soil["soil_type"], top_n=5)
            suggestions = []
            for c in crops:
                plan = smart_planner.irrigation_plan_for_crop(c, water)
                cost = smart_planner.cost_estimate(c, area)
                suggestions.append({"crop": c["crop"], "soil_match": soil["soil_type"], "irrigation": plan, "cost": cost})
            
            result = {"soil_analysis": soil, "area_acres": area, "water_budget_l_per_day": water, "suggestions": suggestions}
            print(json.dumps(result, indent=2))
            continue

        if chain is None:
            print("Chat model not available. Try 'plan' or install/configure Ollama.")
            continue

        observations = retriever.invoke(question)
        result = chain.invoke({"observations": observations, "question": question})
        print(result)


if __name__ == '__main__':
    run_chat_loop()


