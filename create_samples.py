"""
Sample soil image generator for testing
Creates simple placeholder images for soil type testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_images():
    """Generate sample soil images with labels"""
    samples_dir = "samples"
    os.makedirs(samples_dir, exist_ok=True)
    
    soil_types = {
        "soil_loam.jpg": {
            "color": (139, 90, 43),  # Brown - loam
            "label": "Loam Soil",
            "texture": "Balanced"
        },
        "soil_sandy.jpg": {
            "color": (210, 180, 140),  # Tan - sandy
            "label": "Sandy Soil",
            "texture": "Coarse"
        },
        "soil_clay.jpg": {
            "color": (101, 67, 33),  # Dark brown - clay
            "label": "Clay Soil",
            "texture": "Fine"
        },
        "soil_silty.jpg": {
            "color": (160, 120, 80),  # Medium brown - silty
            "label": "Silty Soil",
            "texture": "Fine"
        }
    }
    
    for filename, props in soil_types.items():
        filepath = os.path.join(samples_dir, filename)
        
        # Skip if already exists
        if os.path.exists(filepath):
            continue
        
        # Create image
        img = Image.new('RGB', (400, 300), props["color"])
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"{props['label']}\n{props['texture']} Texture"
        
        # Try to use a nice font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            font_small = font
        
        # Draw semi-transparent background for text
        draw.rectangle([(20, 100), (380, 200)], fill=(255, 255, 255, 128))
        
        # Draw text
        draw.text((40, 120), props['label'], fill=(0, 0, 0), font=font)
        draw.text((40, 160), f"Texture: {props['texture']}", fill=(50, 50, 50), font=font_small)
        
        # Save
        img.save(filepath)
        print(f"✓ Created {filepath}")

if __name__ == "__main__":
    create_sample_images()
    print("\nSample soil images created in samples/ folder")
