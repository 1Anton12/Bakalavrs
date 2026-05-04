"""
Module for calculating the cost of exhibition booth configurations.
Supports multi-language output.
"""

from config import BASE_PRICE_PER_SQM, CONSTRUCTION_TYPES, MATERIALS, EQUIPMENT


def calculate_total_cost(
    length: float,
    width: float,
    construction_type: str,
    materials: list = None,
    equipment: list = None
) -> dict:
    """
    Calculate the total cost of the booth configuration.
    
    Args:
        length: Booth length in meters
        width: Booth width in meters
        construction_type: Construction type key
        materials: List of selected material keys (optional)
        equipment: List of selected equipment keys (optional)
    
    Returns:
        Dictionary with detailed cost calculation
    """
    
    if materials is None:
        materials = []
    if equipment is None:
        equipment = []
    
    # Area calculation
    area = length * width
    
    # Base cost (area × base price)
    base_cost = area * BASE_PRICE_PER_SQM
    
    # Apply construction type multiplier
    if construction_type not in CONSTRUCTION_TYPES:
        construction_type = "standard"
    
    construction_multiplier = CONSTRUCTION_TYPES[construction_type]["multiplier"]
    construction_cost = base_cost * construction_multiplier
    
    # Materials cost
    materials_cost = 0
    for material in materials:
        if material in MATERIALS:
            materials_cost += MATERIALS[material]["price"]
    
    # Equipment cost
    equipment_cost = 0
    for item in equipment:
        if item in EQUIPMENT:
            equipment_cost += EQUIPMENT[item]["price"]
    
    # Total cost
    total_cost = construction_cost + materials_cost + equipment_cost
    
    return {
        "area": area,
        "base_cost": base_cost,
        "construction_type": CONSTRUCTION_TYPES[construction_type]["name"],
        "construction_multiplier": construction_multiplier,
        "construction_cost": construction_cost,
        "materials_cost": materials_cost,
        "equipment_cost": equipment_cost,
        "total_cost": total_cost,
        "materials": materials,
        "equipment": equipment
    }


def format_cost_summary(
    length: float,
    width: float,
    construction_type: str,
    materials: list = None,
    equipment: list = None,
    language: str = "EN"
) -> str:
    """
    Format the cost summary for user display.
    
    Args:
        length: Booth length in meters
        width: Booth width in meters
        construction_type: Construction type key
        materials: List of selected material keys (optional)
        equipment: List of selected equipment keys (optional)
        language: Language code (EN, RUS, LV)
    
    Returns:
        Formatted string with summary
    """
    
    if materials is None:
        materials = []
    if equipment is None:
        equipment = []
    
    cost_data = calculate_total_cost(length, width, construction_type, materials, equipment)
    
    # Build summary based on language
    if language == "RUS":
        summary = f"""
📊 **СВОДКА КОНФИГУРАЦИИ СТЕНДА**

📐 **Размеры:**
   • Длина: {length}м
   • Ширина: {width}м
   • Площадь: {cost_data['area']}м²

🏗️ **Конструкция:**
   • Тип: {cost_data['construction_type']}
   • Коэффициент: x{cost_data['construction_multiplier']}

🎨 **Материалы:**
"""
        
        if materials:
            for material_key in materials:
                if material_key in MATERIALS:
                    material = MATERIALS[material_key]
                    summary += f"   • {material['emoji']} {material['name']}: {material['price']}€\n"
        else:
            summary += "   • Ничего не выбрано\n"
        
        summary += "\n⚙️ **Оборудование:**\n"
        if equipment:
            for equipment_key in equipment:
                if equipment_key in EQUIPMENT:
                    equip = EQUIPMENT[equipment_key]
                    summary += f"   • {equip['emoji']} {equip['name']}: {equip['price']}€\n"
        else:
            summary += "   • Ничего не выбрано\n"
        
        summary += f"""
💰 **РАСЧЕТ СТОИМОСТИ:**
   • Базовая стоимость: {cost_data['base_cost']:.2f}€
   • Стоимость конструкции: {cost_data['construction_cost']:.2f}€
   • Материалы: {cost_data['materials_cost']:.2f}€
   • Оборудование: {cost_data['equipment_cost']:.2f}€
   
   **ИТОГО: {cost_data['total_cost']:.2f}€**
"""
    
    elif language == "LV":
        summary = f"""
📊 **STENDA KONFIGURĀCIJAS KOPSAVILKUMS**

📐 **Izmēri:**
   • Garums: {length}m
   • Platums: {width}m
   • Platība: {cost_data['area']}m²

🏗️ **Konstrukcija:**
   • Tips: {cost_data['construction_type']}
   • Reizinātājs: x{cost_data['construction_multiplier']}

🎨 **Materiāli:**
"""
        
        if materials:
            for material_key in materials:
                if material_key in MATERIALS:
                    material = MATERIALS[material_key]
                    summary += f"   • {material['emoji']} {material['name']}: {material['price']}€\n"
        else:
            summary += "   • Nekas nav izvēlēts\n"
        
        summary += "\n⚙️ **Aprīkojums:**\n"
        if equipment:
            for equipment_key in equipment:
                if equipment_key in EQUIPMENT:
                    equip = EQUIPMENT[equipment_key]
                    summary += f"   • {equip['emoji']} {equip['name']}: {equip['price']}€\n"
        else:
            summary += "   • Nekas nav izvēlēts\n"
        
        summary += f"""
💰 **IZMAKSU APRĒĶINS:**
   • Bāzes izmaksas: {cost_data['base_cost']:.2f}€
   • Konstrukcijas izmaksas: {cost_data['construction_cost']:.2f}€
   • Materiāli: {cost_data['materials_cost']:.2f}€
   • Aprīkojums: {cost_data['equipment_cost']:.2f}€
   
   **KOPĀ: {cost_data['total_cost']:.2f}€**
"""
    
    else:  # EN (default)
        summary = f"""
📊 **BOOTH CONFIGURATION SUMMARY**

📐 **Dimensions:**
   • Length: {length}m
   • Width: {width}m
   • Area: {cost_data['area']}m²

🏗️ **Construction:**
   • Type: {cost_data['construction_type']}
   • Multiplier: x{cost_data['construction_multiplier']}

🎨 **Materials:**
"""
        
        if materials:
            for material_key in materials:
                if material_key in MATERIALS:
                    material = MATERIALS[material_key]
                    summary += f"   • {material['emoji']} {material['name']}: {material['price']}€\n"
        else:
            summary += "   • None selected\n"
        
        summary += "\n⚙️ **Equipment:**\n"
        if equipment:
            for equipment_key in equipment:
                if equipment_key in EQUIPMENT:
                    equip = EQUIPMENT[equipment_key]
                    summary += f"   • {equip['emoji']} {equip['name']}: {equip['price']}€\n"
        else:
            summary += "   • None selected\n"
        
        summary += f"""
💰 **COST CALCULATION:**
   • Base Cost: {cost_data['base_cost']:.2f}€
   • Construction Cost: {cost_data['construction_cost']:.2f}€
   • Materials: {cost_data['materials_cost']:.2f}€
   • Equipment: {cost_data['equipment_cost']:.2f}€
   
   **TOTAL: {cost_data['total_cost']:.2f}€**
"""
    
    return summary
