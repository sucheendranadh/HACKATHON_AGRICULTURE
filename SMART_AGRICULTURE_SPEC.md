# Smart Agriculture Planner — Project Specification

## Project Overview

Smart Agriculture Planner is a modular system that helps smallholders decide what to plant, how to irrigate, and estimate costs for a 1-acre plot using a combination of soil analysis (via photos), simple agronomic rules, and external data (weather, location). The system is designed as an extensible prototype — core components are modular so a future ML model can replace heuristic logic.

## Bots / Components

- Soil Analysis Bot: Accepts a photo of soil or field and returns inferred soil texture/type and moisture estimate (prototype uses heuristics / filename cues; later replaced by ML). 
- Crop Selector Bot: Recommends suitable crops for a 1-acre plot based on soil analysis, expected water availability, and user constraints.
- Irrigation Planner Bot: Provides an irrigation method and schedule estimate and checks whether the plan meets water-usage constraints (bonus: ensure usage below 250 L/day when requested).
- Cost Estimator Bot: Produces a rough cost estimate for seeds, fertilizers, and irrigation for the given area and crop.

## Goals and Constraints

- Goal: Suggest crops appropriate for a 1-acre land parcel.
- Bonus constraint: Provide crop + irrigation plans that can operate below 250 L/day water usage when possible.

## Input Data

- Soil image (photo) OR manual soil descriptors (texture, pH, moisture)
- Plot area (default 1 acre)
- Optional: location (for weather lookup), water budget (L/day)

## Outputs

- Soil classification (example: loam, clay, sandy loam)
- Top N crop suggestions with estimated daily water usage per acre
- Irrigation recommendation (method and simple schedule)
- Estimated cost for the provided area

## Prototype Behaviour

This repository contains a lightweight prototype `smart_planner.py` that implements placeholder logic for each Bot. The prototype is intentionally simple and deterministic so you can run, test and replace components with ML models or external services later.

## Team

- Team Name: Bit By Bit
- Members (as provided):
  - Robart Gowthan Toy  (Reg: 2502155)
  - Gucheendranath E   (Reg: 2362176)
  - Jeel Inian F       (Reg: 2362090)
  - Leeni Immaculati B (Reg: 236210%)

## Next Steps (implementation roadmap)

1. Replace soil-image heuristic with an ML classifier trained on labelled soil texture photos.
2. Integrate weather API (by location) to refine irrigation plans and crop suitability.
3. Add a small frontend or mobile upload endpoint for field photo capture.
4. Replace heuristics with a trained crop-suggestion model using historical yield / water data.

## How to run prototype (quick)

1. Install dependencies: `pip install -r requirements.txt`
2. Start the API server: `python smart_planner.py --serve`
3. Or run the CLI: `python smart_planner.py --image path/to/soil.jpg --area 1`

The prototype returns JSON with soil analysis, crop suggestions, irrigation plan and cost estimate.
