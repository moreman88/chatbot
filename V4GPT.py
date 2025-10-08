import os
import logging
import asyncio
import requests
import google.generativeai as genai
from openai import OpenAI
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties

# 🔧 --- НАСТРОЙКИ ---
BOT_TOKEN = "8407576281:AAF0lofeJQxBxsxEoYrMimB4ACAtVVyHN9w"
OPENAI_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyBSeT4fCI0wphjsujGkfFJ9VkexhUiKveE"
OPENROUTER_KEY = "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"

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


# --- Логирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация бота ---
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# --- Инициализация OpenAI клиента ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- СИСТЕМНАЯ ИНСТРУКЦИЯ ДЛЯ ИИ ---
COLLEGE_RULES = (
    "Ты — виртуальный помощник Карагандинского колледжа технологий и сервиса (ККТиС). "
    "Отвечай только на вопросы, связанные с колледжем, образованием, приёмом, расписанием, "
    "специальностями, контактами и студенческой жизнью. "
    "Если вопрос не касается колледжа или образования — вежливо откажись отвечать, "
    "например: «Извините, я могу отвечать только на вопросы, связанные с колледжем ККТиС.» "
    "Отвечай дружелюбно, кратко и информативно."
)


async def generate_reply(prompt: str) -> str:
    """
    Универсальная функция генерации текста.
    Пытается использовать OpenAI → Gemini → OpenRouter.
    Ограничена только тематикой ККТиС.
    """
    try:
        logger.info("🧠 Используется OpenAI (GPT-4o-mini)")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": COLLEGE_RULES},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        err = str(e)
        logger.warning(f"⚠️ Ошибка OpenAI: {err}")

        if "insufficient_quota" in err or "429" in err:
            # Пробуем Gemini
            try:
                logger.info("🔄 Переключение на Gemini...")
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                reply = model.generate_content(f"{COLLEGE_RULES}\n\nПользователь: {prompt}")
                return reply.text.strip()
            except Exception as e2:
                logger.warning(f"⚠️ Ошибка Gemini: {e2}")

                # Пробуем OpenRouter
                try:
                    logger.info("🔄 Переключение на OpenRouter...")
                    headers = {
                        "Authorization": f"Bearer {OPENROUTER_KEY}",
                        "Content-Type": "application/json",
                    }
                    data = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": COLLEGE_RULES},
                            {"role": "user", "content": prompt}
                        ],
                    }
                    resp = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=60
                    )
                    rj = resp.json()
                    return rj["choices"][0]["message"]["content"].strip()
                except Exception as e3:
                    logger.error(f"❌ Все провайдеры недоступны: {e3}")
                    return "😔 Все модели сейчас недоступны. Попробуй позже."
        else:
            return f"⚠️ Ошибка: {err}"

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

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я виртуальный помощник Карагандинского колледжа технологий и сервиса (ККТиС). "
        "Задайте вопрос о поступлении, расписании или студенческой жизни."
    )


@dp.message()
async def chat(message: Message):
    prompt = message.text
    reply = await generate_reply(prompt)
    await message.answer(reply)


async def main():
    logger.info("✅ Бот запущен и готов к работе! Только по тематике ККТиС.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
