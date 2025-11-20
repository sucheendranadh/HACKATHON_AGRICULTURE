"""
Unit tests for Smart Agriculture Planner
Run: pytest test_smart_planner.py -v
Or: python -m pytest test_smart_planner.py -v
"""

import pytest
import json
import os
import tempfile
from smart_planner import (
    analyze_soil_image_path,
    analyze_soil_from_params,
    select_crops,
    irrigation_plan_for_crop,
    cost_estimate,
    analyze_and_suggest
)


class TestSoilAnalysis:
    """Test soil analysis functions"""
    
    def test_analyze_soil_from_params_loam(self):
        """Test soil analysis with loam parameters"""
        soil = analyze_soil_from_params(
            soil_type="loam",
            texture="balanced",
            moisture_pct=20,
            pH=6.8
        )
        
        assert soil["soil_type"] == "loam"
        assert soil["texture"] == "balanced"
        assert soil["moisture_pct"] == 20.0
        assert soil["pH"] == 6.8
    
    def test_analyze_soil_from_params_sandy(self):
        """Test soil analysis with sandy parameters"""
        soil = analyze_soil_from_params(
            soil_type="sandy",
            moisture_pct=15,
            pH=7.0
        )
        
        assert soil["soil_type"] == "sandy"
        assert soil["texture"] == "coarse"  # auto-detect
        assert soil["moisture_pct"] == 15.0
        assert soil["pH"] == 7.0
    
    def test_analyze_soil_from_params_defaults(self):
        """Test soil analysis with minimal parameters"""
        soil = analyze_soil_from_params(soil_type="clay")
        
        assert soil["soil_type"] == "clay"
        assert soil["texture"] == "fine"
        assert isinstance(soil["moisture_pct"], float)
        assert isinstance(soil["pH"], float)
    
    def test_analyze_soil_from_params_invalid_type(self):
        """Test soil analysis with invalid soil type (should default)"""
        soil = analyze_soil_from_params(soil_type="invalid_type")
        
        assert soil["soil_type"] == "loam"  # should default to loam
    
    def test_analyze_soil_image_path(self):
        """Test soil analysis from image path"""
        soil = analyze_soil_image_path("path/to/soil_loam.jpg")
        
        assert soil["soil_type"] == "loam"
        assert "texture" in soil
        assert "moisture_pct" in soil
    
    def test_analyze_soil_image_path_sandy(self):
        """Test soil analysis from image path with sandy keyword"""
        soil = analyze_soil_image_path("samples/soil_sandy.jpg")
        
        assert soil["soil_type"] == "sandy"
        assert soil["texture"] == "coarse"


class TestCropSelection:
    """Test crop selection logic"""
    
    def test_select_crops_loam(self):
        """Test crop selection for loam soil"""
        crops = select_crops("loam", top_n=3)
        
        assert len(crops) <= 3
        assert len(crops) > 0
        assert all("crop" in c for c in crops)
        assert all("water_l_per_day_per_acre" in c for c in crops)
        assert all("cost_per_acre_usd" in c for c in crops)
    
    def test_select_crops_sandy(self):
        """Test crop selection for sandy soil"""
        crops = select_crops("sandy", top_n=2)
        
        assert len(crops) <= 2
        assert crops[0]["crop"] in ["Groundnut", "Sorghum"]
    
    def test_select_crops_ordered_by_water(self):
        """Test that crops are ordered by water usage (ascending)"""
        crops = select_crops("loam", top_n=5)
        
        # Verify ascending order of water usage
        for i in range(len(crops) - 1):
            assert crops[i]["water_l_per_day_per_acre"] <= crops[i+1]["water_l_per_day_per_acre"]


