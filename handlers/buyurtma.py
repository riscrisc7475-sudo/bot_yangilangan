
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from config import ADMIN_GROUP_ID, CARD_NUMBER
from database import save_order

BUY_WAIT_TOPIC, BUY_WAIT_PAYMENT = range(7, 9)

SECTIONS = {
    "section_diplom": ("📝 Diplom ishi", 400000),
    "section_loyiha": ("📋 Loyiha ishi", 100000),
    "section_boshqa": ("📌 Boshqa ishlar", 50000),
}

async def buyurtma_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    section_key = query.data
    section_name, price = SECTIONS.get(section_key, ("Noma'lum", 0))

    context.user_data["buy_section"] = section_name
    context.user_data["buy_price"] = price

    text = (
        f"<b>{section_name}</b>\n\n"
        f"✍️ Iltimos, <b>mavzu va talablarni</b> bitta xabarda to'liq yozib yuboring.\n\n"
        f"<i>Masalan: Maktabgacha ta'lim tizimini rivojlantirish</i>"
    )
    keyboard = [[InlineKeyboardButton("🏠 Bosh menyuga qaytish", callback_data="back_to_main")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    return BUY_WAIT_TOPIC

async def buy_receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["buy_topic_text"] = update.message.text
    section_name = context.user_data.get("buy_section", "Noma'lum")
    price = context.user_data.get("buy_price", 0)

    keyboard = [[InlineKeyboardButton("🏠 Bosh menyuga qaytish", callback_data="back_to_main")]]
    text = (
        f"✅ Arizangiz qabul qilindi!\n\n"
        f"📌 Bo'lim: <b>{section_name}</b>\n"
        f"💳 Xizmat narxi: <b>{price:,} so'm</b>\n"
        f"📌 Karta raqami: <code>{CARD_NUMBER}</code>\n\n"
        f"To'lovni amalga oshirib, <b>to'lov chekini (skrinshot)</b> shu yerga yuboring 👇"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    return BUY_WAIT_PAYMENT

async def buy_receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    topic_text = context.user_data.get("buy_topic_text", "Yozilmadi")
    section_name = context.user_data.get("buy_section", "Noma'lum")

    order_id = save_order(
        user_id=user.id,
        username=user.username or user.first_name,
        order_type="buyurtma",
        section=section_name,
        topic=topic_text,
        file_id="CUSTOM_ORDER"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"b_approve_{order_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{order_id}")
        ]
    ])

    caption = (
        f"🆕 <b>YANGI BUYURTMA</b>\n\n"
        f"📌 Bo'lim: <b>{section_name}</b>\n"
        f"👤 Mijoz: @{user.username or user.first_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"✍️ Mavzu:\n<b>{topic_text}</b>\n\n"
        f"📋 Buyurtma №: {order_id}\n\n"
        f"⚠️ Fayl tayyor bo'lgach:\n"
        f"<code>/fayl {user.id}</code> deb hujjat bilan yuboring!"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_GROUP_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await update.message.reply_text(
        "✅ Chekingiz va arizangiz adminlarimizga yuborildi!\nKuting... ⏳"
    )
    return ConversationHandler.END
