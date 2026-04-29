import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
from aiohttp import web

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokenlarni olish
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)

# Bot va Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ishlaydigan modelni avtomatik aniqlash
def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_methods]
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if preferred in available_models:
                return genai.GenerativeModel(preferred)
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        logger.error(f"Model aniqlashda xato: {e}")
    return genai.GenerativeModel('gemini-1.5-flash')

ai_model = get_working_model()

# --- Render uchun Veb-Server ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- Bot buyruqlari ---
@dp.message(Command("start"))
async def start(message: Message):
    # Admin tugmasini yaratish
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💻 Admin bilan bog'lanish", url="https://t.me/dilmurod9831")]
    ])
    
    start_text = (
        "✨ **Salom! Men mukammal AI yordamchingizman.**\n\n"
        "Men Google Gemini 1.5 Flash texnologiyasi asosida ishlayman.\n"
        "Sizga kod yozishda, g'oyalarni amalga oshirishda va har qanday savollarga javob berishda yordam bera olaman.\n\n"
        "👤 **Admin:** @dilmurod9831\n\n"
        "💬 **Nima yordam kerak? Shunchaki yozing!**"
    )
    
    await message.answer(start_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.message()
async def chat(message: Message):
    msg = await message.answer("🔍 O'ylayapman...")
    try:
        response = ai_model.generate_content(f"Javobni o'zbek tilida ber: {message.text}")
        await msg.edit_text(response.text)
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await msg.edit_text(f"❌ Xatolik yuz berdi:\n`{str(e)}`", parse_mode="Markdown")

async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
    
