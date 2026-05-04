"""
Keyboard layouts for Exhibition Booth Configurator Bot.
Supports multi-language and navigation.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import CONSTRUCTION_TYPES, MATERIALS, EQUIPMENT, BASE_PRICE_PER_SQM
from translations import get_text


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_EN"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_RUS"),
            InlineKeyboardButton(text="🇱🇻 Latviešu", callback_data="lang_LV"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_start_keyboard(language: str = "EN") -> InlineKeyboardMarkup:
    """Get start menu keyboard."""
    buttons = [
        [InlineKeyboardButton(text=get_text(language, "btn_start"), callback_data="start_config")],
        [InlineKeyboardButton(text=get_text(language, "btn_about"), callback_data="about")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_length_keyboard(language: str = "EN") -> InlineKeyboardMarkup:
    """Get length selection keyboard."""
    buttons = []
    for length in [2.0, 3.0, 4.0, 5.0, 6.0]:
        buttons.append([InlineKeyboardButton(text=f"{length}m", callback_data=f"length_{length}")])
    
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_cancel"), callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_width_keyboard(language: str = "EN") -> InlineKeyboardMarkup:
    """Get width selection keyboard."""
    buttons = []
    for width in [2.0, 3.0, 4.0, 5.0, 6.0]:
        buttons.append([InlineKeyboardButton(text=f"{width}m", callback_data=f"width_{width}")])
    
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_back"), callback_data="back_to_length")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_cancel"), callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_construction_type_keyboard(language: str = "EN", length: float = 0, width: float = 0) -> InlineKeyboardMarkup:
    """Get construction type selection keyboard with price preview."""
    buttons = []
    area = length * width if length > 0 and width > 0 else 0
    base_cost = area * BASE_PRICE_PER_SQM if area > 0 else 0
    
    for key, value in CONSTRUCTION_TYPES.items():
        # Calculate cost for this construction type
        construction_cost = base_cost * value['multiplier']
        cost_text = f" (+{construction_cost:.2f}€)" if area > 0 else ""
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{value['emoji']} {value['name']}{cost_text}",
                callback_data=f"construction_{key}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_back"), callback_data="back_to_width")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_cancel"), callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_materials_keyboard(selected_materials: list = None, language: str = "EN") -> InlineKeyboardMarkup:
    """Get materials selection keyboard with checkmarks and prices."""
    if selected_materials is None:
        selected_materials = []
    
    buttons = []
    
    for key, value in MATERIALS.items():
        checkmark = "✅" if key in selected_materials else "⬜"
        price_text = f" ({value['price']}€)"
        buttons.append([
            InlineKeyboardButton(
                text=f"{checkmark} {value['emoji']} {value['name']}{price_text}",
                callback_data=f"material_{key}"
            )
        ])
    
    # Next button
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_next"), callback_data="materials_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_back"), callback_data="back_to_construction")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_cancel"), callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_equipment_keyboard(selected_equipment: list = None, language: str = "EN") -> InlineKeyboardMarkup:
    """Get equipment selection keyboard with checkmarks and prices."""
    if selected_equipment is None:
        selected_equipment = []
    
    buttons = []
    
    for key, value in EQUIPMENT.items():
        checkmark = "✅" if key in selected_equipment else "⬜"
        price_text = f" ({value['price']}€)"
        buttons.append([
            InlineKeyboardButton(
                text=f"{checkmark} {value['emoji']} {value['name']}{price_text}",
                callback_data=f"equipment_{key}"
            )
        ])
    
    # Calculate button
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_calculate"), callback_data="equipment_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_back"), callback_data="back_to_materials")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "btn_cancel"), callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_keyboard(language: str = "EN") -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    buttons = [
        [InlineKeyboardButton(text=get_text(language, "btn_confirm"), callback_data="confirm_order")],
        [InlineKeyboardButton(text=get_text(language, "btn_back"), callback_data="back_to_equipment")],
        [InlineKeyboardButton(text=get_text(language, "btn_cancel"), callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_final_keyboard(language: str = "EN") -> InlineKeyboardMarkup:
    """Get final keyboard after order confirmation."""
    buttons = [
        [InlineKeyboardButton(text=get_text(language, "btn_start"), callback_data="start_config")],
        [InlineKeyboardButton(text=get_text(language, "btn_main_menu"), callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard(language: str = "EN") -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    buttons = [
        [InlineKeyboardButton(text=get_text(language, "btn_start"), callback_data="start_config")],
        [InlineKeyboardButton(text=get_text(language, "btn_main_menu"), callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
