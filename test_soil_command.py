#!/usr/bin/env python
"""Quick test of the soil command flow"""
import json
import smart_planner

# Test the new soil analysis function
soil = smart_planner.analyze_soil_from_params(
    soil_type="loam",
    texture="balanced",
    moisture_pct=20,
    pH=6.8
)

print("Soil Analysis:")
print(json.dumps(soil, indent=2))

# Now get crop suggestions
crops = smart_planner.select_crops(soil["soil_type"], top_n=5)
suggestions = []
area = 1.0
water = 250

for c in crops:
    plan = smart_planner.irrigation_plan_for_crop(c, water)
    cost = smart_planner.cost_estimate(c, area)
    suggestions.append({"crop": c["crop"], "soil_match": soil["soil_type"], "irrigation": plan, "cost": cost})

result = {"soil_analysis": soil, "area_acres": area, "water_budget_l_per_day": water, "suggestions": suggestions}

print("\nFull Crop Suggestions:")
print(json.dumps(result, indent=2))
