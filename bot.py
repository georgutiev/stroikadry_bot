import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ==============================
# 🔹 Настройка логов
# ==============================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==============================
# 🔹 Переменные окружения
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1002155394225  # <-- твой канал

if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN на Render!")

# ==============================
# 🔹 Обработчики команд
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👷 Подрядчик", "🛠 Рабочий"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Выбери, кто ты:", reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "👷 Подрядчик":
        await update.message.reply_text("Ты выбрал: 👷 Подрядчик")
    elif text == "🛠 Рабочий":
        await update.message.reply_text("Ты выбрал: 🛠 Рабочий")
    else:
        await update.message.reply_text("Пожалуйста, используй кнопки ниже.")

# ==============================
# 🔹 Главная функция
# ==============================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))

    logger.info("✅ Бот запущен через polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
