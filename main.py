import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import google.generativeai as genai
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

# Sozlamalar
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Bot
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Render uchun kichik veb-server ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render beradigan PORTni ishlatamiz, bo'lmasa 10000
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

# --- Bot funksiyalari ---
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Salom! Men Render-da bepul ishlaydigan AI botman.")

@dp.message()
async def chat(message: Message):
    try:
        response = model.generate_content(f"O'zbek tilida javob ber: {message.text}")
        await message.answer(response.text)
    except Exception as e:
        await message.answer(f"Xatolik: {str(e)}")

async def main():
    # Bir vaqtda ham veb-serverni, ham botni ishga tushiramiz
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    
