"""
Exhibition Booth Configurator Bot v16.1 (PRICE DETAILS IMPROVED)
- Prices for each selected item are shown during step-by-step configuration
- Detailed cost summary updated at every toggle
- Empty categories hidden in intermediate steps, shown as "None" in final
"""

import os
import logging
import json
import datetime
from contextlib import suppress
from dotenv import load_dotenv

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest
import urllib.parse

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)
SUPPORT_CONTACT = os.getenv("SUPPORT_CONTACT", "@exhibition_stand_bot")
CONFIGURATOR_URL = "https://1anton12.github.io/Bakalavrs/booth_configurator.html"
MIN_DIM = 2.0
MAX_DIM = 10.0
MAX_AREA = 40.0

if not BOT_TOKEN:
    BOT_TOKEN = "8691159185:AAGOCOvQMex_7y46TzMCAmfQAXTkHEW4pk0"

# Import custom modules
try:
    from database import (
        init_db,
        add_user,
        save_order,
        get_user_orders,
        get_order_by_id,
        get_user_order_stats,
        get_order_stats,
    )
    logger.info("✅ database.py imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import database: {e}", exc_info=True)
    raise

try:
    from pdf_generator import generate_order_pdf
    logger.info("✅ pdf_generator.py imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import pdf_generator: {e}", exc_info=True)
    raise

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# ============================================================================
# STATES
# ============================================================================

class ConfigurationStates(StatesGroup):
    selecting_language = State()
    viewing_support = State()
    choosing_length = State()
    entering_length = State()
    choosing_width = State()
    entering_width = State()
    choosing_layout = State()
    choosing_construction_type = State()
    choosing_materials = State()
    choosing_finishing = State()
    choosing_equipment = State()
    choosing_services = State()
    confirmation = State()
    final_report = State()
    entering_phone = State()
    entering_email = State()
    booking_consultation = State()

# ============================================================================
# CONFIGURATION DATA
# ============================================================================

BASE_PRICE_PER_SQM = 100.0
LENGTHS = [2.0, 3.0, 4.0, 5.0, 6.0]
WIDTHS = [2.0, 2.5, 3.0, 3.5, 4.0]

LAYOUTS = {
    "standard": {"name_en": "Standard", "name_ru": "Стандартный", "name_lv": "Standarts", "multiplier": 1.0, "price_per_sqm": 0},
    "exclusive": {"name_en": "Exclusive", "name_ru": "Эксклюзивный", "name_lv": "Eksklusīvs", "multiplier": 1.5, "price_per_sqm": 50.0},
}

CONSTRUCTION_TYPES = {
    "standard": {"name_en": "Standard", "name_ru": "Стандартный", "name_lv": "Standarts", "multiplier": 1.0},
    "exclusive": {"name_en": "Exclusive", "name_ru": "Эксклюзивный", "name_lv": "Eksklusīvs", "multiplier": 1.5},
}

MATERIALS = {
    "plastic": {"name_en": "Plastic", "name_ru": "Пластик", "name_lv": "Plastmasa", "price_per_sqm": 50.0},
    "wood": {"name_en": "Wood", "name_ru": "Дерево", "name_lv": "Koks", "price_per_sqm": 150.0},
    "metal": {"name_en": "Metal", "name_ru": "Металл", "name_lv": "Metāls", "price_per_sqm": 200.0},
}

FINISHINGS = {
    "matte": {"name_en": "Matte", "name_ru": "Матовое", "name_lv": "Matēts", "price": 100.0},
    "glossy": {"name_en": "Glossy", "name_ru": "Глянцевое", "name_lv": "Spīdīgs", "price": 150.0},
    "textured": {"name_en": "Textured", "name_ru": "Текстурированное", "name_lv": "Teksturēts", "price": 120.0},
}

EQUIPMENT = {
    "lighting": {"name_en": "LED Lighting", "name_ru": "LED Освещение", "name_lv": "LED Apgaismojums", "price": 300.0},
    "sound": {"name_en": "Sound System", "name_ru": "Звуковая система", "name_lv": "Skaņas sistēma", "price": 500.0},
    "display": {"name_en": "Display Screen", "name_ru": "Экран дисплея", "name_lv": "Displeja ekrāns", "price": 800.0},
}

SERVICES = {
    "delivery": {"name_en": "Delivery", "name_ru": "Доставка", "name_lv": "Piegāde", "price": 200.0},
    "installation": {"name_en": "Installation", "name_ru": "Установка", "name_lv": "Instalācija", "price": 300.0},
    "support": {"name_en": "24/7 Support", "name_ru": "24/7 Поддержка", "name_lv": "24/7 Atbalsts", "price": 150.0},
}

# ============================================================================
# TEXTS (MULTILINGUAL) – Full original dictionary
# ============================================================================

