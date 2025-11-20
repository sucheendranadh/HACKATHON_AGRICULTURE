"""
Flask Web UI for Smart Agriculture Planner
Run: python web_app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify
import json
import smart_planner
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Ensure templates folder exists
os.makedirs('templates', exist_ok=True)


@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint for soil analysis and crop suggestions"""
    try:
        mode = request.form.get('mode', 'params')  # 'params' or 'image'
        
        if mode == 'image':
            # Image-based analysis
            if 'image' not in request.files:
                return jsonify({"error": "No image provided", "success": False}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected", "success": False}), 400
            
            # Save temporarily
            save_path = os.path.join(".", "_tmp_upload.jpg")
            file.save(save_path)
            image_path = save_path
        else:
            image_path = None
        
        # Get other parameters
        area = float(request.form.get('area', 1.0))
        water_budget = request.form.get('water_budget')
        
        if water_budget:
            try:
                water_budget = float(water_budget)
            except:
                water_budget = None
        
        if mode == 'params':
            # Manual soil parameters
            soil_type = request.form.get('soil_type', 'loam').strip()
            texture = request.form.get('texture', '').strip() or None
            moisture = request.form.get('moisture', '').strip() or None
            ph = request.form.get('pH', '').strip() or None
            
            soil = smart_planner.analyze_soil_from_params(
                soil_type=soil_type,
                texture=texture,
                moisture_pct=moisture,
                pH=ph
            )
        else:
            # Image-based analysis
            soil = smart_planner.analyze_soil_image_path(image_path)
            # Cleanup
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except:
                    pass
        
        # Get crop suggestions
        crops = smart_planner.select_crops(soil["soil_type"], top_n=5)
        suggestions = []
        
        for c in crops:
            plan = smart_planner.irrigation_plan_for_crop(c, water_budget)
            cost = smart_planner.cost_estimate(c, area)
            suggestions.append({
                "crop": c["crop"],
                "soil_match": soil["soil_type"],
                "irrigation": plan,
                "cost": cost
            })
        
        result = {
            "success": True,
            "soil_analysis": soil,
            "area_acres": area,
            "water_budget_l_per_day": water_budget,
            "suggestions": suggestions
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/soil_types', methods=['GET'])
def get_soil_types():
    """Return available soil types"""
    return jsonify({
        "soil_types": ["loam", "sandy", "clay", "silty"],
        "textures": ["fine", "balanced", "coarse"],
        "default_area": 1.0,
        "default_water_budget": 250
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Smart Agriculture Planner - Web UI")
    print("="*60)
    print("\n✅ Starting Flask web server...")
    print("📱 Open http://127.0.0.1:5000 in your browser")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, port=5000, use_reloader=False)