class TestIrrigationPlanning:
    """Test irrigation planning functions"""
    
    def test_irrigation_plan_low_water(self):
        """Test irrigation plan for low water crop"""
        crop = {"water_l_per_day_per_acre": 150, "crop": "Millet"}
        plan = irrigation_plan_for_crop(crop)
        
        assert plan["method"] == "drip"
        assert plan["recommended_daily_water_l"] == 150
        assert plan["meets_budget"] == True
    
    def test_irrigation_plan_medium_water(self):
        """Test irrigation plan for medium water crop"""
        crop = {"water_l_per_day_per_acre": 400, "crop": "Maize"}
        plan = irrigation_plan_for_crop(crop)
        
        assert plan["method"] == "sprinkler"
        assert plan["recommended_daily_water_l"] == 400
    
    def test_irrigation_plan_high_water(self):
        """Test irrigation plan for high water crop"""
        crop = {"water_l_per_day_per_acre": 1200, "crop": "Rice"}
        plan = irrigation_plan_for_crop(crop)
        
        assert plan["method"] == "flood"
        assert plan["recommended_daily_water_l"] == 1200
    
    def test_irrigation_plan_with_budget(self):
        """Test irrigation plan respects water budget"""
        crop = {"water_l_per_day_per_acre": 300, "crop": "Test"}
        
        # With sufficient budget
        plan1 = irrigation_plan_for_crop(crop, water_budget_l_per_day=400)
        assert plan1["meets_budget"] == True
        
        # With insufficient budget
        plan2 = irrigation_plan_for_crop(crop, water_budget_l_per_day=200)
        assert plan2["meets_budget"] == False


class TestCostEstimation:
    """Test cost estimation functions"""
    
    def test_cost_estimate_1_acre(self):
        """Test cost estimation for 1 acre"""
        crop = {"cost_per_acre_usd": 100}
        cost = cost_estimate(crop, area_acres=1.0)
        
        assert cost["area_acres"] == 1.0
        assert cost["estimated_total_cost_usd"] == 100.0
    
    def test_cost_estimate_2_acres(self):
        """Test cost estimation scales with area"""
        crop = {"cost_per_acre_usd": 100}
        cost = cost_estimate(crop, area_acres=2.0)
        
        assert cost["estimated_total_cost_usd"] == 200.0
    
    def test_cost_estimate_half_acre(self):
        """Test cost estimation for fractional acres"""
        crop = {"cost_per_acre_usd": 100}
        cost = cost_estimate(crop, area_acres=0.5)
        
        assert cost["estimated_total_cost_usd"] == 50.0


class TestFullWorkflow:
    """Test complete soil analysis workflow"""
    
    def test_analyze_and_suggest_params(self):
        """Test full workflow with manual parameters"""
        result = analyze_and_suggest(
            image_path=None,
            area_acres=1.0,
            water_budget=250
        )
        
        assert result["soil_analysis"]["soil_type"] is not None
        assert len(result["suggestions"]) > 0
        assert result["area_acres"] == 1.0
        assert result["water_budget_l_per_day"] == 250
        
        # Verify suggestion structure
        for sugg in result["suggestions"]:
            assert "crop" in sugg
            assert "irrigation" in sugg
            assert "cost" in sugg
            assert "soil_match" in sugg
    
    def test_analyze_and_suggest_with_image(self):
        """Test full workflow with image path"""
        result = analyze_and_suggest(
            image_path="samples/soil_clay.jpg",
            area_acres=1.0
        )
        
        assert result["soil_analysis"]["soil_type"] == "clay"
        assert len(result["suggestions"]) > 0
    
    def test_all_suggestions_have_water_data(self):
        """Test that all suggestions include water and cost data"""
        result = analyze_and_suggest(
            area_acres=2.0,
            water_budget=300
        )
        
        for sugg in result["suggestions"]:
            assert sugg["irrigation"]["recommended_daily_water_l"] > 0
            assert sugg["cost"]["estimated_total_cost_usd"] > 0
            assert sugg["cost"]["area_acres"] == 2.0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_zero_area_handling(self):
        """Test handling of very small areas"""
        result = analyze_and_suggest(area_acres=0.1)
        
        assert result["area_acres"] == 0.1
        for sugg in result["suggestions"]:
            assert sugg["cost"]["estimated_total_cost_usd"] > 0
    
    def test_large_area_handling(self):
        """Test handling of large areas"""
        result = analyze_and_suggest(area_acres=10.0)
        
        assert result["area_acres"] == 10.0
        for sugg in result["suggestions"]:
            assert sugg["cost"]["estimated_total_cost_usd"] > 0
    
    def test_high_water_budget(self):
        """Test with high water budget"""
        result = analyze_and_suggest(water_budget=5000)
        
        assert result["water_budget_l_per_day"] == 5000
        # All crops should meet budget
        for sugg in result["suggestions"]:
            assert sugg["irrigation"]["meets_budget"] == True
    
    def test_low_water_budget(self):
        """Test with very low water budget"""
        result = analyze_and_suggest(water_budget=100)
        
        # Some crops may exceed budget
        exceeds_count = sum(1 for s in result["suggestions"] if not s["irrigation"]["meets_budget"])
        assert exceeds_count > 0  # At least some should exceed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