TEXTS = {
    "EN": {
        "welcome": "🎉 **Welcome to Exhibition Booth Configurator!**\n\nLet's create your perfect booth. You can use our 3D Online Configurator or follow the step-by-step setup here.",
        "3d_configurator": "🎨 Open 3D Configurator Online",
        "quick_config": "⚙️ Step-by-Step Configuration",
        "support": "📞 Support & FAQ",
        "3d_description": "Click the button below to open the 3D visualizer with your current settings.",
        "step_length": "📏 **Select booth length (in meters):**",
        "step_width": "📐 **Select booth width (in meters):**",
        "step_construction": "🏗️ **Select construction type:**",
        "step_materials": "🎨 **Select materials (you can choose multiple):**",
        "step_equipment": "⚙️ **Select additional equipment (you can choose multiple):**",
        "selected_length": "✅ Length: {length}m",
        "selected_width": "✅ Width: {width}m",
        "selected_area": "📊 Area: {area}m²",
        "selected_layout": "🧩 Layout: {layout}",
        "selected_construction": "🏗️ Type: {construction}",
        "selected_materials": "🎨 Materials: {materials}",
        "selected_finishing": "✨ Finishing: {finishing}",
        "selected_equipment": "⚙️ Equipment: {equipment}",
        "selected_services": "🛠️ Services: {services}",
        "none_selected": "None",
        "calculate": "💰 Calculate Total",
        "confirm": "✅ Confirm Order",
        "cancel": "❌ Cancel",
        "back": "⬅️ Back",
        "order_confirmed": "🎉 **Order Confirmed!**\n\nYour PDF summary is being generated...",
        "main_menu": "🏠 Main Menu",
        "canceled": "❌ Configuration canceled. Select language to start again.",
        "help": "❓ **HELP**\n\nUse /start to begin, /cancel to cancel, /my_orders to see your saved configurations, /stats to view your totals.",
        "about": "ℹ️ This bot helps you create exhibition booth quotes with materials, services and order history.",
        "contacts": "📞 Contact support: {contact}",
        "my_orders": "📦 My Orders",
        "my_quote": "📌 Current Quote",
        "enter_length_custom": "Enter length from {min} to {max} meters:\n(example: 3.5)",
        "enter_width_custom": "Enter width from {min} to {max} meters:\n(example: 2.5)",
        "invalid_dimension": "❌ Invalid value. Enter a number from {min} to {max}.",
        "invalid_area": "❌ Area must not exceed {max_area} m². Reduce length or width.",
        "custom_length": "🔧 Other length",
        "custom_width": "🔧 Other width",
        "layout_selection": "🏟️ **Select stand layout:**",
        "finishing_selection": "🎨 **Choose stand finishing options:**",
        "services_selection": "⚙️ **Choose additional services:**",
        "order_saved": "✅ Order saved. You can view it in /my_orders.",
        "admin_notification": "📣 New order from {user} — total {total}€\nOrder ID: {order_id}",
        "stats_self": "📊 Your orders: {count}\nTotal spent: {total:.2f}€",
        "stats_admin": "📈 Orders in last 24h: {today_count} ({today_total:.2f}€)\nOrders in last 7 days: {week_count} ({week_total:.2f}€)\nTotal orders: {total_count} ({total_sum:.2f}€)",
        "press_button": "▶️ Please use the buttons to continue the configuration.",
        "no_configuration": "⚠️ No active configuration found yet. Start with /start.",
        "order_history": "📁 Your last orders:",
        "no_orders": "📭 No orders yet. Create your first quote with /start.",
        "copy_order": "Order ID: {order_id} | {created_at}\nSize: {length}x{width}m | Total: {total:.2f}€",
        "download_pdf": "📄 Download PDF",
        "cost_summary": "💰 **COST SUMMARY**\n\n",
        "base_price": "Base booth: ",
        "materials_cost": "Materials: ",
        "finishing_cost": "Finishing: ",
        "services_cost": "Services: ",
        "equipment_cost": "Equipment: ",
        "layout_cost": "Layout multiplier: x{multiplier}\n",
        "total_price": "\n**TOTAL: {total}€**",
        "error_calc": "❌ Error calculating cost. Please try again.",
        "support_title": "📞 **SUPPORT & FAQ**",
        "support_text": "**Working Hours:** Monday-Friday 9:00-18:00 (UTC+2)\n\n**FAQ:**\n1️⃣ What is the minimum booth size? → 2m x 2m\n2️⃣ Do you offer installation? → Yes, included in delivery package\n3️⃣ Can I modify my order? → Yes, up to 48 hours before event\n4️⃣ What payment methods do you accept? → Bank transfer, card payment\n\n**3D Configurator:** You can also configure your booth online using our 3D configurator at [booth-configurator.com](https://booth-configurator.com)\n\n**Contact Manager:** {contact}\n\n**Email:** support@exhibitionbooths.com",
        "book_consultation": "📅 Book Consultation",
        "enter_phone": "📱 Please enter your phone number:",
        "enter_email": "✉️ Please enter your email address:",
        "consultation_booked": "✅ Consultation booked! Our manager will contact you within 2 hours.",
        "payment_demo": "💳 Demo Payment (€10 deposit)",
        "payment_success": "✅ Payment received! Order ID: {order_id}",
        "what_next": "🎯 **What's next?**\n\n1. 📋 Review your configuration\n2. 💳 Make a deposit or full payment\n3. 📅 Book installation date\n4. 🚚 We'll deliver and install your booth\n5. 🎉 Enjoy your exhibition!",
        "modify_config": "🔄 Modify Configuration",
        "download_quote": "📥 Download Quote (PDF)",
    },
    "RUS": {
        "welcome": "🎉 **Добро пожаловать в Конфигуратор Выставочных Стендов!**\n\nДавайте создадим ваш идеальный стенд. Вы можете использовать наш 3D онлайн-конфигуратор или пройти пошаговую настройку здесь.",
        "3d_configurator": "🎨 Открыть 3D конфигуратор онлайн",
        "quick_config": "⚙️ Пошаговая конфигурация",
        "support": "📞 Поддержка и FAQ",
        "3d_description": "Нажмите кнопку ниже, чтобы открыть 3D визуализатор с вашими настройками.",
        "step_length": "📏 **Выберите длину стенда (в метрах):**",
        "step_width": "📐 **Выберите ширину стенда (в метрах):**",
        "step_construction": "🏗️ **Выберите тип конструкции:**",
        "step_materials": "🎨 **Выберите материалы (можно выбрать несколько):**",
        "step_equipment": "⚙️ **Выберите дополнительное оборудование (можно выбрать несколько):**",
        "selected_length": "✅ Длина: {length}м",
        "selected_width": "✅ Ширина: {width}м",
        "selected_area": "📊 Площадь: {area}м²",
        "selected_layout": "🧩 План: {layout}",
        "selected_construction": "🏗️ Тип: {construction}",
        "selected_materials": "🎨 Материалы: {materials}",
        "selected_finishing": "✨ Оформление: {finishing}",
        "selected_equipment": "⚙️ Оборудование: {equipment}",
        "selected_services": "🛠️ Услуги: {services}",
        "none_selected": "Не выбрано",
        "calculate": "💰 Рассчитать",
        "confirm": "✅ Подтвердить заказ",
        "cancel": "❌ Отмена",
        "back": "⬅️ Назад",
        "order_confirmed": "🎉 **Заказ подтвержден!**\n\nВаша смета в формате PDF формируется...",
        "main_menu": "🏠 Главное меню",
        "canceled": "❌ Конфигурация отменена. Выберите язык, чтобы начать заново.",
        "help": "❓ **ПОМОЩЬ**\n\nИспользуйте /start для начала, /cancel для отмены, /my_orders для просмотра сохраненных заказов, /stats для статистики.",
        "about": "ℹ️ Этот бот помогает создавать сметы для выставочных стендов с выбором материалов, услуг и историей заказов.",
        "contacts": "📞 Поддержка: {contact}",
        "my_orders": "📦 Мои заказы",
        "my_quote": "📌 Текущая смета",
        "enter_length_custom": "Введите длину от {min} до {max} метров:\n(пример: 3.5)",
        "enter_width_custom": "Введите ширину от {min} до {max} метров:\n(пример: 2.5)",
        "invalid_dimension": "❌ Неверное значение. Введите число от {min} до {max}.",
        "invalid_area": "❌ Площадь не должна превышать {max_area} м². Уменьшите длину или ширину.",
        "custom_length": "🔧 Другая длина",
        "custom_width": "🔧 Другая ширина",
        "layout_selection": "🏟️ **Выберите план стенда:**",
        "finishing_selection": "🎨 **Выберите вариант отделки:**",
        "services_selection": "⚙️ **Выберите дополнительные услуги:**",
        "order_saved": "✅ Заказ сохранен. Его можно просмотреть в /my_orders.",
        "admin_notification": "📣 Новый заказ от {user} — всего {total}€\nID заказа: {order_id}",
        "stats_self": "📊 Ваши заказы: {count}\nОбщая сумма: {total:.2f}€",
        "stats_admin": "📈 Заказы за последние 24ч: {today_count} ({today_total:.2f}€)\nЗа последние 7 дней: {week_count} ({week_total:.2f}€)\nВсего: {total_count} ({total_sum:.2f}€)",
        "press_button": "▶️ Пожалуйста, используйте кнопки для продолжения конфигурации.",
        "no_configuration": "⚠️ Активная конфигурация не найдена. Начните с /start.",
        "order_history": "📁 Ваши последние заказы:",
        "no_orders": "📭 Заказов еще нет. Создайте свою первую смету с /start.",
        "copy_order": "ID заказа: {order_id} | {created_at}\nРазмер: {length}x{width}м | Всего: {total:.2f}€",
        "download_pdf": "📄 Скачать PDF",
        "cost_summary": "💰 **СМЕТА СТОИМОСТИ**\n\n",
        "base_price": "Базовая стоимость стенда: ",
        "materials_cost": "Материалы: ",
        "finishing_cost": "Отделка: ",
        "services_cost": "Услуги: ",
        "equipment_cost": "Оборудование: ",
        "layout_cost": "Коэффициент плана: x{multiplier}\n",
        "total_price": "\n**ИТОГО: {total}€**",
        "error_calc": "❌ Ошибка при расчете стоимости. Попробуйте еще раз.",
        "support_title": "📞 **ПОДДЕРЖКА И FAQ**",
        "support_text": "**Время работы:** Пн-Пт 9:00-18:00 (UTC+2)\n\n**Часто задаваемые вопросы:**\n1️⃣ Какой минимальный размер стенда? → 2м x 2м\n2️⃣ Вы предоставляете установку? → Да, включено в пакет доставки\n3️⃣ Могу ли я изменить заказ? → Да, до 48 часов до события\n4️⃣ Какие способы оплаты вы принимаете? → Банковский перевод, оплата картой\n\n**3D Конфигуратор:** Вы также можете выполнить конфигурацию стенда онлайн, используя наш 3D конфигуратор на сайте [booth-configurator.com](https://booth-configurator.com)\n\n**Контакт менеджера:** {contact}\n\n**Email:** support@exhibitionbooths.com",
        "book_consultation": "📅 Записаться на консультацию",
        "enter_phone": "📱 Пожалуйста, введите ваш номер телефона:",
        "enter_email": "✉️ Пожалуйста, введите ваш адрес электронной почты:",
        "consultation_booked": "✅ Консультация записана! Наш менеджер свяжется с вами в течение 2 часов.",
        "payment_demo": "💳 Демо-платеж (€10 депозит)",
        "payment_success": "✅ Платеж получен! ID заказа: {order_id}",
        "what_next": "🎯 **Что дальше?**\n\n1. 📋 Проверьте вашу конфигурацию\n2. 💳 Внесите депозит или полную оплату\n3. 📅 Забронируйте дату установки\n4. 🚚 Мы доставим и установим ваш стенд\n5. 🎉 Наслаждайтесь выставкой!",
        "modify_config": "🔄 Изменить конфигурацию",
        "download_quote": "📥 Скачать смету (PDF)",
    },
    "LV": {
        "welcome": "🎉 **Sveicināti Exhibition Booth Configurator!**\n\nVeidosim jūsu ideālo stendu. Jūs varat izmantot mūsu 3D tiešsaistes konfiguratoru vai veikt pakāpenisku iestatīšanu šeit.",
        "3d_configurator": "🎨 Atvērt 3D konfiguratoru tiešsaistē",
        "quick_config": "⚙️ Pakāpeniska konfigurācija",
        "support": "📞 Atbalsts un FAQ",
        "3d_description": "Noklikšķiniet uz pogas zemāk, lai atvērtu 3D vizualizatoru ar jūsu iestatījumiem.",
        "step_length": "📏 **Izvēlieties stenda garumu (metros):**",
        "step_width": "📐 **Izvēlieties stenda platumu (metros):**",
        "step_construction": "🏗️ **Izvēlieties konstrukcijas tipu:**",
        "step_materials": "🎨 **Izvēlieties materiālus (varat izvēlēties vairākus):**",
        "step_equipment": "⚙️ **Izvēlieties papildu aprīkojumu (varat izvēlēties vairākus):**",
        "selected_length": "✅ Garums: {length}m",
        "selected_width": "✅ Platums: {width}m",
        "selected_area": "📊 Platība: {area}m²",
        "selected_layout": "🧩 Plāns: {layout}",
        "selected_construction": "🏗️ Tips: {construction}",
        "selected_materials": "🎨 Materiāli: {materials}",
        "selected_finishing": "✨ Apdare: {finishing}",
        "selected_equipment": "⚙️ Aprīkojums: {equipment}",
        "selected_services": "🛠️ Pakalpojumi: {services}",
        "none_selected": "Nav izvēlēts",
        "calculate": "💰 Aprēķināt kopējo",
        "confirm": "✅ Apstiprināt pasūtījumu",
        "cancel": "❌ Atcelt",
        "back": "⬅️ Atpakaļ",
        "order_confirmed": "🎉 **Pasūtījums apstiprināts!**\n\nJūsu PDF tāme tiek sagatavota...",
        "main_menu": "🏠 Galvenā izvēlne",
        "canceled": "❌ Konfigurācija atcelta. Izvēlieties valodu, lai sāktu no jauna.",
        "help": "❓ **PALĪDZĪBA**\n\nIzmantojiet /start lai sāktu, /cancel lai atceltu, /my_orders lai redzētu saglabātos pasūtījumus, /stats statistikai.",
        "about": "ℹ️ Šis bots palīdz izveidot izstāžu stendu tāmes ar materiālu, pakalpojumu izvēli un pasūtījumu vēsturi.",
        "contacts": "📞 Atbalsts: {contact}",
        "my_orders": "📦 Mani pasūtījumi",
        "my_quote": "📌 Pašreizējā tāme",
        "enter_length_custom": "Ievadiet garumu no {min} līdz {max} metriem:\n(piemērs: 3.5)",
        "enter_width_custom": "Ievadiet platumu no {min} līdz {max} metriem:\n(piemērs: 2.5)",
        "invalid_dimension": "❌ Nederīga vērtība. Ievadiet skaitli no {min} līdz {max}.",
        "invalid_area": "❌ Platība nedrīkst pārsniegt {max_area} m². Samaziniet garumu vai platumu.",
        "custom_length": "🔧 Cits garums",
        "custom_width": "🔧 Cits platums",
        "layout_selection": "🏟️ **Izvēlieties stenda plānu:**",
        "finishing_selection": "🎨 **Izvēlieties apdares variantus:**",
        "services_selection": "⚙️ **Izvēlieties papildu pakalpojumus:**",
        "order_saved": "✅ Pasūtījums saglabāts. To varat apskatīt /my_orders.",
        "admin_notification": "📣 Jauns pasūtījums no {user} — kopā {total}€\nPasūtījuma ID: {order_id}",
        "stats_self": "📊 Jūsu pasūtījumi: {count}\nKopējā summa: {total:.2f}€",
        "stats_admin": "📈 Pasūtījumi pēdējās 24h: {today_count} ({today_total:.2f}€)\nPēdējās 7 dienās: {week_count} ({week_total:.2f}€)\nKopā: {total_count} ({total_sum:.2f}€)",
        "press_button": "▶️ Lūdzu, izmantojiet pogas, lai turpinātu konfigurāciju.",
        "no_configuration": "⚠️ Aktīva konfigurācija nav atrasta. Sāciet ar /start.",
        "order_history": "📁 Jūsu pēdējie pasūtījumi:",
        "no_orders": "📭 Pasūtījumu vēl nav. Izveidojiet savu pirmo tāmi ar /start.",
        "copy_order": "ID: {order_id} | {created_at}\nIzmērs: {length}x{width}m | Kopā: {total:.2f}€",
        "download_pdf": "📄 Lejupielādēt PDF",
        "cost_summary": "💰 **IZMAKSU KOPSAVILKUMS**\n\n",
        "base_price": "Pamatne stendam: ",
        "materials_cost": "Materiāli: ",
        "finishing_cost": "Apdare: ",
        "services_cost": "Pakalpojumi: ",
        "equipment_cost": "Aprīkojums: ",
        "layout_cost": "Plāna reizinātājs: x{multiplier}\n",
        "total_price": "\n**KOPĀ: {total}€**",
        "error_calc": "❌ Kļūda aprēķinot izmaksas. Lūdzu, mēģiniet vēlreiz.",
        "support_title": "📞 **ATBALSTS UN FAQ**",
        "support_text": "**Darba laiks:** Pirmdiena-Piektdiena 9:00-18:00 (UTC+2)\n\n**Bieži uzdotie jautājumi:**\n1️⃣ Kāds ir minimālais stenda izmērs? → 2m x 2m\n2️⃣ Vai jūs sniedzat instalācijas pakalpojumus? → Jā, iekļauts piegādes paketē\n3️⃣ Vai es varu modificēt savu pasūtījumu? → Jā, līdz 48 stundām pirms pasākuma\n4️⃣ Kādus maksājuma veidus jūs pieņemat? → Bankas pārskaitījums, karšu maksājums\n\n**3D Konfigurators:** Jūs varat arī konfigurēt savu stendu tiešsaistē, izmantojot mūsu 3D konfiguratoru vietnē [booth-configurator.com](https://booth-configurator.com)\n\n**Menedžera kontakts:** {contact}\n\n**E-pasts:** support@exhibitionbooths.com",
        "book_consultation": "📅 Rezervēt konsultāciju",
        "enter_phone": "📱 Lūdzu, ievadiet savu tālruņa numuru:",
        "enter_email": "✉️ Lūdzu, ievadiet savu e-pasta adresi:",
        "consultation_booked": "✅ Konsultācija rezervēta! Mūsu menedžers ar jums sazinās 2 stundu laikā.",
        "payment_demo": "💳 Demonstrācijas maksājums (€10 depozīts)",
        "payment_success": "✅ Maksājums saņemts! Pasūtījuma ID: {order_id}",
        "what_next": "🎯 **Kas tālāk?**\n\n1. 📋 Pārskatiet savu konfigurāciju\n2. 💳 Veiciet depozīta vai pilna maksājuma samaksu\n3. 📅 Rezervējiet instalācijas datumu\n4. 🚚 Mēs piegādāsim un instalēsim jūsu stendu\n5. 🎉 Baudiet izstādi!",
        "modify_config": "🔄 Modificēt konfigurāciju",
        "download_quote": "📥 Lejupielādēt tāmi (PDF)",
    }
}

