import os
import random
import argparse
import json
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)


def analyze_soil_image_path(path):
    """Prototype soil analysis: infer soil type from filename or randomize."""
    basename = os.path.basename(path).lower()
    # Simple heuristics based on filename keywords
    if "clay" in basename:
        soil_type = "clay"
        texture = "fine"
    elif "sand" in basename:
        soil_type = "sandy"
        texture = "coarse"
    elif "loam" in basename:
        soil_type = "loam"
        texture = "balanced"
    else:
        soil_type = random.choice(["loam", "sandy", "clay", "silty"])
        texture = "inferred"

    moisture_pct = round(random.uniform(5, 35), 1)
    return {"soil_type": soil_type, "texture": texture, "moisture_pct": moisture_pct}


def analyze_soil_from_params(soil_type, texture=None, moisture_pct=None, pH=None):
    """Analyze soil based on manual input parameters instead of image."""
    # Normalize soil_type
    soil_type = soil_type.lower().strip()
    if soil_type not in ["loam", "sandy", "clay", "silty"]:
        soil_type = "loam"  # default
    
    # Fill in missing fields with defaults or random
    if texture is None:
        texture_map = {"loam": "balanced", "sandy": "coarse", "clay": "fine", "silty": "fine"}
        texture = texture_map.get(soil_type, "balanced")
    
    if moisture_pct is None:
        moisture_pct = round(random.uniform(5, 35), 1)
    else:
        moisture_pct = float(moisture_pct)
    
    if pH is None:
        pH = round(random.uniform(6.0, 7.5), 1)
    else:
        pH = float(pH)
    
    return {
        "soil_type": soil_type,
        "texture": texture,
        "moisture_pct": moisture_pct,
        "pH": pH
    }


_CROP_DB = {
    "loam": [
        {"crop": "Millet", "water_l_per_day_per_acre": 150, "cost_per_acre_usd": 80},
        {"crop": "Sorghum", "water_l_per_day_per_acre": 200, "cost_per_acre_usd": 100},
        {"crop": "Maize", "water_l_per_day_per_acre": 400, "cost_per_acre_usd": 150},
    ],
    "sandy": [
        {"crop": "Groundnut", "water_l_per_day_per_acre": 120, "cost_per_acre_usd": 90},
        {"crop": "Sorghum", "water_l_per_day_per_acre": 200, "cost_per_acre_usd": 100},
    ],
    "clay": [
        {"crop": "Rice", "water_l_per_day_per_acre": 1200, "cost_per_acre_usd": 300},
        {"crop": "Sugarcane", "water_l_per_day_per_acre": 900, "cost_per_acre_usd": 250},
    ],
    "silty": [
        {"crop": "Wheat", "water_l_per_day_per_acre": 220, "cost_per_acre_usd": 110},
        {"crop": "Barley", "water_l_per_day_per_acre": 180, "cost_per_acre_usd": 95},
    ],
}


def select_crops(soil_type, top_n=3):
    options = _CROP_DB.get(soil_type, [])
    # sort by water usage ascending to help meet low-water constraints first
    options_sorted = sorted(options, key=lambda x: x["water_l_per_day_per_acre"])
    return options_sorted[:top_n]


def irrigation_plan_for_crop(crop_info, water_budget_l_per_day=None):
    w = crop_info["water_l_per_day_per_acre"]
    method = "drip" if w <= 250 else "sprinkler" if w <= 600 else "flood"
    meets_budget = True if (water_budget_l_per_day is None or w <= water_budget_l_per_day) else False
    schedule = {
        "method": method,
        "recommended_daily_water_l": w,
        "meets_budget": meets_budget,
        "notes": "Drip irrigation recommended for low water usage crops. Adjust frequency by season."
    }
    return schedule


def cost_estimate(crop_info, area_acres=1.0):
    cost = crop_info.get("cost_per_acre_usd", 0) * area_acres
    return {"area_acres": area_acres, "estimated_total_cost_usd": cost}


def analyze_and_suggest(image_path=None, area_acres=1.0, water_budget=None):
    if image_path and os.path.exists(image_path):
        soil = analyze_soil_image_path(image_path)
    else:
        soil = analyze_soil_image_path(image_path or "placeholder.jpg")

    crops = select_crops(soil["soil_type"], top_n=5)
    suggestions = []
    for c in crops:
        plan = irrigation_plan_for_crop(c, water_budget)
        cost = cost_estimate(c, area_acres)
        suggestions.append({"crop": c["crop"], "soil_match": soil["soil_type"], "irrigation": plan, "cost": cost})

    return {"soil_analysis": soil, "area_acres": area_acres, "water_budget_l_per_day": water_budget, "suggestions": suggestions}


@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    # Accept file upload or JSON body
    water_budget = request.form.get('water_budget') or request.args.get('water_budget')
    area = float(request.form.get('area', request.args.get('area', 1.0)))
    if water_budget:
        try:
            water_budget = float(water_budget)
        except Exception:
            water_budget = None

    file = request.files.get('image')
    image_path = None
    if file:
        # Save temporarily
        save_path = os.path.join(".", "_tmp_upload.jpg")
        file.save(save_path)
        image_path = save_path

    result = analyze_and_suggest(image_path=image_path, area_acres=area, water_budget=water_budget)
    # cleanup
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except Exception:
            pass
    return jsonify(result)


def cli_main():
    parser = argparse.ArgumentParser(description='Smart Agriculture Planner (prototype)')
    parser.add_argument('--image', help='Path to soil image (optional)')
    parser.add_argument('--area', type=float, default=1.0, help='Area in acres (default 1)')
    parser.add_argument('--water_budget', type=float, help='Max water budget in L/day')
    parser.add_argument('--serve', action='store_true', help='Start API server')
    args = parser.parse_args()

    if args.serve:
        print('Starting Smart Planner API on http://127.0.0.1:5000')
        app.run()
        return

    result = analyze_and_suggest(image_path=args.image, area_acres=args.area, water_budget=args.water_budget)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    cli_main()
