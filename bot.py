import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ==============================
# 🔹 Логирование
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
CHANNEL_ID = -1002155394225  # ID канала @StroiKadry15

if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN на Render!")

# ==============================
# 🔹 Состояния
# ==============================
ROLE, CONTRACTOR_PLACE, CONTRACTOR_NEED, CONTRACTOR_CONTACT, WORKER_SPEC, WORKER_PRICE, WORKER_CONTACT, OTHER = range(8)

# ==============================
# 🔹 /start
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👷 Подрядчик", "🛠 Рабочий", "➕ Другое"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Выбери, кто ты:", reply_markup=reply_markup)
    return ROLE

# ==============================
# 🔹 Выбор роли
# ==============================
async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "👷 Подрядчик":
        await update.message.reply_text("Укажи, где нужны рабочие (город/объект):")
        return CONTRACTOR_PLACE
    elif text == "🛠 Рабочий":
        await update.message.reply_text("Укажи свою специальность (профиль):")
        return WORKER_SPEC
    elif text == "➕ Другое":
        await update.message.reply_text("Напиши, что именно тебе нужно:")
        return OTHER
    else:
        await update.message.reply_text("Используй кнопки ниже.")
        return ROLE

# ==============================
# 🔹 Подрядчик
# ==============================
async def contractor_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text
    await update.message.reply_text("Какие рабочие нужны (специальность)?")
    return CONTRACTOR_NEED

async def contractor_need(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["need"] = update.message.text
    await update.message.reply_text("Оставь номер для связи:")
    return CONTRACTOR_CONTACT

async def contractor_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = context.user_data["place"]
    need = context.user_data["need"]
    contact = update.message.text

    text_user = f"✅ Спасибо! Ваша заявка сохранена.\n📍 Место: {place}\n👷 Нужны: {need}\n📞 Контакт: {contact}"
    await update.message.reply_text(text_user)

    text_channel = f"📢 Новая заявка от подрядчика\n📍 Место: {place}\n👷 Нужны: {need}\n📞 Контакт: {contact}"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text_channel)

    return ConversationHandler.END

# ==============================
# 🔹 Рабочий
# ==============================
async def worker_spec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["spec"] = update.message.text
    await update.message.reply_text("Укажи стоимость за единицу работы (например 3000₽/день):")
    return WORKER_PRICE

async def worker_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    await update.message.reply_text("Оставь номер для связи:")
    return WORKER_CONTACT

async def worker_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    spec = context.user_data["spec"]
    price = context.user_data["price"]
    contact = update.message.text

    text_user = f"✅ Спасибо! Ваша анкета сохранена.\n👷 Специальность: {spec}\n💰 Ставка: {price}\n📞 Контакт: {contact}"
    await update.message.reply_text(text_user)

    text_channel = f"📢 Новая анкета от рабочего\n👷 Специальность: {spec}\n💰 Ставка: {price}\n📞 Контакт: {contact}"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text_channel)

    return ConversationHandler.END

# ==============================
# 🔹 Другое
# ==============================
async def other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    other_text = update.message.text
    text_user = f"✅ Спасибо! Мы сохранили твой запрос: {other_text}"
    await update.message.reply_text(text_user)

    text_channel = f"📢 Новый запрос (Другое)\n📝 {other_text}"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text_channel)

    return ConversationHandler.END

# ==============================
# 🔹 Главная функция
# ==============================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
            CONTRACTOR_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_place)],
            CONTRACTOR_NEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_need)],
            CONTRACTOR_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_contact)],
            WORKER_SPEC: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_spec)],
            WORKER_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_price)],
            WORKER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_contact)],
            OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, other)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    logger.info("✅ Бот запущен через polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