def get_text(language, key, **kwargs):
    """Get translated text."""
    text = TEXTS.get(language, TEXTS["EN"]).get(key, "")
    return text.format(**kwargs) if kwargs else text

def get_language_code(language):
    """Convert language code to suffix used in keys."""
    lang_map = {"EN": "en", "RUS": "ru", "LV": "lv"}
    return lang_map.get(language, "en")

# ============================================================================
# KEYBOARD BUILDERS (unchanged from original except start keyboard already fixed)
# ============================================================================

def get_language_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_EN")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_RUS")],
        [InlineKeyboardButton(text="🇱🇻 Latviešu", callback_data="lang_LV")]
    ])
    return kb

def get_start_keyboard(language):
    url = CONFIGURATOR_URL 
    print(f"DEBUG: Opening WebApp with URL: {url}") 
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[language]["3d_configurator"], web_app=WebAppInfo(url=url))],
        [InlineKeyboardButton(text=TEXTS[language]["quick_config"], callback_data="start_config")],
        [InlineKeyboardButton(text=TEXTS[language]["support_faq"], callback_data="view_support")]
    ])
    return kb


def get_length_keyboard(language):
    default_width = 3.0   # для оценки цены
    buttons = []
    for l in LENGTHS:
        price = BASE_PRICE_PER_SQM * l * default_width
        text = f"{l}м ({price:.0f}€)"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"length_{l}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "custom_length"), callback_data="custom_length")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_width_keyboard(language, length):
    buttons = []
    for w in WIDTHS:
        area = length * w
        price = BASE_PRICE_PER_SQM * area
        text = f"{w}м ({price:.0f}€)"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"width_{w}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "custom_width"), callback_data="custom_width")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_length")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_layout_keyboard(language):
    buttons = []
    for key, val in LAYOUTS.items():
        name = val.get(f"name_{get_language_code(language)}", val["name_en"])
        mult = val["multiplier"]
        extra = val["price_per_sqm"]
        if extra > 0:
            text = f"{name} (+{extra:.0f}€/m²)"
        else:
            text = f"{name} (x{mult:.1f})"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"layout_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_width")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_construction_keyboard(language):
    buttons = []
    for key, val in CONSTRUCTION_TYPES.items():
        name = val.get(f"name_{get_language_code(language)}", val["name_en"])
        mult = val["multiplier"]
        text = f"{name} (x{mult:.1f})"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"construction_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_layout")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_materials_keyboard(language, selected_materials):
    buttons = []
    for key, val in MATERIALS.items():
        name = val.get(f"name_{get_language_code(language)}", val["name_en"])
        price = val["price_per_sqm"]
        check = "✅" if key in selected_materials else "☐"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f}€/m²", callback_data=f"material_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "calculate"), callback_data="materials_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_construction")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_finishing_keyboard(language, selected_finishing):
    buttons = []
    for key, val in FINISHINGS.items():
        name = val.get(f"name_{get_language_code(language)}", val["name_en"])
        price = val["price"]
        check = "✅" if key in selected_finishing else "☐"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f}€", callback_data=f"finishing_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "calculate"), callback_data="finishing_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "confirm_order"), callback_data="confirm_order_from_finishing")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_materials")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_equipment_keyboard(language, selected_equipment):
    buttons = []
    for key, val in EQUIPMENT.items():
        name = val.get(f"name_{get_language_code(language)}", val["name_en"])
        price = val["price"]
        check = "✅" if key in selected_equipment else "☐"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f}€", callback_data=f"equipment_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "calculate"), callback_data="equipment_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_finishing")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_services_keyboard(language, selected_services):
    buttons = []
    for key, val in SERVICES.items():
        name = val.get(f"name_{get_language_code(language)}", val["name_en"])
        price = val["price"]
        check = "✅" if key in selected_services else "☐"
        buttons.append([InlineKeyboardButton(text=f"{check} {name} +{price:.0f}€", callback_data=f"service_{key}")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "calculate"), callback_data="services_done")])
    buttons.append([InlineKeyboardButton(text=get_text(language, "back"), callback_data="back_to_equipment")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

def get_post_calculation_keyboard(language):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "payment_demo"), callback_data="demo_payment")],
        [InlineKeyboardButton(text=get_text(language, "book_consultation"), callback_data="book_consultation")],
        [InlineKeyboardButton(text=get_text(language, "modify_config"), callback_data="start_config")],
        [InlineKeyboardButton(text=get_text(language, "download_quote"), callback_data="download_quote")],
        [InlineKeyboardButton(text=get_text(language, "main_menu"), callback_data="main_menu")]
    ])
    return kb

