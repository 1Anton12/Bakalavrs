"""FSM States for Exhibition Booth Configurator Bot.
Supports multi-language and navigation."""

from aiogram.fsm.state import State, StatesGroup


class ConfigurationStates(StatesGroup):
    """States for booth configuration flow."""
    
    # Language selection
    selecting_language = State()
    
    # Configuration steps
    choosing_length = State()
    choosing_width = State()
    choosing_construction_type = State()
    choosing_materials = State()
    choosing_equipment = State()
    confirmation = State()
    final_report = State()
