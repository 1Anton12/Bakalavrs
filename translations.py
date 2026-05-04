"""
Translations for Exhibition Booth Configurator Bot.
Supports: Russian (RUS), Latvian (LV), English (EN)
"""

TRANSLATIONS = {
    "EN": {
        # Commands and general
        "language_selection": "🌍 **Select your language:**",
        "welcome": """
👋 **Welcome to the Exhibition Booth Configurator!**

I will help you create the perfect booth for your exhibition.

Let's get started! 🚀
""",
        "help": """
❓ **HELP**

**Commands:**
• /start - Start configuration
• /help - Show this help
• /cancel - Cancel current configuration

**How to use the bot:**
1. Select language
2. Choose parameters by clicking buttons
3. Use ⬅️ Back to modify previous choices
4. After completion, you will see a full summary with cost calculation
""",
        "canceled": "❌ Configuration canceled. Use /start to begin again.",
        
        # Configuration steps
        "step_length": "📐 **Select booth length (in meters):**",
        "step_width": "📐 **Select booth width (in meters):**",
        "step_construction": "🏗️ **Select construction type:**",
        "step_materials": "🎨 **Select materials (you can choose multiple):**",
        "step_equipment": "⚙️ **Select additional equipment (you can choose multiple):**",
        "step_confirmation": "📋 **Review your configuration:**",
        
        # Selected items display
        "selected_length": "✅ Length: {length}m",
        "selected_width": "✅ Width: {width}m",
        "selected_area": "📊 Area: {area}m²",
        "selected_construction": "✅ Construction: {construction}",
        "selected_materials": "✅ Materials: {materials}",
        "selected_equipment": "✅ Equipment: {equipment}",
        "none_selected": "None selected",
        
        # Buttons
        "btn_next": "✅ Next",
        "btn_calculate": "💰 Calculate Total",
        "btn_confirm": "✅ Confirm Order",
        "confirm_order": "✅ Confirm Order",
        "btn_back": "⬅️ Back",
        "btn_cancel": "❌ Cancel",
        "btn_start": "🚀 Start Configuration",
        "btn_main_menu": "📋 Main Menu",
        "btn_about": "ℹ️ About",
        
        # Final messages
        "order_confirmed": "✅ **ORDER CONFIRMED!**",
        "thank_you": "📧 Thank you for using our service! Your configuration has been saved.",
        "new_config": "To create a new configuration, use /start",
        
        # Visualization
        "booth_visualization": "🏗️ **Booth Visualization:**",
        "booth_size": "Size: {length}m × {width}m",
        "booth_area": "Area: {area}m²",
    },
    
    "RUS": {
        # Commands and general
        "language_selection": "🌍 **Выберите язык:**",
        "welcome": """
👋 **Добро пожаловать в Конфигуратор выставочных стендов!**

Я помогу вам создать идеальный стенд для вашей выставки.

Начнём! 🚀
""",
        "help": """
❓ **СПРАВКА**

**Команды:**
• /start - Начать конфигурацию
• /help - Показать справку
• /cancel - Отменить конфигурацию

**Как использовать бота:**
1. Выберите язык
2. Выбирайте параметры, нажимая кнопки
3. Используйте ⬅️ Назад для изменения предыдущего выбора
4. По завершении вы увидите полную смету с расчетом стоимости
""",
        "canceled": "❌ Конфигурация отменена. Используйте /start для начала.",
        
        # Configuration steps
        "step_length": "📐 **Выберите длину стенда (в метрах):**",
        "step_width": "📐 **Выберите ширину стенда (в метрах):**",
        "step_construction": "🏗️ **Выберите тип конструкции:**",
        "step_materials": "🎨 **Выберите материалы (можно выбрать несколько):**",
        "step_equipment": "⚙️ **Выберите дополнительное оборудование (можно выбрать несколько):**",
        "step_confirmation": "📋 **Проверьте вашу конфигурацию:**",
        
        # Selected items display
        "selected_length": "✅ Длина: {length}м",
        "selected_width": "✅ Ширина: {width}м",
        "selected_area": "📊 Площадь: {area}м²",
        "selected_construction": "✅ Конструкция: {construction}",
        "selected_materials": "✅ Материалы: {materials}",
        "selected_equipment": "✅ Оборудование: {equipment}",
        "none_selected": "Ничего не выбрано",
        
        # Buttons
        "btn_next": "✅ Далее",
        "btn_calculate": "💰 Рассчитать",
        "btn_confirm": "✅ Подтвердить",
        "confirm_order": "✅ Подтвердить заказ",
        "btn_back": "⬅️ Назад",
        "btn_cancel": "❌ Отменить",
        "btn_start": "🚀 Начать",
        "btn_main_menu": "📋 Главное меню",
        "btn_about": "ℹ️ О боте",
        
        # Final messages
        "order_confirmed": "✅ **ЗАКАЗ ПОДТВЕРЖДЕН!**",
        "thank_you": "📧 Спасибо за использование нашего сервиса! Ваша конфигурация сохранена.",
        "new_config": "Для создания новой конфигурации используйте /start",
        
        # Visualization
        "booth_visualization": "🏗️ **Визуализация стенда:**",
        "booth_size": "Размер: {length}м × {width}м",
        "booth_area": "Площадь: {area}м²",
    },
    
    "LV": {
        # Commands and general
        "language_selection": "🌍 **Izvēlieties valodu:**",
        "welcome": """
👋 **Laipni lūdzam izstāžu stendu konfiguratorā!**

Es palīdzēšu jums izveidot ideālu stendu jūsu izstādei.

Sāksim! 🚀
""",
        "help": """
❓ **PALĪDZĪBA**

**Komandas:**
• /start - Sākt konfigurāciju
• /help - Rādīt palīdzību
• /cancel - Atcelt konfigurāciju

**Kā lietot botu:**
1. Izvēlieties valodu
2. Izvēlieties parametrus, noklikšķinot uz pogām
3. Izmantojiet ⬅️ Atpakaļ, lai mainītu iepriekšējo izvēli
4. Pēc pabeigšanas jūs redzēsiet pilnu kopsavilkumu ar izmaksu aprēķinu
""",
        "canceled": "❌ Konfigurācija atcelta. Izmantojiet /start, lai sāktu no jauna.",
        
        # Configuration steps
        "step_length": "📐 **Izvēlieties stenda garumu (metros):**",
        "step_width": "📐 **Izvēlieties stenda platumu (metros):**",
        "step_construction": "🏗️ **Izvēlieties konstrukcijas tipu:**",
        "step_materials": "🎨 **Izvēlieties materiālus (varat izvēlēties vairākus):**",
        "step_equipment": "⚙️ **Izvēlieties papildu aprīkojumu (varat izvēlēties vairākus):**",
        "step_confirmation": "📋 **Pārskatiet jūsu konfigurāciju:**",
        
        # Selected items display
        "selected_length": "✅ Garums: {length}m",
        "selected_width": "✅ Platums: {width}m",
        "selected_area": "📊 Platība: {area}m²",
        "selected_construction": "✅ Konstrukcija: {construction}",
        "selected_materials": "✅ Materiāli: {materials}",
        "selected_equipment": "✅ Aprīkojums: {equipment}",
        "none_selected": "Nekas nav izvēlēts",
        
        # Buttons
        "btn_next": "✅ Tālāk",
        "btn_calculate": "💰 Aprēķināt",
        "btn_confirm": "✅ Apstiprināt",
        "confirm_order": "✅ Apstiprināt pasūtījumu",
        "btn_back": "⬅️ Atpakaļ",
        "btn_cancel": "❌ Atcelt",
        "btn_start": "🚀 Sākt",
        "btn_main_menu": "📋 Galvenā izvēlne",
        "btn_about": "ℹ️ Par botu",
        
        # Final messages
        "order_confirmed": "✅ **PASŪTĪJUMS APSTIPRINĀTS!**",
        "thank_you": "📧 Paldies par mūsu pakalpojuma izmantošanu! Jūsu konfigurācija ir saglabāta.",
        "new_config": "Lai izveidotu jaunu konfigurāciju, izmantojiet /start",
        
        # Visualization
        "booth_visualization": "🏗️ **Stenda vizualizācija:**",
        "booth_size": "Izmērs: {length}m × {width}m",
        "booth_area": "Platība: {area}m²",
    }
}


def get_text(language: str, key: str, **kwargs) -> str:
    """
    Get translated text.
    
    Args:
        language: Language code (EN, RUS, LV)
        key: Translation key
        **kwargs: Format parameters
    
    Returns:
        Translated text or key if not found
    """
    if language not in TRANSLATIONS:
        language = "EN"
    
    text = TRANSLATIONS[language].get(key, key)
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    
    return text
