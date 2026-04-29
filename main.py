import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import google.generativeai as genai
from aiohttp import web

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokenlarni olish (Render Environment Variables'dan)
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Bot va Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Render uchun majburiy Veb-Server ---
async def handle(request):
    return web.Response(text="AI Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on port {port}")

# --- Bot buyruqlari ---
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("✨ Salom! Men Render-da ishlaydigan AI yordamchingizman. Savolingizni yozing!")

@dp.message()
async def chat(message: Message):
    try:
        # Gemini-dan javob olish
        response = model.generate_content(f"Javobni o'zbek tilida ber: {message.text}")
        await message.answer(response.text)
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await message.answer("Kechirasiz, hozirda javob bera olmayman. API kalitini tekshiring.")

async def main():
    # Veb-server va Botni birga ishga tushirish
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
        