# ============================================================================
# COST CALCULATION (unchanged)
# ============================================================================

def calculate_cost(length, width, construction_type, layout_type, materials, finishing, equipment, services):
    try:
        length = float(length) if length else 2.0
        width = float(width) if width else 2.0
        area = length * width
        
        base_cost = BASE_PRICE_PER_SQM * area

        construction = CONSTRUCTION_TYPES.get(construction_type, CONSTRUCTION_TYPES["standard"])
        construction_multiplier = construction.get("multiplier", 1.0)
        layout = LAYOUTS.get(layout_type, LAYOUTS["standard"])
        layout_multiplier = layout.get("multiplier", 1.0)

        total_base = base_cost * construction_multiplier * layout_multiplier
        materials_total = sum([MATERIALS[m]["price_per_sqm"] * area for m in materials if m in MATERIALS])
        finishing_total = sum([FINISHINGS[f]["price"] for f in finishing if f in FINISHINGS])
        equipment_total = sum([EQUIPMENT[e]["price"] for e in equipment if e in EQUIPMENT])
        services_total = sum([SERVICES[s]["price"] for s in services if s in SERVICES])

        total = total_base + materials_total + finishing_total + equipment_total + services_total
        
        return {
            "area": area,
            "base": total_base,
            "construction_multiplier": construction_multiplier,
            "layout_multiplier": layout_multiplier,
            "materials": materials_total,
            "finishing": finishing_total,
            "equipment": equipment_total,
            "services": services_total,
            "total": round(total, 2)
        }
    except Exception as e:
        logger.error(f"Error in calculation: {e}")
        return {"base": 0, "construction_multiplier": 1.0, "layout_multiplier": 1.0, "materials": 0, "finishing": 0, "equipment": 0, "services": 0, "total": 0}

