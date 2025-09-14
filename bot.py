import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# --- Состояния ---
CHOOSING, CONTRACTOR_PLACE, CONTRACTOR_WORKERS, CONTRACTOR_CONTACT, \
WORKER_SPECIALTY, WORKER_RATE, WORKER_CONTACT = range(7)

CHANNEL_ID = -1002155394225  # твой канал

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["👷 Подрядчик", "⚒ Рабочий", "➕ Другое"]]
    await update.message.reply_text(
        "Привет! Выбери, кто ты:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return CHOOSING

# --- Ветвь Подрядчик ---
async def contractor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Где нужны рабочие?", reply_markup=ReplyKeyboardRemove())
    return CONTRACTOR_PLACE

async def contractor_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["place"] = update.message.text
    await update.message.reply_text("Какие рабочие нужны?")
    return CONTRACTOR_WORKERS

async def contractor_workers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["workers"] = update.message.text
    await update.message.reply_text("Номер для связи?")
    return CONTRACTOR_CONTACT

async def contractor_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["contact"] = update.message.text
    text = (
        f"📌 Заявка от подрядчика:\n"
        f"📍 Место: {context.user_data['place']}\n"
        f"👷 Рабочие: {context.user_data['workers']}\n"
        f"📞 Контакт: {context.user_data['contact']}"
    )
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    await update.message.reply_text("✅ Спасибо! Ваша анкета сохранена.\nЧтобы начать заново, введите /start.")
    return ConversationHandler.END

# --- Ветвь Рабочий ---
async def worker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Какая у тебя специальность?", reply_markup=ReplyKeyboardRemove())
    return WORKER_SPECIALTY

async def worker_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["specialty"] = update.message.text
    await update.message.reply_text("Сколько денег берёшь за единицу измерения?")
    return WORKER_RATE

async def worker_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["rate"] = update.message.text
    await update.message.reply_text("Оставь свой контакт для связи:")
    return WORKER_CONTACT

async def worker_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["contact"] = update.message.text
    text = (
        f"📌 Анкета от рабочего:\n"
        f"👷 Специальность: {context.user_data['specialty']}\n"
        f"💰 Ставка: {context.user_data['rate']}\n"
        f"📞 Контакт: {context.user_data['contact']}"
    )
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    await update.message.reply_text("✅ Спасибо! Ваша анкета сохранена.\nЧтобы начать заново, введите /start.")
    return ConversationHandler.END

# --- Ветвь Другое ---
async def other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=CHANNEL_ID, text="➕ Новая заявка: Другое")
    await update.message.reply_text("Спасибо! Ваша заявка передана админу.\nЧтобы начать заново, введите /start.",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Отмена ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Диалог завершён. Чтобы начать заново, введи /start.",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Основное приложение ---
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^👷 Подрядчик$"), contractor),
                MessageHandler(filters.Regex("^⚒ Рабочий$"), worker),
                MessageHandler(filters.Regex("^➕ Другое$"), other),
            ],
            CONTRACTOR_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_place)],
            CONTRACTOR_WORKERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_workers)],
            CONTRACTOR_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contractor_contact)],
            WORKER_SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_specialty)],
            WORKER_RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_rate)],
            WORKER_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, worker_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()

