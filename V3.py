"""
Telegram-бот для Карагандинского колледжа технологий и сервиса
Версия: 1.0 (базовый функционал)
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

import google.generativeai as genai
import os

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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (получите у @BotFather)
BOT_TOKEN = "8407576281:AAF0lofeJQxBxsxEoYrMimB4ACAtVVyHN9w"

# Константы с контактной информацией
COLLEGE_NAME = "Карагандинский колледж технологий и сервиса"
SCHEDULE_URL = "https://docs.google.com/spreadsheets/d/1F82YExVeyvm0CPNuMfVYBxLPzX17p_iz/edit?usp=sharing&ouid=112502196767433801385&rtpof=true&sd=true"
SITE_URL = "https://kktis.kz"
CONTACTS_INFO = """📍 <b>Адрес:</b> Караганда, ул. Затаевича, 75
☎️ <b>Телефон:</b> 8-7212-37-58-44
✉️ <b>Email:</b> krg-koll-7092@bilim09.kzu.kz"""

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создаёт главное меню с кнопками
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 Расписание"),
                KeyboardButton(text="🎓 Приёмная комиссия")
            ],
            [
                KeyboardButton(text="📞 Контакты")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел..."
    )
    return keyboard


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    Приветствует пользователя и показывает возможности бота
    """
    welcome_text = (
        f"╔═══════════════════════╗\n"
        f"   🎓 <b>{COLLEGE_NAME}</b> 🎓\n"
        f"╚═══════════════════════╝\n\n"
        f"👋 Здравствуйте, <b>{message.from_user.first_name}</b>!\n\n"
        f"Я — официальный бот колледжа, и я помогу вам быстро найти нужную информацию:\n\n"
        f"┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃ 📅 <b>Расписание</b>\n"
        f"┃    Актуальное расписание\n"
        f"┃    занятий всех групп\n"
        f"┃\n"
        f"┃ 📞 <b>Контакты</b>\n"
        f"┃    Адрес, телефоны и\n"
        f"┃    способы связи с колледжем\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👇 <i>Выберите нужный раздел в меню</i>"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode=ParseMode.HTML
    )