# ============================================================================
# DETAILED COST SUMMARY (NEW)
# ============================================================================

def format_cost_summary(language, length, width, layout_type, construction_type,
                        materials, finishing, equipment, services, show_empty=False):
    costs = calculate_cost(length, width, construction_type, layout_type,
                           materials, finishing, equipment, services)
    area = length * width
    lines = []
    lines.append(get_text(language, "selected_length", length=length))
    lines.append(get_text(language, "selected_width", width=width))
    lines.append(get_text(language, "selected_area", area=area))

    layout_name = LAYOUTS.get(layout_type, LAYOUTS["standard"]).get(
        f"name_{get_language_code(language)}", LAYOUTS["standard"]["name_en"])
    lines.append(get_text(language, "selected_layout", layout=layout_name))
    construction_name = CONSTRUCTION_TYPES.get(construction_type, CONSTRUCTION_TYPES["standard"]).get(
        f"name_{get_language_code(language)}", CONSTRUCTION_TYPES["standard"]["name_en"])
    lines.append(get_text(language, "selected_construction", construction=construction_name))
    lines.append("")

    if materials or show_empty:
        lines.append("🎨 " + get_text(language, "materials_cost").rstrip(":") + ":")
        if materials:
            for m in materials:
                mat = MATERIALS[m]
                name = mat.get(f"name_{get_language_code(language)}", mat["name_en"])
                item_cost = mat["price_per_sqm"] * area
                lines.append(f"   - {name}: {mat['price_per_sqm']:.0f}€/m² × {area:.1f}m² = {item_cost:.2f}€")
            lines.append(f"   Итого материалов: {costs['materials']:.2f}€")
        else:
            lines.append("   " + get_text(language, "none_selected"))
        lines.append("")

    if finishing or show_empty:
        lines.append("✨ " + get_text(language, "finishing_cost").rstrip(":") + ":")
        if finishing:
            for f in finishing:
                fin = FINISHINGS[f]
                name = fin.get(f"name_{get_language_code(language)}", fin["name_en"])
                lines.append(f"   - {name}: {fin['price']:.2f}€")
            lines.append(f"   Итого отделка: {costs['finishing']:.2f}€")
        else:
            lines.append("   " + get_text(language, "none_selected"))
        lines.append("")

    if equipment or show_empty:
        lines.append("⚙️ " + get_text(language, "equipment_cost").rstrip(":") + ":")
        if equipment:
            for e in equipment:
                eq = EQUIPMENT[e]
                name = eq.get(f"name_{get_language_code(language)}", eq["name_en"])
                lines.append(f"   - {name}: {eq['price']:.2f}€")
            lines.append(f"   Итого оборудование: {costs['equipment']:.2f}€")
        else:
            lines.append("   " + get_text(language, "none_selected"))
        lines.append("")

    if services or show_empty:
        lines.append("🛠️ " + get_text(language, "services_cost").rstrip(":") + ":")
        if services:
            for s in services:
                serv = SERVICES[s]
                name = serv.get(f"name_{get_language_code(language)}", serv["name_en"])
                lines.append(f"   - {name}: {serv['price']:.2f}€")
            lines.append(f"   Итого услуги: {costs['services']:.2f}€")
        else:
            lines.append("   " + get_text(language, "none_selected"))
        lines.append("")

    lines.append(get_text(language, "total_price", total=f"{costs['total']:.2f}"))
    return "\n".join(lines)


