# TELEGRAM_TOKEN = "6521993430:AAFwNuNOUmZJT_kJnUzuq3thkqAh05FoSQg"
# CHAT_ID = "1279066123"  # Укажи свой ID (получить можно через @userinfobot)

import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ====== НАСТРОЙКИ ======
TELEGRAM_TOKEN = "6521993430:AAFwNuNOUmZJT_kJnUzuq3thkqAh05FoSQg"

# ====== ДАННЫЕ ======
DUAS = [
    {
        "title": "Перед сном",
        "arabic": "اللَّهُمَّ بِاسْمِكَ أَمُوتُ وَأَحْيَا",
        "translit": "Аллахумма бисмика амуту уа ахья",
        "translate": "О, Аллах! С Твоим именем я умираю и оживаю."
    },
    {
        "title": "Перед едой",
        "arabic": "بِسْمِ اللَّهِ وَعَلَى بَرَكَةِ اللَّهِ",
        "translit": "Бисмиллях ва ‘аля баракатиллях",
        "translate": "С именем Аллаха и с Его благословением."
    },
]

HADITHS = [
    {
        "number": "аль-Бухари №1",
        "text": "Поистине, дела оцениваются по намерениям."
    },
    {
        "number": "Муслим №223",
        "text": "Тот, кто усердно совершает молитву, будет защищён от бед."
    },
]

IMAGE_URL = "https://i.imgur.com/4M34hi2.jpeg"

# ====== ОБРАБОТЧИКИ ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 Случайный аят", callback_data='quran')],
        [InlineKeyboardButton("🤲 Дуа", callback_data='dua')],
        [InlineKeyboardButton("📜 Хадис", callback_data='hadith')],
        [InlineKeyboardButton("🔍 Поиск суры", callback_data='search')],
        [InlineKeyboardButton("🕌 Время намаза", callback_data='prayer')],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🌙 *Ассаляму алейкум!* Я — исламский бот 🤖\n\n"
        "Выбери нужный раздел:"
    )
    await update.message.reply_photo(photo=IMAGE_URL, caption=text, parse_mode="Markdown", reply_markup=markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'quran':
        await query.message.reply_text(get_quran_verse(), parse_mode="Markdown")
    elif query.data == 'dua':
        await query.message.reply_text(get_random_dua(), parse_mode="Markdown")
    elif query.data == 'hadith':
        await query.message.reply_text(get_random_hadith(), parse_mode="Markdown")
    elif query.data == 'search':
        await query.message.reply_text("🔍 Введите номер или название суры:")
        context.user_data["search_mode"] = True
    elif query.data == 'prayer':
        await query.message.reply_text("🌍 Введите название города:")
        context.user_data["prayer_mode"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if context.user_data.get("search_mode"):
        await update.message.reply_text(get_surah(msg), parse_mode="Markdown")
        context.user_data["search_mode"] = False
    elif context.user_data.get("prayer_mode"):
        await update.message.reply_text(get_prayer_times(msg), parse_mode="Markdown")
        context.user_data["prayer_mode"] = False

def get_random_dua():
    d = random.choice(DUAS)
    return f"🤲 *{d['title']}*\n\n📖 {d['arabic']}\n\n🔊 _{d['translit']}_\n\n💬 {d['translate']}"

def get_random_hadith():
    h = random.choice(HADITHS)
    return f"📜 *Хадис ({h['number']}):*\n\n_{h['text']}_"

def get_quran_verse():
    num = random.randint(1, 6236)
    url = f"https://api.alquran.cloud/v1/ayah/{num}/ru.kuliev"
    r = requests.get(url)
    if r.status_code != 200:
        return "❌ Не удалось загрузить аят."
    d = r.json()["data"]
    return (
        f"📖 *Сура {d['surah']['englishName']}, аят {d['numberInSurah']}*\n\n"
        f"🕋 {d['text']}"
    )

def get_surah(identifier):
    url_ar = f"https://api.alquran.cloud/v1/surah/{identifier}/ar.alafasy"
    url_ru = f"https://api.alquran.cloud/v1/surah/{identifier}/ru.kuliev"
    try:
        ar = requests.get(url_ar).json()["data"]
        ru = requests.get(url_ru).json()["data"]
        name = ar["englishName"]
        ayah_ar = ar["ayahs"][0]["text"]
        ayah_ru = ru["ayahs"][0]["text"]
        return (
            f"📖 *Сура {name}* (аят 1):\n\n"
            f"🕋 {ayah_ar}\n\n"
            f"📚 _{ayah_ru}_"
        )
    except:
        return "❌ Не удалось найти суру."

def get_prayer_times(city):
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=&method=2"
        r = requests.get(url).json()
        t = r["data"]["timings"]
        return (
            f"🕌 *Время намаза в {city.title()}:*\n\n"
            f"Фаджр: {t['Fajr']}\n"
            f"Зухр: {t['Dhuhr']}\n"
            f"Аср: {t['Asr']}\n"
            f"Магриб: {t['Maghrib']}\n"
            f"Иша: {t['Isha']}"
        )
    except:
        return "❌ Не удалось получить время намаза."

# ====== ЗАПУСК ======
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
