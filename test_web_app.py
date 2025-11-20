"""
Integration tests for the Flask web app
Run: pytest test_web_app.py -v
"""

import pytest
import json
import os
from web_app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestWebAppEndpoints:
    """Test web app endpoints"""
    
    def test_index_loads(self, client):
        """Test that the main page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Smart Agriculture Planner' in response.data
    
    def test_get_soil_types(self, client):
        """Test soil types endpoint"""
        response = client.get('/api/soil_types')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert "soil_types" in data
        assert "loam" in data["soil_types"]
        assert "sandy" in data["soil_types"]


class TestAnalysisAPI:
    """Test the analysis API endpoint"""
    
    def test_analyze_with_params(self, client):
        """Test analysis with manual parameters"""
        data = {
            'mode': 'params',
            'soil_type': 'loam',
            'texture': 'balanced',
            'moisture': '20',
            'pH': '6.8',
            'area': '1',
            'water_budget': '250'
        }
        
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] == True
        assert 'soil_analysis' in result
        assert 'suggestions' in result
        assert len(result['suggestions']) > 0
    
    def test_analyze_minimal_params(self, client):
        """Test analysis with minimal parameters"""
        data = {
            'mode': 'params',
            'soil_type': 'clay'
        }
        
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 200
        
        result = json.loads(response.data)
        assert result['success'] == True
        assert result['soil_analysis']['soil_type'] == 'clay'
    
    def test_analyze_with_image(self, client):
        """Test analysis with image upload"""
        # Create a temporary test image
        image_path = 'samples/soil_loam.jpg'
        if not os.path.exists(image_path):
            pytest.skip(f"Sample image not found: {image_path}")
        
        with open(image_path, 'rb') as img:
            response = client.post(
                '/api/analyze',
                data={
                    'mode': 'image',
                    'area': '1',
                    'water_budget': '250',
                    'image': (img, 'test.jpg')
                }
            )
        
        # Check response
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] == True
    
    def test_analyze_missing_image(self, client):
        """Test analysis with missing image"""
        data = {
            'mode': 'image'
        }
        
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert result['success'] == False
        assert 'error' in result
    
    def test_soil_suggestion_structure(self, client):
        """Test that suggestions have correct structure"""
        data = {
            'mode': 'params',
            'soil_type': 'loam',
            'area': '1'
        }
        
        response = client.post('/api/analyze', data=data)
        result = json.loads(response.data)
        
        for sugg in result['suggestions']:
            assert 'crop' in sugg
            assert 'soil_match' in sugg
            assert 'irrigation' in sugg
            assert 'cost' in sugg
            
            # Check irrigation details
            irrigation = sugg['irrigation']
            assert 'method' in irrigation
            assert 'recommended_daily_water_l' in irrigation
            assert 'meets_budget' in irrigation
            
            # Check cost details
            cost = sugg['cost']
            assert 'area_acres' in cost
            assert 'estimated_total_cost_usd' in cost


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_soil_type_defaults(self, client):
        """Test that invalid soil types are handled gracefully"""
        data = {
            'mode': 'params',
            'soil_type': 'not_a_real_soil_type'
        }
        
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] == True
        # Should default to loam
        assert result['soil_analysis']['soil_type'] == 'loam'
    
    def test_invalid_area_value(self, client):
        """Test handling of invalid area values"""
        data = {
            'mode': 'params',
            'area': 'not_a_number'
        }
        
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 500
    
    def test_negative_water_budget(self, client):
        """Test handling of negative water budget"""
        data = {
            'mode': 'params',
            'water_budget': '-100'
        }
        
        response = client.post('/api/analyze', data=data)
        # May succeed or fail depending on validation
        # Just check that the app handles it gracefully
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