# ============================================================================
# HANDLERS (MODIFIED WHERE NECESSARY)
# ============================================================================

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ConfigurationStates.selecting_language)
    await message.answer(
        "Выберите язык / Select language / Izvēlieties valodu:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        language = callback.data.split("_")[1]
        logger.info(f"Selected language: {language}")
        await state.update_data(language=language)
        
        welcome_text = get_text(language, "welcome")
        kb = get_start_keyboard(language)
        
        try:
            await add_user(
                callback.from_user.id, 
                callback.from_user.username, 
                callback.from_user.full_name, 
                language
            )
            logger.info("User saved to DB")
        except Exception as db_e:
            logger.error(f"DB error: {db_e}", exc_info=True)
        
        await callback.message.edit_text(
            welcome_text,
            reply_markup=kb
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in select_language: {e}", exc_info=True)
        try:
            await callback.answer("Error occurred. Please try again.", show_alert=True)
        except:
            pass

@router.callback_query(F.data == "view_support")
async def view_support(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    support_text = get_text(language, "support_title") + "\n\n" + get_text(language, "support_text", contact=SUPPORT_CONTACT)
    
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, "main_menu"), callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(support_text, reply_markup=back_kb)
    await callback.answer()

@router.callback_query(F.data == "start_config")
async def start_config(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_length)
    await callback.message.edit_text(get_text(language, "step_length"), reply_markup=get_length_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("length_"))
async def select_length(callback: CallbackQuery, state: FSMContext) -> None:
    length = float(callback.data.split("_")[1])
    await state.update_data(length=length)
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_width)
    summary = get_text(language, "selected_length", length=length) + "\n\n" + get_text(language, "step_width")
    await callback.message.edit_text(summary, reply_markup=get_width_keyboard(language, length))
    await callback.answer()

@router.callback_query(F.data == "custom_length")
async def custom_length(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.entering_length)
    await callback.message.edit_text(get_text(language, "enter_length_custom", min=MIN_DIM, max=MAX_DIM))
    await callback.answer()

@router.message(ConfigurationStates.entering_length)
async def handle_custom_length(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    try:
        text = message.text.replace(',', '.')
        length = float(text)
        if MIN_DIM <= length <= MAX_DIM:
            await state.update_data(length=length)
            await state.set_state(ConfigurationStates.choosing_width)
            summary = get_text(language, "selected_length", length=length) + "\n\n" + get_text(language, "step_width")
            await message.answer(summary, reply_markup=get_width_keyboard(language, length))
        else:
            await message.answer(get_text(language, "invalid_dimension", min=MIN_DIM, max=MAX_DIM))
    except ValueError:
        await message.answer(get_text(language, "invalid_dimension", min=MIN_DIM, max=MAX_DIM))

@router.callback_query(F.data == "custom_width")
async def custom_width(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.entering_width)
    await callback.message.edit_text(get_text(language, "enter_width_custom", min=MIN_DIM, max=MAX_DIM))
    await callback.answer()

@router.message(ConfigurationStates.entering_width)
async def handle_custom_width(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    try:
        text = message.text.replace(',', '.')
        width = float(text)
        if MIN_DIM <= width <= MAX_DIM:
            if length * width <= MAX_AREA:
                await state.update_data(width=width)
                await state.set_state(ConfigurationStates.choosing_layout)
                summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=length*width) + "\n\n" + get_text(language, "layout_selection")
                await message.answer(summary, reply_markup=get_layout_keyboard(language))
            else:
                await message.answer(get_text(language, "invalid_area", max_area=MAX_AREA))
        else:
            await message.answer(get_text(language, "invalid_dimension", min=MIN_DIM, max=MAX_DIM))
    except ValueError:
        await message.answer(get_text(language, "invalid_dimension", min=MIN_DIM, max=MAX_DIM))

@router.callback_query(F.data.startswith("width_"))
async def select_width(callback: CallbackQuery, state: FSMContext) -> None:
    width = float(callback.data.split("_")[1])
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    
    if length * width > MAX_AREA:
        await callback.answer(get_text(language, "invalid_area", max_area=MAX_AREA), show_alert=True)
        return
    
    await state.update_data(width=width)
    await state.set_state(ConfigurationStates.choosing_layout)
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=length*width) + "\n\n" + get_text(language, "layout_selection")
    await callback.message.edit_text(summary, reply_markup=get_layout_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("layout_"))
async def select_layout(callback: CallbackQuery, state: FSMContext) -> None:
    layout_type = callback.data.split("_")[1]
    await state.update_data(layout_type=layout_type)
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_construction_type)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_name = LAYOUTS[layout_type].get(f"name_{get_language_code(language)}", LAYOUTS[layout_type]["name_en"])
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=length*width) + "\n" + get_text(language, "selected_layout", layout=layout_name) + "\n\n" + get_text(language, "step_construction")
    await callback.message.edit_text(summary, reply_markup=get_construction_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("construction_"))
