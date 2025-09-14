Друг, [14.09.2025 17:45]
import os
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from flask import Flask, request

# === Константы ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1002155394225  # ID канала
if not BOT_TOKEN:
    raise ValueError("❌ Установи переменную окружения BOT_TOKEN на Render!")

# Этапы анкеты
CHOOSING_ROLE, CONTRACTOR_STEP1, CONTRACTOR_STEP2, CONTRACTOR_STEP3, \
WORKER_STEP1, WORKER_STEP2, WORKER_STEP3 = range(7)

# === Flask для Webhook ===
app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()


# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👷 Подрядчик", callback_data="contractor")],
        [InlineKeyboardButton("⚒️ Рабочий", callback_data="worker")],
    ]
    await update.message.reply_text(
        "Привет! Выбери, кто ты:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSING_ROLE


# === Выбор подрядчик/рабочий ===
async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "contractor":
        await query.edit_message_text("🏗 Где нужны рабочие?")
        return CONTRACTOR_STEP1

    elif query.data == "worker":
        await query.edit_message_text("🔧 Какого профиля специалист?")
        return WORKER_STEP1


# === Подрядчик: шаги анкеты ===
async def contractor_step1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text
    await update.message.reply_text("👷‍♂️ Какие рабочие нужны?")
    return CONTRACTOR_STEP2


async def contractor_step2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["workers"] = update.message.text
    await update.message.reply_text("📞 Номер для связи?")
    return CONTRACTOR_STEP3


async def contractor_step3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text

    text = (
        "✅ Заявка от подрядчика:\n"
        f"🏗 Где нужны рабочие: {context.user_data['place']}\n"
        f"👷‍♂️ Кто нужен: {context.user_data['workers']}\n"
        f"📞 Контакт: {context.user_data['contact']}"
    )

    await update.message.reply_text("Спасибо! Ваша анкета сохранена.")
    await telegram_app.bot.send_message(chat_id=CHANNEL_ID, text=text)
    return ConversationHandler.END


# === Рабочий: шаги анкеты ===
async def worker_step1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["specialty"] = update.message.text
    await update.message.reply_text("💰 Сколько денег за работу (ед. изм.)?")
    return WORKER_STEP2


async def worker_step2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["rate"] = update.message.text
    await update.message.reply_text("📞 Номер для связи?")
    return WORKER_STEP3


async def worker_step3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["contact"] = update.message.text

    text = (
        "✅ Анкета рабочего:\n"
        f"👷‍♂️ Специальность: {context.user_data['specialty']}\n"
        f"💰 Ставка: {context.user_data['rate']}\n"
        f"📞 Контакт: {context.user_data['contact']}"
    )

    await update.message.reply_text("Спасибо! Ваша анкета сохранена.")
    await telegram_app.bot.send_message(chat_id=CHANNEL_ID, text=text)
    return ConversationHandler.END


# === Отмена ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено.")
    return ConversationHandler.END


# === Регистрация хендлеров ===
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_ROLE: [CallbackQueryHandler(choose_role)],
        CONTRACTOR_STEP1: [MessageHandler(filters.TEXT & ~filters.

Друг, [14.09.2025 17:45]
COMMAND, contractor_step1)],
        CONTRACTOR_STEP2: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_step2)],
        CONTRACTOR_STEP3: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_step3)],
        WORKER_STEP1: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_step1)],
        WORKER_STEP2: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_step2)],
        WORKER_STEP3: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_step3)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

telegram_app.add_handler(conv_handler)


# === Flask endpoint для Webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"


if name == "__main__":
    import threading

    # Запускаем Telegram-бота в отдельном потоке
    threading.Thread(target=lambda: telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path=BOT_TOKEN,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    )).start()

    # Запускаем Flask
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
