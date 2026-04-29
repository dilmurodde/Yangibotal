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

# --- Ishlaydigan modelni topish funksiyasi ---
def find_working_model():
    try:
        # API kalitga ruxsat berilgan barcha modellarni olish
        models = genai.list_models()
        for m in models:
            # Faqat matn yarata oladigan modellarni qidiramiz
            if 'generateContent' in m.supported_methods:
                logger.info(f"Ishlaydigan model topildi: {m.name}")
                return genai.GenerativeModel(m.name)
    except Exception as e:
        logger.error(f"Modellarni sanashda xato: {e}")
    # Agar hech narsa topilmasa, standart nomni qaytaramiz
    return genai.GenerativeModel('gemini-pro')

# Modelni bir marta aniqlab olamiz
ai_model = find_working_model()

# --- Bot buyruqlari ---
@dp.message(Command("start"))
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💻 Admin bilan bog'lanish", url="https://t.me/dilmurod9831")]
    ])
    
    start_text = (
        "✨ **Salom! Men mukammal Dilmurod AI yordamchingizman.**\n\n"
        "Men Dilmurod AI texnologiyasi asosida ishlayman.\n"
        "Sizga kod yozishda, g'oyalarni amalga oshirishda va har qanday savollarga javob berishda yordam bera olaman.\n\n"
        "👤 **Admin:** @dilmurod9831\n\n"
        "💬 **Nima yordam kerak? Shunchaki yozing!**"
    )
    await message.answer(start_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.message()
async def chat(message: Message):
    msg = await message.answer("🔍 O'ylayapman...")
    try:
        # AI dan javob olish
        response = ai_model.generate_content(f"Javobni o'zbek tilida ber: {message.text}")
        
        if response.text:
            await msg.edit_text(response.text)
        else:
            await msg.edit_text("Kechirasiz, AI javob qaytara olmadi.")
            
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        # Agar xatolik bo'lsa, modelni qayta aniqlashga harakat qilamiz
        try:

async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
    
