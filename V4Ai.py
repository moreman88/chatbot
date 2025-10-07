"""
Telegram-бот для Карагандинского колледжа технологий и сервиса
Версия: 1.1 (с поддержкой Gemini)
"""

import asyncio
import logging
import ssl
import os
import google.generativeai as genai
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

# ---------------------------------------
# SSL обход для Python из Microsoft Store
# ---------------------------------------
ssl._create_default_https_context = ssl._create_unverified_context

# ---------------------------------------
# Настройка Gemini
# ---------------------------------------
os.environ["GOOGLE_API_KEY"] = "AIzaSyBSeT4fCI0wphjsujGkfFJ9VkexhUiKveE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = (
    "Ты — виртуальный помощник Карагандинского колледжа технологий и сервиса (ККТиС). "
    "Отвечай только на вопросы, связанные с колледжем, образованием, приёмом, расписанием, "
    "специальностями, контактами и студенческой жизнью. "
    "Если вопрос не касается колледжа или образования — вежливо откажись отвечать, "
    "например: «Извините, я могу отвечать только на вопросы, связанные с колледжем ККТиС.» "
    "Отвечай дружелюбно, кратко и информативно."
)

# ---------------------------------------
# Настройка логирования
# ---------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------
# Константы
# ---------------------------------------
BOT_TOKEN = "8407576281:AAF0lofeJQxBxsxEoYrMimB4ACAtVVyHN9w"

COLLEGE_NAME = "Карагандинский колледж технологий и сервиса"
SCHEDULE_URL = "https://docs.google.com/spreadsheets/d/1F82YExVeyvm0CPNuMfVYBxLPzX17p_iz/edit?usp=sharing&ouid=112502196767433801385&rtpof=true&sd=true"
SITE_URL = "https://kktis.kz"

# ---------------------------------------
# Инициализация бота
# ---------------------------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 Расписание"),
                KeyboardButton(text="🎓 Приёмная комиссия")
            ],
            [KeyboardButton(text="📞 Контакты")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел..."
    )
    return keyboard


# ---------------------------------------
# Команда /start
# ---------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        f"🎓 <b>{COLLEGE_NAME}</b>\n\n"
        f"👋 Здравствуйте, <b>{message.from_user.first_name}</b>!\n"
        f"Я помогу вам найти нужную информацию:\n\n"
        f"📅 Расписание\n"
        f"🎓 Приёмная комиссия\n"
        f"📞 Контакты\n\n"
        f"👇 Выберите раздел ниже:"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)


# ---------------------------------------
# Расписание
# ---------------------------------------
@dp.message(F.text == "📅 Расписание")
async def show_schedule(message: Message):
    await message.answer(
        f"📚 Расписание доступно по ссылке:\n🔗 <a href='{SCHEDULE_URL}'>Открыть расписание</a>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


# ---------------------------------------
# Контакты
# ---------------------------------------
@dp.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    contacts_text = (
        f"📍 Караганда, ул. Затаевича, 75\n"
        f"☎️ 8-7212-37-58-44\n"
        f"✉️ krg-koll-7092@bilim09.kzu.kz\n"
        f"🌐 {SITE_URL}"
    )
    await message.answer(contacts_text, parse_mode=ParseMode.HTML)


# ---------------------------------------
# Приёмная комиссия
# ---------------------------------------
@dp.message(F.text == "🎓 Приёмная комиссия")
async def show_admission(message: Message):
    await message.answer("📋 Информация о приёме и специальностях доступна на сайте: https://kktis.kz", parse_mode=ParseMode.HTML)


# ---------------------------------------
# AI-Ответы (Gemini)
# ---------------------------------------
@dp.message()
async def handle_ai_chat(message: Message):
    """Все остальные запросы — через Gemini"""
    user_text = message.text.strip()

    try:
        prompt = f"{SYSTEM_PROMPT}\n\nПользователь: {user_text}"
        response = model.generate_content(prompt)
        ai_reply = response.text if response and response.text else "⚠️ Не удалось получить ответ от ИИ."
    except Exception as e:
        ai_reply = f"🚫 Ошибка при обращении к ИИ: {e}"

    await message.answer(ai_reply)


# ---------------------------------------
# Основная функция запуска
# ---------------------------------------
async def main():
    logger.info(f"🚀 Запуск бота {COLLEGE_NAME}")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