async def select_construction(callback: CallbackQuery, state: FSMContext) -> None:
    construction_type = callback.data.split("_")[1]
    await state.update_data(construction_type=construction_type)
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_materials)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    layout_name = LAYOUTS[layout_type].get(f"name_{get_language_code(language)}", LAYOUTS[layout_type]["name_en"])
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{get_language_code(language)}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=length*width) + "\n" + get_text(language, "selected_layout", layout=layout_name) + "\n" + get_text(language, "selected_construction", construction=construction_name) + "\n\n" + get_text(language, "step_materials")
    await callback.message.edit_text(summary, reply_markup=get_materials_keyboard(language, materials))
    await callback.answer()

@router.callback_query(F.data.startswith("material_"))
async def toggle_material(callback: CallbackQuery, state: FSMContext) -> None:
    material = callback.data.split("_")[1]
    data = await state.get_data()
    materials = data.get("materials", [])
    if material in materials:
        materials.remove(material)
    else:
        materials.append(material)
    await state.update_data(materials=materials)
    language = data.get("language", "EN")

    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])

    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, services, show_empty=False)
    await callback.message.edit_text(summary, reply_markup=get_materials_keyboard(language, materials))
    await callback.answer()

@router.callback_query(F.data == "materials_done")
async def materials_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_finishing)
    
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])
    
    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, services, show_empty=False)
    summary += "\n\n" + get_text(language, "finishing_selection")
    await callback.message.edit_text(summary, reply_markup=get_finishing_keyboard(language, finishing))
    await callback.answer()

@router.callback_query(F.data.startswith("finishing_") & (F.data != "finishing_done"))
async def toggle_finishing(callback: CallbackQuery, state: FSMContext) -> None:
    finishing = callback.data.split("_")[1]
    if finishing == "done":
        await callback.answer()
        return
    data = await state.get_data()
    finishings = data.get("finishing", [])
    if finishing in finishings:
        finishings.remove(finishing)
    else:
        finishings.append(finishing)
    await state.update_data(finishing=finishings)
    language = data.get("language", "EN")

    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])

    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishings, equipment, services, show_empty=False)
    await callback.message.edit_text(summary, reply_markup=get_finishing_keyboard(language, finishings))
    await callback.answer()

@router.callback_query(F.data == "finishing_done")
async def finishing_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_equipment)
    
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])
    
    costs = calculate_cost(length, width, construction_type, layout_type, materials, finishing, equipment, services)
    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, services, show_empty=False)
    summary += "\n\n" + get_text(language, "step_equipment")
    await callback.message.edit_text(summary, reply_markup=get_equipment_keyboard(language, equipment))
    await callback.answer()

@router.callback_query(F.data == "confirm_order_from_finishing")
async def confirm_order_from_finishing(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.confirmation)
    
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])
    
    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, services, show_empty=True)
    summary += "\n\n" + get_text(language, "what_next")
    await callback.message.edit_text(summary, reply_markup=get_post_calculation_keyboard(language))
    await callback.answer()

@router.callback_query(F.data.startswith("equipment_") & (F.data != "equipment_done"))
async def toggle_equipment(callback: CallbackQuery, state: FSMContext) -> None:
    equipment = callback.data.split("_")[1]
    if equipment == "done":
        await callback.answer()
        return
    data = await state.get_data()
    equipments = data.get("equipment", [])
    if equipment in equipments:
        equipments.remove(equipment)
    else:
        equipments.append(equipment)
    await state.update_data(equipment=equipments)
    language = data.get("language", "EN")

    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    services = data.get("services", [])

    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipments, services, show_empty=False)
    await callback.message.edit_text(summary, reply_markup=get_equipment_keyboard(language, equipments))
    await callback.answer()

@router.callback_query(F.data == "equipment_done")
async def equipment_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_services)
    
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])
    
    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, services, show_empty=False)
    summary += "\n\n" + get_text(language, "services_selection")
    await callback.message.edit_text(summary, reply_markup=get_services_keyboard(language, services))
    await callback.answer()

@router.callback_query(F.data.startswith("service_"))
async def toggle_service(callback: CallbackQuery, state: FSMContext) -> None:
    service = callback.data.split("_")[1]
    data = await state.get_data()
    services = data.get("services", [])
    if service in services:
        services.remove(service)
    else:
        services.append(service)
    await state.update_data(services=services)
    language = data.get("language", "EN")

    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])

    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, services, show_empty=False)
    await callback.message.edit_text(summary, reply_markup=get_services_keyboard(language, services))
    await callback.answer()

@router.callback_query(F.data == "services_done")
async def services_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.confirmation)
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])
    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, services, show_empty=True)
    summary += "\n\n" + get_text(language, "what_next")
    await callback.message.edit_text(summary, reply_markup=get_post_calculation_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "demo_payment")
async def demo_payment(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    
    order_id = int(datetime.datetime.now().timestamp())
    await state.update_data(order_id=order_id)
    
    msg = get_text(language, "payment_success", order_id=order_id)
    await callback.message.edit_text(msg, reply_markup=get_post_calculation_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "book_consultation")
async def book_consultation(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.entering_phone)
    await callback.message.edit_text(get_text(language, "enter_phone"))
    await callback.answer()

@router.message(ConfigurationStates.entering_phone)
async def handle_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text)
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.entering_email)
    await message.answer(get_text(language, "enter_email"))

@router.message(ConfigurationStates.entering_email)
async def handle_email(message: Message, state: FSMContext) -> None:
    await state.update_data(email=message.text)
    data = await state.get_data()
    language = data.get("language", "EN")
    
    phone = data.get("phone", "")
    email = message.text
    
    msg = get_text(language, "consultation_booked")
    await message.answer(msg, reply_markup=get_post_calculation_keyboard(language))
    
    if ADMIN_ID:
        admin_msg = f"📅 New consultation booking:\nPhone: {phone}\nEmail: {email}"
        try:
            await bot.send_message(ADMIN_ID, admin_msg)
        except:
            pass

@router.message()
async def catch_all(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "EN")
    await message.answer(get_text(language, "press_button"))

