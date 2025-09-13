import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "7703388794:AAFiB0m0-PLQz70u9XBcJXW9CgOtpdRog5U"

if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN на Render!")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👷 Подрядчик", "🛠 Рабочий"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Выбери, кто ты:", reply_markup=reply_markup)

# Обработка выбора
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "👷 Подрядчик":
        await update.message.reply_text("Ты выбрал: Подрядчик 👷")
    elif text == "🛠 Рабочий":
        await update.message.reply_text("Ты выбрал: Рабочий 🛠")
    else:
        await update.message.reply_text("Пожалуйста, используй кнопки.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))

    app.run_polling()

if __name__ == "__main__":
    main()
