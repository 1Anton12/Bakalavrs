"""
Booth visualization module for Exhibition Booth Configurator.
Creates ASCII/Emoji visualizations of booth configurations.
"""

from config import CONSTRUCTION_TYPES, MATERIALS, EQUIPMENT


def generate_booth_visualization(length: float, width: float, construction_type: str, materials: list, equipment: list) -> str:
    """
    Generate a visual representation of the booth configuration.
    
    Args:
        length: Booth length in meters
        width: Booth width in meters
        construction_type: Type of construction
        materials: List of selected materials
        equipment: List of selected equipment
    
    Returns:
        String with ASCII/Emoji visualization
    """
    
    # Get construction and material names
    construction_name = CONSTRUCTION_TYPES.get(construction_type, {}).get("name", "Unknown")
    
    materials_names = []
    for mat in materials:
        if mat in MATERIALS:
            materials_names.append(MATERIALS[mat]["name"])
    
    equipment_names = []
    for eq in equipment:
        if eq in EQUIPMENT:
            equipment_names.append(EQUIPMENT[eq]["name"])
    
    # Create size visualization
    length_blocks = int(length)
    width_blocks = int(width)
    
    # Limit blocks for display
    max_blocks = 6
    if length_blocks > max_blocks:
        length_blocks = max_blocks
    if width_blocks > max_blocks:
        width_blocks = max_blocks
    
    # Create booth frame
    booth_top = "🟦" * length_blocks
    booth_middle = "🟦" + "⬜" * (length_blocks - 2) + "🟦" if length_blocks > 2 else "🟦" * length_blocks
    booth_bottom = "🟦" * length_blocks
    
    # Build visualization
    visualization = "```\n"
    visualization += "BOOTH VISUALIZATION\n"
    visualization += "=" * 30 + "\n\n"
    
    # Draw booth
    visualization += booth_top + "\n"
    for _ in range(max(1, width_blocks - 2)):
        visualization += booth_middle + "\n"
    visualization += booth_bottom + "\n\n"
    
    # Add details
    visualization += "```\n\n"
    
    # Add configuration details
    details = f"""
📏 **Dimensions:** {length}m × {width}m
📊 **Area:** {length * width}m²

🏗️ **Construction:** {construction_name}

🎨 **Materials:** {', '.join(materials_names) if materials_names else 'None selected'}

⚙️ **Equipment:** {', '.join(equipment_names) if equipment_names else 'None selected'}
"""
    
    return visualization + details


def generate_summary_with_visualization(length: float, width: float, construction_type: str, 
                                       materials: list, equipment: list, language: str = "EN") -> str:
    """
    Generate a complete summary with visualization.
    
    Args:
        length: Booth length
        width: Booth width
        construction_type: Construction type
        materials: List of materials
        equipment: List of equipment
        language: Language code
    
    Returns:
        Complete formatted summary
    """
    
    visualization = generate_booth_visualization(length, width, construction_type, materials, equipment)
    
    return visualization


def get_booth_emoji_representation(length: float, width: float) -> str:
    """
    Get a simple emoji representation of booth size.
    
    Args:
        length: Booth length
        width: Booth width
    
    Returns:
        Emoji representation
    """
    
    # Create simple size indicator
    size_indicator = ""
    
    if length <= 2:
        size_indicator += "🟩 "
    elif length <= 3:
        size_indicator += "🟩🟩 "
    elif length <= 4:
        size_indicator += "🟩🟩🟩 "
    else:
        size_indicator += "🟩🟩🟩🟩 "
    
    size_indicator += f"({length}m)\n"
    
    if width <= 2:
        size_indicator += "🟩 "
    elif width <= 3:
        size_indicator += "🟩🟩 "
    elif width <= 4:
        size_indicator += "🟩🟩🟩 "
    else:
        size_indicator += "🟩🟩🟩🟩 "
    
    size_indicator += f"({width}m)"
    
    return size_indicator


def get_current_configuration_summary(length: float = None, width: float = None, 
                                     construction_type: str = None, materials: list = None, 
                                     equipment: list = None, language: str = "EN") -> str:
    """
    Get a formatted summary of current configuration choices.
    
    Args:
        length: Booth length
        width: Booth width
        construction_type: Construction type
        materials: List of materials
        equipment: List of equipment
        language: Language code
    
    Returns:
        Formatted summary string
    """
    from translations import get_text
    
    summary = "📋 **" + get_text(language, "step_confirmation") + "**\n\n"
    
    if length:
        summary += get_text(language, "selected_length", length=length) + "\n"
    
    if width:
        summary += get_text(language, "selected_width", width=width) + "\n"
        if length:
            area = length * width
            summary += get_text(language, "selected_area", area=area) + "\n"
    
    if construction_type and construction_type in CONSTRUCTION_TYPES:
        construction_name = CONSTRUCTION_TYPES[construction_type]["name"]
        summary += get_text(language, "selected_construction", construction=construction_name) + "\n"
    
    if materials:
        materials_names = [MATERIALS[m]["name"] for m in materials if m in MATERIALS]
        if materials_names:
            summary += get_text(language, "selected_materials", materials=", ".join(materials_names)) + "\n"
    
    if equipment:
        equipment_names = [EQUIPMENT[eq]["name"] for eq in equipment if eq in EQUIPMENT]
        if equipment_names:
            summary += get_text(language, "selected_equipment", equipment=", ".join(equipment_names)) + "\n"
    
    return summary
