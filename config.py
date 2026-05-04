"""
Exhibition booth parameters and pricing configuration.
"""

# Base price per square meter (in currency units)
BASE_PRICE_PER_SQM = 100

# Construction types and their multipliers
CONSTRUCTION_TYPES = {
    "standard": {
        "emoji": "🏗️",
        "name": "Standard",
        "multiplier": 1.0,
        "description": "Basic construction"
    },
    "exclusive": {
        "emoji": "👑",
        "name": "Exclusive",
        "multiplier": 1.5,
        "description": "Premium construction with additional features"
    },
    "modular": {
        "emoji": "🔧",
        "name": "Modular",
        "multiplier": 1.2,
        "description": "Flexible construction for various configurations"
    }
}

# Materials and their costs
MATERIALS = {
    "plastic": {
        "emoji": "♻️",
        "name": "Plastic",
        "price": 50,
        "description": "Lightweight and economical material"
    },
    "wood": {
        "emoji": "🪵",
        "name": "Wood",
        "price": 150,
        "description": "Natural and aesthetic material"
    },
    "metal": {
        "emoji": "⚙️",
        "name": "Metal",
        "price": 200,
        "description": "Durable and reliable material"
    },
    "composite": {
        "emoji": "✨",
        "name": "Composite",
        "price": 180,
        "description": "Modern material with high-end characteristics"
    }
}

# Additional equipment and its costs
EQUIPMENT = {
    "lighting": {
        "emoji": "💡",
        "name": "LED Lighting",
        "price": 300,
        "description": "Professional LED lighting"
    },
    "furniture": {
        "emoji": "🪑",
        "name": "Furniture",
        "price": 250,
        "description": "Comfortable furniture for demonstration"
    },
    "monitor": {
        "emoji": "📺",
        "name": "Monitor (55\")",
        "price": 800,
        "description": "Large interactive screen"
    },
    "sound_system": {
        "emoji": "🔊",
        "name": "Sound System",
        "price": 400,
        "description": "Professional audio system"
    },
    "carpet": {
        "emoji": "🟫",
        "name": "Carpet",
        "price": 150,
        "description": "High-quality flooring"
    }
}

# Available dimensions (in meters)
AVAILABLE_LENGTHS = [2.0, 3.0, 4.0, 5.0, 6.0]
AVAILABLE_WIDTHS = [2.0, 3.0, 4.0, 5.0, 6.0]
