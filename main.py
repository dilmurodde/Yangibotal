import os
import logging
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# .env faylidan ma'lumotlarni yuklash
load_dotenv()

# Loggingni sozlash
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tokenlarni olish
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini AI ni sozlash
genai.configure(api_key=GEMINI_API_KEY)

# Bot va Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ishlaydigan modelni aniqlash funksiyasi
def get_model():
    try:
        # Mavjud modellarni tekshirish
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_methods]
        logger.info(f"Mavjud modellar: {models}")
        
        # Eng yaxshi modelni tanlash
        for m in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if m in models:
                logger.info(f"Tanlangan model: {m}")
                return genai.GenerativeModel(m)
        
        return genai.GenerativeModel(models[0])
    except Exception as e:
        logger.error(f"Model aniqlashda xato: {e}")
        return genai.GenerativeModel('gemini-1.5-flash')

# Modelni yuklash
ai_model = get_model()

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "✨ **Salom! Men mukammal AI yordamchingizman.**\n\n"
        "Men Google Gemini 1.5 Flash texnologiyasi asosida ishlayman.\n"
        "Sizga kod yozishda, g'oyalarni amalga oshirishda va har qanday savollarga javob berishda yordam bera olaman.\n\n"
        "💬 **Nima yordam kerak? Shunchaki yozing!**",
        parse_mode="Markdown"
    )

@dp.message()
async def handle_message(message: Message):
    # Foydalanuvchiga kutish xabarini ko'rsatish
    status_msg = await message.answer("🔍 *O'ylayapman...*", parse_mode="Markdown")
    
    try:
        # AI dan javob olish
        prompt = f"Sen aqlli dasturchi va yordamchisan. Javoblarni o'zbek tilida ber. So'rov: {message.text}"
        response = ai_model.generate_content(prompt)
        
        # Javobni yuborish (uzun bo'lsa bo'lib yuboradi)
        text = response.text
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                await message.answer(text[i:i+4000])
            await status_msg.delete()
        else:
            await status_msg.edit_text(text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await status_msg.edit_text(f"❌ **Xatolik yuz berdi.**\n\nTexnik xabar: `{str(e)}`", parse_mode="Markdown")

async def main():
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                                  
