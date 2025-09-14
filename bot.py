import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN на Render!")
if not CHANNEL_ID:
    raise ValueError("❌ Установи переменную окружения CHANNEL_ID на Render!")

# Flask для webhook
app = Flask(__name__)

# Состояния
CHOOSING, CONTRACTOR_LOCATION, CONTRACTOR_WORKERS, CONTRACTOR_PHONE, WORKER_PROFILE, WORKER_PRICE, WORKER_PHONE = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👷 Подрядчик", callback_data="contractor")],
        [InlineKeyboardButton("🔨 Рабочий", callback_data="worker")]
    ]
    await update.message.reply_text("Привет! Выбери, кто ты:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING

async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role = query.data
    context.user_data["role"] = role

    if role == "contractor":
        await query.edit_message_text("📍 Где нужны рабочие?")
        return CONTRACTOR_LOCATION
    else:
        await query.edit_message_text("👷 Какого профиля специалист?")
        return WORKER_PROFILE

async def contractor_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text
    await update.message.reply_text("🔧 Какие рабочие нужны?")
    return CONTRACTOR_WORKERS

async def contractor_workers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["workers"] = update.message.text
    await update.message.reply_text("📞 Укажи номер для связи:")
    return CONTRACTOR_PHONE

async def contractor_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    text = (f"📢 Заявка от подрядчика:
"
            f"📍 Место: {context.user_data['location']}
"
            f"👷 Нужны: {context.user_data['workers']}
"
            f"📞 Контакт: {context.user_data['phone']}")
    await update.message.reply_text("✅ Заявка отправлена в канал!")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    return ConversationHandler.END

async def worker_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["profile"] = update.message.text
    await update.message.reply_text("💰 Сколько денег за ед. измерения?")
    return WORKER_PRICE

async def worker_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = update.message.text
    await update.message.reply_text("📞 Укажи номер для связи:")
    return WORKER_PHONE

async def worker_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    text = (f"📢 Заявка от рабочего:
"
            f"👷 Профиль: {context.user_data['profile']}
"
            f"💰 Цена: {context.user_data['price']}
"
            f"📞 Контакт: {context.user_data['phone']}")
    await update.message.reply_text("✅ Анкета отправлена в канал!")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заполнение анкеты отменено. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(choose_role)],
            CONTRACTOR_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_location)],
            CONTRACTOR_WORKERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_workers)],
            CONTRACTOR_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_phone)],
            WORKER_PROFILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_profile)],
            WORKER_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_price)],
            WORKER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler)

    # Flask endpoint для Telegram webhook
    @app.route(f"/{BOT_TOKEN}", methods=["POST"])
    def webhook():
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return "ok", 200

    # Запуск Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    main()
