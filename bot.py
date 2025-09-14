
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002155394225"))

if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN на Render!")

# Flask app
app_flask = Flask(__name__)

ROLE, PLACE, NEED, CONTACT_C, SPEC, PRICE, CONTACT_W = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏗 Подрядчик", callback_data="contractor")],
        [InlineKeyboardButton("⚒ Рабочий", callback_data="worker")]
    ]
    await update.message.reply_text("Привет! Выбери, кто ты:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ROLE

async def role_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role = query.data
    context.user_data["role"] = role

    if role == "contractor":
        await query.edit_message_text("🏗 Где нужны рабочие?")
        return PLACE
    else:
        await query.edit_message_text("⚒ Укажи свою специальность:")
        return SPEC

async def contractor_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text
    await update.message.reply_text("Какие рабочие нужны?")
    return NEED

async def contractor_need(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["need"] = update.message.text
    await update.message.reply_text("Оставь контакт для связи:")
    return CONTACT_C

async def contractor_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    place = context.user_data["place"]
    need = context.user_data["need"]
    contact = update.message.text

    text = (
        f"🏗 <b>Заявка от подрядчика</b>\n"
        f"Объект: {place}\n"
        f"Нужны: {need}\n"
        f"Контакт: {contact}"
    )

    await update.message.reply_html("✅ Объявление отправлено!")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")
    return ConversationHandler.END

async def worker_spec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["spec"] = update.message.text
    await update.message.reply_text("💰 Укажи ставку за работу:")
    return PRICE

async def worker_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    await update.message.reply_text("☎️ Оставь контакт для связи:")
    return CONTACT_W

async def worker_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    spec = context.user_data["spec"]
    price = context.user_data["price"]
    contact = update.message.text

    text = (
        f"⚒ <b>Анкета рабочего</b>\n"
        f"Специальность: {spec}\n"
        f"Ставка: {price}\n"
        f"Контакт: {contact}"
    )

    await update.message.reply_html("✅ Анкета отправлена!")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ROLE: [CallbackQueryHandler(role_chosen)],
            PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_place)],
            NEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_need)],
            CONTACT_C: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_contact)],
            SPEC: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_spec)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_price)],
            CONTACT_W: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_contact)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv)
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    )

if __name__ == "__main__":
    main()
