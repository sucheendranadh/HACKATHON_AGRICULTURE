# Testing Guide

## Overview

The Smart Agriculture Planner has comprehensive unit and integration tests covering:
- **23 unit tests** for core business logic
- **10 integration tests** for the Flask web API

All tests pass successfully (33/33 ✅).

## Running Tests

### Run all tests:
```powershell
python -m pytest test_smart_planner.py test_web_app.py -v
```

### Run unit tests only:
```powershell
python -m pytest test_smart_planner.py -v
```

### Run web app integration tests only:
```powershell
python -m pytest test_web_app.py -v
```

### Run with coverage report:
```powershell
pip install pytest-cov
python -m pytest test_smart_planner.py test_web_app.py --cov=smart_planner --cov=web_app
```

## Test Coverage

### Unit Tests (`test_smart_planner.py`)

#### Soil Analysis Tests (6 tests)
- ✅ Manual soil parameter input (loam, sandy, clay, silty)
- ✅ Auto-detection of texture from soil type
- ✅ Default value handling
- ✅ Invalid soil type fallback
- ✅ Image path-based soil analysis
- ✅ Keyword detection in filenames

#### Crop Selection Tests (3 tests)
- ✅ Crop recommendations for different soil types
- ✅ Water usage sorting (ascending order)
- ✅ Top-N filtering

#### Irrigation Planning Tests (4 tests)
- ✅ Method selection (drip/sprinkler/flood) based on water usage
- ✅ Water budget constraint validation
- ✅ Budget met/exceeded indicators

#### Cost Estimation Tests (3 tests)
- ✅ Per-acre cost calculation
- ✅ Scaling with area
- ✅ Fractional acre support

#### Full Workflow Tests (3 tests)
- ✅ Complete analysis with manual parameters
- ✅ Complete analysis with image
- ✅ Data structure validation

#### Edge Case Tests (4 tests)
- ✅ Very small areas (0.1 acres)
- ✅ Large areas (10+ acres)
- ✅ High water budgets (all crops within budget)
- ✅ Low water budgets (some crops exceed budget)

### Integration Tests (`test_web_app.py`)

#### Web App Endpoints (2 tests)
- ✅ Web UI loads and renders
- ✅ Soil types API returns valid data

#### Analysis API Tests (5 tests)
- ✅ Analysis with all parameters
- ✅ Analysis with minimal parameters
- ✅ Image file upload
- ✅ Error handling for missing images
- ✅ Response structure validation

#### Error Handling Tests (3 tests)
- ✅ Invalid soil type defaults gracefully
- ✅ Non-numeric area values rejected
- ✅ Negative water budgets handled

## Sample Data

Sample soil images are generated in the `samples/` folder:

| File | Soil Type | Texture |
|------|-----------|---------|
| `soil_loam.jpg` | Loam | Balanced |
| `soil_sandy.jpg` | Sandy | Coarse |
| `soil_clay.jpg` | Clay | Fine |
| `soil_silty.jpg` | Silty | Fine |

These are used for integration tests and for manual testing the web UI.

## Creating Test Images

To regenerate sample images:
```powershell
python create_samples.py
```

## Test Scenarios

### Scenario 1: Loamy soil, 1 acre, 250 L/day budget
```python
result = analyze_and_suggest(
    image_path=None,
    area_acres=1.0,
    water_budget=250
)
# Expected: Millet and Sorghum recommended (within budget)
```

### Scenario 2: Clay soil, 2 acres, no water constraint
```python
result = analyze_and_suggest(
    image_path="samples/soil_clay.jpg",
    area_acres=2.0,
    water_budget=None
)
# Expected: Rice and Sugarcane recommended (high water needs, high cost)
```

### Scenario 3: Manual sandy soil entry
```python
soil = analyze_soil_from_params(
    soil_type="sandy",
    texture="coarse",
    moisture_pct=15,
    pH=7.0
)
crops = select_crops(soil["soil_type"], top_n=5)
# Expected: Groundnut (low water), Sorghum
```

## Continuous Integration

To add these tests to CI/CD:

```yaml
# Example GitHub Actions workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest test_smart_planner.py test_web_app.py --cov
```

## Future Test Enhancements

1. **ML Model Tests**: When integrating actual soil classifiers, add tests for model accuracy
2. **Weather API Tests**: Mock weather service calls and test weather-based recommendations
3. **Performance Tests**: Benchmark analysis speed with large datasets
4. **UI Tests**: Selenium/Playwright tests for web UI interactions
5. **Load Tests**: Test API under concurrent requests

## Troubleshooting

### Tests fail with module not found
```powershell
pip install -r requirements.txt
pip install pytest
```

### Image tests fail
Ensure sample images exist:
```powershell
python create_samples.py
```

### Flask app tests error
Make sure Flask is installed:
```powershell
pip install Flask
```

## Test Statistics

- **Total Tests**: 33
- **Passing**: 33 ✅
- **Failing**: 0
- **Skipped**: 0
- **Coverage**: Core business logic fully tested
- **Execution Time**: ~0.5 seconds
