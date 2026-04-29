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
    logger.info(f"Veb-server {port}-portda ishga tushdi")

# --- Ishlaydigan modelni tanlash ---
# Hozirda 'gemini-1.5-flash' eng barqaror va deyarli barcha mintaqalarda ishlaydi
MODEL_NAME = 'gemini-1.5-flash'
ai_model = genai.GenerativeModel(MODEL_NAME)

# --- Bot buyruqlari ---
@dp.message(Command("start"))
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💻 Admin bilan bog'lanish", url="https://t.me/dilmurod9831")]
    ])
    
    start_text = (
        "✨ **Salom! Men mukammal AI yordamchingizman.**\n\n"
        "Men Google Gemini AI texnologiyasi asosida ishlayman.\n"
        "Sizga kod yozishda, g'oyalarni amalga oshirishda va har qanday savollarga javob berishda yordam bera olaman.\n\n"
        "💬 **Nima yordam kerak? Shunchaki yozing!**"
    )
    await message.answer(start_text, reply_markup=keyboard, parse_mode="Markdown")

@dp.message()
async def chat(message: Message):
    # Foydalanuvchiga javob kutishini bildirish
    msg = await message.answer("🔍 O'ylayapman...")
    
    try:
        # AI dan javob olish
        # generate_content'ga string yuborish kifoya
        response = ai_model.generate_content(f"Javobni o'zbek tilida ber: {message.text}")
        
        if response and response.text:
            # Telegram xabar uzunligi chegarasi (4096 belgi)
            full_text = response.text
            if len(full_text) > 4000:
                full_text = full_text[:4000] + "..."
            
            await msg.edit_text(full_text)
        else:
            await msg.edit_text("Kechirasiz, AI javob qaytara olmadi (bo'sh javob).")
            
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        error_message = str(e)
        
        if "404" in error_message:
            await msg.edit_text("❌ Model topilmadi. Admin model nomini yangilashi kerak.")
        elif "429" in error_message:
            await msg.edit_text("⚠️ Juda ko'p so'rov yuborildi. Birozdan keyin urinib ko'ring.")
        else:
            await msg.edit_text(f"❌ Xatolik yuz berdi:\n`{error_message[:200]}`", parse_mode="Markdown")

async def main():
    # Bir vaqtning o'zida ham serverni, ham botni ishga tushirish
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi")
        
