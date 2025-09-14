import os
from flask import Flask, request
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)

# --- Константы шагов анкеты ---
CHOOSING_ROLE, SPECIALTY, RATE, CONTACT = range(4)

# --- Flask-приложение ---
app = Flask(__name__)

# --- Создаём приложение Telegram ---
TOKEN = os.getenv("BOT_TOKEN")  # токен берётся из переменных окружения на Render
application = Application.builder().token(TOKEN).build()

# --- Команда старт ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("👷 Подрядчик"), KeyboardButton("⚒️ Рабочий")],
        [KeyboardButton("➕ Другое")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋\nВыберите, кто вы:",
        reply_markup=reply_markup
    )
    return CHOOSING_ROLE

# --- Выбор роли ---
async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["role"] = update.message.text
    await update.message.reply_text("Укажите вашу специальность:")
    return SPECIALTY

# --- Ввод специальности ---
async def get_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["specialty"] = update.message.text
    await update.message.reply_text("Укажите вашу ставку:")
    return RATE

# --- Ввод ставки ---
async def get_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["rate"] = update.message.text
    await update.message.reply_text("Укажите ваш контакт (телефон или Telegram):")
    return CONTACT

# --- Ввод контакта и завершение ---
async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text

    role = context.user_data["role"]
    specialty = context.user_data["specialty"]
    rate = context.user_data["rate"]
    contact = context.user_data["contact"]

    text = (
        f"✅ Спасибо! Ваша анкета сохранена.\n\n"
        f"👷 Роль: {role}\n"
        f"🛠 Специальность: {specialty}\n"
        f"💰 Ставка: {rate}\n"
        f"📞 Контакт: {contact}"
    )

    await update.message.reply_text(text)

    return ConversationHandler.END

# --- Отмена ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Анкета отменена. Чтобы начать заново, напишите /start")
    return ConversationHandler.END

# --- Настройка ConversationHandler ---
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
        SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_specialty)],
        RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_rate)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)

# --- Flask route для Telegram Webhook ---
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# --- Flask healthcheck ---
@app.route("/")
def index():
    return "Бот работает!"

# --- Запуск ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )
    app.run(host="0.0.0.0", port=port)