@dp.message(F.text == "📅 Расписание")
async def show_schedule(message: Message):
    """
    Обработчик кнопки "Расписание"
    Отправляет ссылку на расписание занятий в Google Таблицах
    """
    schedule_text = (
        f"╔═══════════════════════╗\n"
        f"     📅 <b>РАСПИСАНИЕ ЗАНЯТИЙ</b>\n"
        f"╚═══════════════════════╝\n\n"
        f"📚 Актуальное расписание всех групп и преподавателей доступно в Google Таблицах:\n\n"
        f"🔗 <a href='{SCHEDULE_URL}'>Открыть расписание</a>\n\n"
        f"┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃ ℹ️ <b>Полезная информация:</b>\n"
        f"┃\n"
        f"┃ • Расписание обновляется\n"
        f"┃   регулярно\n"
        f"┃ • Вы можете сохранить\n"
        f"┃   ссылку для быстрого\n"
        f"┃   доступа\n"
        f"┃ • Расписание доступно\n"
        f"┃   на любом устройстве\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"🌐 Официальный сайт: {SITE_URL}"
    )
    
    await message.answer(
        schedule_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


@dp.message(F.text == "📞 Контакты")
async def show_contacts(message: Message):
    """
    Обработчик кнопки "Контакты"
    Отправляет контактную информацию колледжа
    """
    contacts_text = (
        f"╔═══════════════════════╗\n"
        f"      📞 <b>КОНТАКТНАЯ ИНФОРМАЦИЯ</b>\n"
        f"╚═══════════════════════╝\n\n"
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃ 📍 <b>Адрес:</b>\n"
        f"┃    Караганда, ул. Затаевича, 75\n"
        f"┃\n"
        f"┃ ☎️ <b>Телефон:</b>\n"
        f"┃    8-7212-37-58-44\n"
        f"┃\n"
        f"┃ ✉️ <b>Email:</b>\n"
        f"┃    krg-koll-7092@bilim09.kzu.kz\n"
        f"┃\n"
        f"┃ 🌐 <b>Веб-сайт:</b>\n"
        f"┃    {SITE_URL}\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"⏰ <b>Режим работы:</b>\n"
        f"Понедельник - Пятница: 8:00 - 17:00\n"
        f"Суббота - Воскресенье: Выходной\n\n"
        f"💬 Мы всегда рады ответить на ваши вопросы!"
    )

    await message.answer(
        contacts_text,
        parse_mode=ParseMode.HTML
    )


@dp.message(F.text == "🎓 Приёмная комиссия")
async def show_admission(message: Message):
    """
    Обработчик кнопки "Приёмная комиссия"
    Отправляет информацию о поступлении и специальностях
    """
    # Первое сообщение - специальности
    await message.answer(
        specialties_text := (
            f"╔═══════════════════════╗\n"
            f"   🎓 <b>ПРИЁМНАЯ КОМИССИЯ</b>\n"
            f"╚═══════════════════════╝\n\n"
            f"<b>КГКП «Карагандинский колледж технологии и сервиса» осуществляет набор студентов на новый учебный год по следующим специальностям:</b>\n\n"
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃ 💻 <b>ЦИФРОВАЯ ТЕХНИКА</b>\n"
            f"┃    (целевая группа)\n"
            f"┃    • На базе 11 кл. - 10 месяцев\n"
            f"┃\n"
            f"┃ ✂️ <b>ПАРИКМАХЕРСКОЕ ИСКУССТВО</b>\n"
            f"┃    • На базе 9 кл. - 2г. 10 мес.\n"
            f"┃    • На базе ТиПО - 10 мес.\n"
            f"┃\n"
            f"┃ 👗 <b>ШВЕЙНОЕ ПРОИЗВОДСТВО И</b>\n"
            f"┃    <b>МОДЕЛИРОВАНИЕ ОДЕЖДЫ</b>\n"
            f"┃    • На базе 9 кл. - 2г. 10 мес.\n"
            f"┃    • На базе ТиПО - 10 мес.\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        ),
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        specialties_text_2 := (
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃ 🧵 <b>ПОРТНОЙ</b>\n"
            f"┃    • На базе 9 кл. - 2г. 10 мес.\n"
            f"┃\n"
            f"┃ 👞 <b>ОБУВНОЕ ДЕЛО</b>\n"
            f"┃    • На базе ТиПО - 10 мес.\n"
            f"┃\n"
            f"┃ 💼 <b>ОФИС-МЕНЕДЖЕР</b>\n"
            f"┃    • На базе 11 кл. - 10 мес.\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        ),
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        documents_text := (
            f"╔═══════════════════════╗\n"
            f"   📋 <b>ДОКУМЕНТЫ ДЛЯ ПОСТУПЛЕНИЯ</b>\n"
            f"╚═══════════════════════╝\n\n"
            f"<b>Необходимые документы:</b>\n\n"
            f"1️⃣ Заявление о приеме документов\n\n"
            f"2️⃣ Подлинник документа об образовании\n"
            f"   (аттестат, диплом)\n\n"
            f"3️⃣ Фотографии 3×4 см - 4 штуки\n\n"
            f"4️⃣ Медицинская справка формы № 075У\n\n"
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃ 🌍 <b>Для иностранных граждан</b>\n"
            f"┃    <b>и лиц без гражданства:</b>\n"
            f"┃ • Вид на жительство\n"
            f"┃ • Удостоверение лица без гражданства\n"
            f"┃ • Удостоверение беженца\n"
            f"┃ • Удостоверение кандаса\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        ),
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        submission_text := (
            f"╔═══════════════════════╗\n"
            f"   📤 <b>СПОСОБЫ ПОДАЧИ ДОКУМЕНТОВ</b>\n"
            f"╚═══════════════════════╝\n\n"
            f"1️⃣ Лично в колледже\n"
            f"   📍 г. Караганда, ул. Затаевича, 75\n\n"
            f"2️⃣ Через портал электронного правительства 🌐 www.egov.kz\n\n"
            f"3️⃣ Через платформу My College\n\n"
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃ 📞 <b>ПРИЁМНАЯ КОМИССИЯ</b>\n"
            f"┃ 👤 Әмірханова М.А. — ☎️ 8-701-842-25-36\n"
            f"┃ 👤 Искакова Г.К. — ☎️ 8-700-145-45-36\n"
            f"┃ ⏰ Пн–Пт: 8:00–17:00\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"✅ <b>Результат:</b> Расписка о приеме документов\n\n"
            f"📚 Мы ждём вас в нашем колледже!"
        ),
        parse_mode=ParseMode.HTML
    )
@dp.message()
async def handle_ai_chat(message: Message):
    """
    Универсальный обработчик всех текстов, не попавших в другие команды.
    Отправляет запрос к Gemini и возвращает ответ пользователю.
    """
    user_text = message.text.strip()

    try:
        response = model.generate_content(user_text)
        ai_reply = response.text if response and response.text else "⚠️ Не удалось получить ответ от ИИ."
    except Exception as e:
        ai_reply = f"🚫 Ошибка при обращении к ИИ: {e}"

    await message.answer(ai_reply)

@dp.message()
async def handle_unknown_message(message: Message):
    """
    Обработчик неизвестных сообщений
    Подсказывает пользователю использовать меню
    """
    await message.answer(
        "❓ Я не понял вашего сообщения.\n"
        "Пожалуйста, используйте кнопки меню ниже для навигации.",
        reply_markup=get_main_keyboard()
    )


async def main():
    """
    Основная функция запуска бота
    """
    logger.info(f"Запуск бота для {COLLEGE_NAME}")
    
    # Удаление вебхуков (на случай если были)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

        # Настройка клиента Gemini
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


