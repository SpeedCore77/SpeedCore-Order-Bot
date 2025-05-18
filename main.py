import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

ADMIN_CONTACT = "@aksy_can_help"
CRYPTO_ADDRESSES = {
    "BTC": "bc1qexampleaddressbtc",
    "USDT": "TExampleUSDTAddress",
    "TON": "EQCexampleTONaddress",
    "LTC": "ltc1qexampleltcaddress",
    "Monero": "4AexampleMoneroAddress",
    "Перевод на счёт": "IBAN: LV00BANK0123456789012"
}
PRICES = {
    "1 г": "15€",
    "5 г": "50€",
    "10 г": "70€"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✉️ Сделать заказ", callback_data="order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в магазин A...+!\nВыберите действие:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "order":
        grams_keyboard = [[InlineKeyboardButton(f"A...+ {g} — {p}", callback_data=f"gram_{g}")] for g, p in PRICES.items()]
        await query.edit_message_text("Выберите объём:", reply_markup=InlineKeyboardMarkup(grams_keyboard))
    elif query.data.startswith("gram_"):
        g = query.data.split("_")[1]
        context.user_data["gram"] = g
        methods = [[InlineKeyboardButton(k, callback_data=f"pay_{k}")] for k in CRYPTO_ADDRESSES.keys()]
        await query.edit_message_text(f"Вы выбрали: A...+ {g}\nВыберите способ оплаты:", reply_markup=InlineKeyboardMarkup(methods))
    elif query.data.startswith("pay_"):
        m = query.data.split("_")[1]
        g = context.user_data.get("gram", "?")
        price = PRICES.get(g, "?")
        addr = CRYPTO_ADDRESSES[m]
        context.user_data["payment"] = m
        context.user_data["address"] = addr
        context.user_data["price"] = price
        delivery_keyboard = [
            [InlineKeyboardButton("📍 Дроп (закладка)", callback_data="delivery_drop")],
            [InlineKeyboardButton("📦 Почтовая посылка", callback_data="delivery_mail")]
        ]
        await query.edit_message_text(
            "Выберите способ доставки:",
            reply_markup=InlineKeyboardMarkup(delivery_keyboard)
        )
    elif query.data.startswith("delivery_"):
        delivery = "закладку" if query.data == "delivery_drop" else "почтовую посылку"
        g = context.user_data.get("gram", "?")
        price = context.user_data.get("price", "?")
        m = context.user_data.get("payment", "?")
        addr = context.user_data.get("address", "?")
        text = f"Ваш заказ: A...+ {g} — {price}\nОплата через: {m}\nДоставка: {delivery}\nАдрес для оплаты:\n{addr}\n\nПосле оплаты отправьте скриншот и ваш ник в {ADMIN_CONTACT}"
        await query.edit_message_text(text, parse_mode="Markdown")

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("order", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.run_polling()
