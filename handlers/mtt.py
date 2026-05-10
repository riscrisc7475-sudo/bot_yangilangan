from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import PRICE_MTT, CARD_NUMBER, CARD_OWNER, PHONE_NUMBER
import json

with open("data/mtt_files.json") as f:
    MTT_DATA = json.load(f)

CHOOSE_GROUP, CHOOSE_TOPIC, CHOOSE_SUBTOPIC, WAIT_PAYMENT = range(4)
WAIT_TEXT = 99

MTT_ARIZA_TOPIC, MTT_ARIZA_PAYMENT = range(10, 12)


async def mtt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()

    keyboard = [[InlineKeyboardButton(g, callback_data=f"mtt_group_{g}")] for g in MTT_DATA.keys()]
    keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")])
    text = "📚 MTT bo'limi\n\nQaysi guruh uchun material kerak?"

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_GROUP


async def choose_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    group = query.data.replace("mtt_group_", "")
    context.user_data["mtt_group"] = group

    topics = MTT_DATA[group]
    keyboard = [[InlineKeyboardButton(t, callback_data=f"mtt_topic_{t}")] for t in topics.keys()]
    keyboard.append([InlineKeyboardButton("📝 Kerakli mavzu yo'qmi? Ariza qoldiring!", callback_data=f"mtt_ariza_{group}")])
    keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")])

    await query.edit_message_text(
        f"📂 <b>{group}</b> guruhi\n\nQaysi fan/yo'nalish kerak?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return CHOOSE_TOPIC


async def choose_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    topic = query.data.replace("mtt_topic_", "")
    context.user_data["mtt_topic"] = topic
    group = context.user_data["mtt_group"]

    subtopics = MTT_DATA[group][topic]
    keyboard = [[InlineKeyboardButton(st, callback_data=f"mtt_sub_{st}")] for st in subtopics.keys()]
    keyboard.append([InlineKeyboardButton("📝 Kerakli mavzu yo'qmi? Ariza qoldiring!", callback_data=f"mtt_ariza_{group}")])
    keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")])

    await query.edit_message_text(
        f"📘 <b>{topic}</b> ({group})\n\nAynan qaysi mavzu kerak?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return CHOOSE_SUBTOPIC


async def choose_subtopic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subtopic = query.data.replace("mtt_sub_", "")
    group = context.user_data["mtt_group"]
    topic = context.user_data["mtt_topic"]
    file_id = MTT_DATA[group][topic][subtopic]

    context.user_data["mtt_subtopic"] = subtopic
    context.user_data["mtt_file_id"] = file_id
    context.user_data["order_type"] = "mtt"
    context.user_data["mtt_topic"] = f"{topic} → {subtopic}"
    context.user_data["user_text"] = "Matn talab qilinmadi"

    keyboard = [[InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_main")]]

    await query.edit_message_text(
        f"✅ Siz tanladingiz: <b>{topic} → {subtopic}</b>\n\n"
        f"💳 To'lov miqdori: <b>{PRICE_MTT:,} so'm</b>\n"
        f"📌 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"👤 Karta egasi: <b>{CARD_OWNER}</b>\n\n"
        f"To'lovni amalga oshirib, <b>to'lov chekini (skrinshot)</b> shu yerga yuboring 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAIT_PAYMENT


# =============================================
# MTT MAXSUS ARIZA
# =============================================

async def mtt_ariza_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    group = query.data.replace("mtt_ariza_", "")
    context.user_data["mtt_ariza_group"] = group

    text = (
        f"📝 <b>MTT Maxsus Ariza</b> ({group})\n\n"
        "Kerakli mavzuni ro'yxatda topa olmadingizmi? Xavotir olmang!\n\n"
        "✍️ Iltimos, quyidagi ma'lumotlarni <b>bitta xabarda</b> yozib yuboring:\n"
        "<i>Guruh, Fan va Mavzu nomi</i>\n\n"
        "📌 Masalan: <i>2-kichik guruh, Matematika, Geometrik shakllar</i>"
    )
    keyboard = [[InlineKeyboardButton("🏠 Bosh menyuga qaytish", callback_data="back_to_main")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    return MTT_ARIZA_TOPIC


async def mtt_ariza_receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mtt_ariza_text"] = update.message.text

    keyboard = [[InlineKeyboardButton("🏠 Bosh menyuga qaytish", callback_data="back_to_main")]]
    text = (
        f"✅ Arizangiz qabul qilindi!\n\n"
        f"💳 Xizmat narxi: <b>{PRICE_MTT:,} so'm</b>\n"
        f"📌 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"👤 Karta egasi: <b>{CARD_OWNER}</b>\n\n"
        f"To'lovni amalga oshirib, <b>to'lov chekini (skrinshot)</b> shu yerga yuboring 👇"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    return MTT_ARIZA_PAYMENT


async def mtt_ariza_receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_GROUP_ID
    from database import save_order

    user = update.message.from_user
    ariza_text = context.user_data.get("mtt_ariza_text", "Yozilmadi")
    group = context.user_data.get("mtt_ariza_group", "Noma'lum")

    order_id = save_order(
        user_id=user.id,
        username=user.username or user.first_name,
        order_type="mtt_ariza",
        section=f"MTT Maxsus Ariza ({group})",
        topic=ariza_text,
        file_id="CUSTOM_ORDER"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"b_approve_{order_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{order_id}")
        ]
    ])

    caption = (
        f"🆕 <b>MTT MAXSUS ARIZA</b>\n\n"
        f"👤 Mijoz: @{user.username or user.first_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📂 Guruh: <b>{group}</b>\n"
        f"✍️ Buyurtma:\n<b>{ariza_text}</b>\n\n"
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
        f"✅ Chekingiz va arizangiz adminlarimizga yuborildi!\n"
        f"📞 Qo'shimcha savol bo'lsa: {PHONE_NUMBER}\n"
        f"Kuting... ⏳"
    )
    return ConversationHandler.END