@router.callback_query(F.data == "download_quote")
async def download_quote(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    construction_type = data.get("construction_type", "standard")
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    services = data.get("services", [])
    
    order_data = {
        "order_id": data.get("order_id", int(datetime.datetime.now().timestamp())),
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "length": length,
        "width": width,
        "layout_name": LAYOUTS.get(layout_type, LAYOUTS["standard"]).get(f"name_{get_language_code(language)}", LAYOUTS["standard"]["name_en"]),
        "construction_name": CONSTRUCTION_TYPES.get(construction_type, CONSTRUCTION_TYPES["standard"]).get(f"name_{get_language_code(language)}", CONSTRUCTION_TYPES["standard"]["name_en"]),
        "materials_names": [MATERIALS[m].get(f"name_{get_language_code(language)}", MATERIALS[m]["name_en"]) for m in materials if m in MATERIALS],
        "finishing_names": [FINISHINGS[f].get(f"name_{get_language_code(language)}", FINISHINGS[f]["name_en"]) for f in finishing if f in FINISHINGS],
        "equipment_names": [EQUIPMENT[e].get(f"name_{get_language_code(language)}", EQUIPMENT[e]["name_en"]) for e in equipment if e in EQUIPMENT],
        "services_names": [SERVICES[s].get(f"name_{get_language_code(language)}", SERVICES[s]["name_en"]) for s in services if s in SERVICES],
        "total_price": calculate_cost(length, width, construction_type, layout_type, materials, finishing, equipment, services)["total"]
    }
    
    pdf_filename = os.path.abspath(f"quote_{callback.from_user.id}_{order_data['order_id']}.pdf")
    try:
        generate_order_pdf(order_data, pdf_filename)
        pdf_file = FSInputFile(pdf_filename)
        await callback.message.answer_document(pdf_file, caption="📄 Your booth configuration quote")
        with suppress(Exception):
            os.remove(pdf_filename)
    except Exception as e:
        logger.error("Error generating PDF", exc_info=True)
        await callback.message.answer("❌ Error generating PDF. Please try again.")
    
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.clear()
    await state.update_data(language=language)
    await callback.message.edit_text(get_text(language, "welcome"), reply_markup=get_start_keyboard(language))
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await message.answer(get_text(language, "help"), reply_markup=get_start_keyboard(language))

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.clear()
    await state.update_data(language=language)
    await message.answer(get_text(language, "canceled"), reply_markup=get_start_keyboard(language))

@router.message(Command("my_orders"))
async def cmd_my_orders(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer(get_text(language, "no_orders"))
        return

    await message.answer(get_text(language, "order_history"))
    for order in orders[:10]:
        summary = f"ID: {order[0]} | {order[11]}\nSize: {order[2]}x{order[3]}m | Total: {order[10]:.2f}€"
        await message.answer(summary)

@router.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    
    if message.from_user.id == ADMIN_ID:
        stats = await get_order_stats()
        msg = f"📈 Orders in last 24h: {stats.get('today_count', 0)} ({stats.get('today_total', 0):.2f}€)\nOrders in last 7 days: {stats.get('week_count', 0)} ({stats.get('week_total', 0):.2f}€)\nTotal: {stats.get('total_count', 0)} ({stats.get('total_sum', 0):.2f}€)"
        await message.answer(msg)
    else:
        stats = await get_user_order_stats(message.from_user.id)
        msg = f"📊 Your orders: {stats.get('count', 0)}\nTotal spent: {stats.get('total', 0):.2f}€"
        await message.answer(msg)

# Back buttons (unchanged but kept for completeness)
@router.callback_query(F.data == "back_to_length")
async def back_to_length(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    await state.set_state(ConfigurationStates.choosing_length)
    await callback.message.edit_text(get_text(language, "step_length"), reply_markup=get_length_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_width")
async def back_to_width(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    await state.set_state(ConfigurationStates.choosing_width)
    summary = get_text(language, "selected_length", length=length) + "\n\n" + get_text(language, "step_width")
    await callback.message.edit_text(summary, reply_markup=get_width_keyboard(language, length))
    await callback.answer()

@router.callback_query(F.data == "back_to_layout")
async def back_to_layout(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    await state.set_state(ConfigurationStates.choosing_layout)
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=length*width) + "\n\n" + get_text(language, "layout_selection")
    await callback.message.edit_text(summary, reply_markup=get_layout_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_construction")
async def back_to_construction(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    layout_name = LAYOUTS[layout_type].get(f"name_{get_language_code(language)}", LAYOUTS[layout_type]["name_en"])
    await state.set_state(ConfigurationStates.choosing_construction_type)
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=length*width) + "\n" + get_text(language, "selected_layout", layout=layout_name) + "\n\n" + get_text(language, "step_construction")
    await callback.message.edit_text(summary, reply_markup=get_construction_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "back_to_materials")
async def back_to_materials(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    layout_name = LAYOUTS[layout_type].get(f"name_{get_language_code(language)}", LAYOUTS[layout_type]["name_en"])
    construction_type = data.get("construction_type", "standard")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{get_language_code(language)}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    await state.set_state(ConfigurationStates.choosing_materials)
    summary = get_text(language, "selected_length", length=length) + "\n" + get_text(language, "selected_width", width=width) + "\n" + get_text(language, "selected_area", area=length*width) + "\n" + get_text(language, "selected_layout", layout=layout_name) + "\n" + get_text(language, "selected_construction", construction=construction_name) + "\n\n" + get_text(language, "step_materials")
    await callback.message.edit_text(summary, reply_markup=get_materials_keyboard(language, materials))
    await callback.answer()

@router.callback_query(F.data == "back_to_finishing")
async def back_to_finishing(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    layout_name = LAYOUTS[layout_type].get(f"name_{get_language_code(language)}", LAYOUTS[layout_type]["name_en"])
    construction_type = data.get("construction_type", "standard")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{get_language_code(language)}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    await state.set_state(ConfigurationStates.choosing_finishing)
    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, [], [])
    summary += "\n\n" + get_text(language, "finishing_selection")
    await callback.message.edit_text(summary, reply_markup=get_finishing_keyboard(language, finishing))
    await callback.answer()

@router.callback_query(F.data == "back_to_equipment")
async def back_to_equipment(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    language = data.get("language", "EN")
    length = data.get("length", 2.0)
    width = data.get("width", 2.0)
    layout_type = data.get("layout_type", "standard")
    layout_name = LAYOUTS[layout_type].get(f"name_{get_language_code(language)}", LAYOUTS[layout_type]["name_en"])
    construction_type = data.get("construction_type", "standard")
    construction_name = CONSTRUCTION_TYPES[construction_type].get(f"name_{get_language_code(language)}", CONSTRUCTION_TYPES[construction_type]["name_en"])
    materials = data.get("materials", [])
    finishing = data.get("finishing", [])
    equipment = data.get("equipment", [])
    await state.set_state(ConfigurationStates.choosing_equipment)
    summary = format_cost_summary(language, length, width, layout_type, construction_type,
                                  materials, finishing, equipment, [])
    summary += "\n\n" + get_text(language, "step_equipment")
    await callback.message.edit_text(summary, reply_markup=get_equipment_keyboard(language, equipment))
    await callback.answer()

async def main() -> None:
    await init_db()
    dp.include_router(router)
    try:
        logger.info("🤖 BOT IS RUNNING AND READY TO WORK...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
