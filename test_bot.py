"""
Minimal test bot to diagnose issues
"""
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Load environment
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class States(StatesGroup):
    choosing_lang = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"START command from {message.from_user.id}")
    await state.clear()
    await state.set_state(States.choosing_lang)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_EN")],
        [InlineKeyboardButton(text="🇷🇺 Russian", callback_data="lang_RUS")],
    ])
    await message.answer("Choose language:", reply_markup=kb)

@router.callback_query(F.data.startswith("lang_"))
async def select_lang(callback: CallbackQuery, state: FSMContext):
    logger.info(f"SELECT_LANG callback from {callback.from_user.id}")
    try:
        lang = callback.data.split("_")[1]
        logger.info(f"Selected language: {lang}")
        await state.update_data(language=lang)
        await callback.message.edit_text(f"✅ Language selected: {lang}")
        await callback.answer()
    except Exception as e:
        logger.error(f"ERROR in select_lang: {e}", exc_info=True)
        await callback.answer("Error!", show_alert=True)

async def main():
    logger.info("Bot starting...")
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
