import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)
from flask import Flask
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1002155394225  # id твоего канала

if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN на Render!")

# Состояния
ROLE, SPEC, PRICE, CONTACT_W, PLACE, NEED, CONTACT_C = range(7)

# Flask для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👷 Рабочий", callback_data="worker")],
        [InlineKeyboardButton("🏗 Подрядчик", callback_data="contractor")]
    ]
    await update.message.reply_text(
        "Привет! Выбери, кто ты:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ROLE

# Роль
async def role_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["role"] = query.data

    if query.data == "worker":
        await query.edit_message_text("✍️ Введи свою специальность:")
        return SPEC
    else:
        await query.edit_message_text("📍 Где нужны рабочие?")
        return PLACE

# Рабочий — спец
async def worker_spec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["spec"] = update.message.text
    await update.message.reply_text("💰 Сколько денег просишь (ставка за ед.)?")
    return PRICE

# Рабочий — ставка
async def worker_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    await update.message.reply_text("📞 Оставь номер или @username:")
    return CONTACT_W

# Рабочий — контакт
async def worker_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    spec = context.user_data["spec"]
    price = context.user_data["price"]
    contact = context.user_data["contact"]

    text = (
        f"✅ Новая анкета:\n\n"
        f"👷 Рабочий\n"
        f"🛠 Специальность: {spec}\n"
        f"💰 Ставка: {price}\n"
        f"📞 Контакт: {contact}"
    )
    await update.message.reply_text("Спасибо! Ваша анкета сохранена.")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    return ConversationHandler.END

# Подрядчик — место
async def contractor_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text
    await update.message.reply_text("👷 Какие рабочие нужны?")
    return NEED

# Подрядчик — нужные
async def contractor_need(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["need"] = update.message.text
    await update.message.reply_text("📞 Оставь номер или @username:")
    return CONTACT_C

# Подрядчик — контакт
async def contractor_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text
    place = context.user_data["place"]
    need = context.user_data["need"]
    contact = context.user_data["contact"]

    text = (
        f"✅ Новая анкета:\n\n"
        f"🏗 Подрядчик\n"
        f"📍 Объект: {place}\n"
        f"👷 Нужны: {need}\n"
        f"📞 Контакт: {contact}"
    )
    await update.message.reply_text("Спасибо! Ваша анкета сохранена.")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def run_bot():
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ROLE: [CallbackQueryHandler(role_chosen)],
            SPEC: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_spec)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_price)],
            CONTACT_W: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_contact)],
            PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_place)],
            NEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_need)],
            CONTACT_C: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    tg_app.add_handler(conv_handler)
    tg_app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
