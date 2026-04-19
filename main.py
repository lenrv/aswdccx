import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

API_TOKEN = "8789764033:AAEdqYi_PpmKUFuFHRuuqczAAJ-knUpteGY"
ADMIN_ID = 68205305

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ---------------- DATA ----------------

REQUIRED_CHANNELS = []
user_state = {}
msg_map = {}
admin_step = {}
banned_users = set()

# ---------------- CHECK SUB ----------------

async def is_subscribed(user_id: int) -> bool:
    if not REQUIRED_CHANNELS:
        return True

    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ---------------- FORCE JOIN ----------------

def join_kb():
    kb = []
    for ch in REQUIRED_CHANNELS:
        kb.append([
            InlineKeyboardButton(
                text=f"📢 اشتراك {ch}",
                url=f"https://t.me/{ch.replace('@','')}"
            )
        ])
    kb.append([InlineKeyboardButton(text="🔄 تحقق", callback_data="check")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ---------------- MENU ----------------

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔞 اشتراك في الكلوزات", callback_data="sub")],
        [InlineKeyboardButton(text="💬 تواصل المطور", callback_data="dev")],
        [InlineKeyboardButton(text="📢 قسم الإعلانات", callback_data="ads")],
        [InlineKeyboardButton(text="🚨 قسم البلاغات", callback_data="report")],
        [InlineKeyboardButton(text="📮 المساعدة", callback_data="help")],
    ])

# ---------------- ADMIN PANEL ----------------

def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 إضافة قناة", callback_data="add"),
            InlineKeyboardButton(text="➖ حذف قناة", callback_data="del")
        ],
        [
            InlineKeyboardButton(text="👤 حظر مستخدم", callback_data="ban"),
            InlineKeyboardButton(text="❌ إلغاء حظر", callback_data="unban")
        ]
    ])

# ---------------- CANCEL BUTTON ----------------

def cancel_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ إلغاء الإرسال", callback_data="cancel")]
    ])

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(msg: Message):
    if msg.from_user.id in banned_users:
        await msg.answer("⛔️ انت محظور")
        return

    if not await is_subscribed(msg.from_user.id):
        await msg.answer("⚠️ يجب الاشتراك بالقنوات أولاً", reply_markup=join_kb())
        return

    if msg.from_user.id == ADMIN_ID:
        await msg.answer("👋 مرحبا بك في البوت", reply_markup=admin_panel())
    else:
        await msg.answer("👋 مرحبا بك في البوت\n\nاختر القسم المناسب:", reply_markup=menu())

# ---------------- CALLBACK ----------------

@dp.callback_query()
async def cb(call: CallbackQuery):
    uid = call.from_user.id

    if uid in banned_users:
        await call.message.answer("⛔️ انت محظور")
        return

    if not await is_subscribed(uid):
        await call.message.answer("⚠️ غير مشترك", reply_markup=join_kb())
        return

    if call.data == "check":
        if await is_subscribed(uid):
            await call.message.answer("✅ تم التحقق")
            await call.message.answer("👋 مرحبا بك", reply_markup=menu())
        else:
            await call.message.answer("❌ غير مشترك", reply_markup=join_kb())

    elif uid == ADMIN_ID:
        if call.data == "add":
            admin_step[uid] = "add_channel"
            await call.message.answer("📢 ارسل يوزر القناة @")

        elif call.data == "del":
            admin_step[uid] = "del_channel"
            await call.message.answer("➖ ارسل يوزر القناة للحذف")

        elif call.data == "ban":
            admin_step[uid] = "ban"
            await call.message.answer("👤 ارسل ID المستخدم")

        elif call.data == "unban":
            admin_step[uid] = "unban"
            await call.message.answer("❌ ارسل ID لفك الحظر")

    elif call.data in ["sub", "dev", "ads", "report", "help"]:
        user_state[uid] = call.data

        texts = {
            "sub": "💬 ارسل الان رسالتك الاشتراك في الكلوزات\n\n📍سيتم تحويلك إلى قسم الاشتراكات",
            "ads": "💬 ارسل الان رسالتك الاشتراك في الاعلانات او استفسار عن الإعلانات\n\n📍 سيتم تحويل رسالتك إلى قسم الإعلانات",
            "dev": "💬 ارسل الان رسالتك التواصل المطور\n\n📍سيتم تحويل رسالتك إلى قسم المطور",
            "report": "🚨 ارسل الان بلاغك او تقديم بلاغ\n👮🏼‍♂️ارسل مشكلتك بالتفصيل\n\n📍سيتم تحويل رسالتك إلى قسم البلاغات",
            "help": "📮 ارسل طلب المساعدة\n\n📍 سيتم تحويل رسالتك إلى قسم المساعدة"
        }

        await call.message.answer(texts[call.data], reply_markup=cancel_button())

    elif call.data == "cancel":
        await call.message.answer(
            "📋 تم إلغاء الإرسال، العودة للقائمة الرئيسية.",
            reply_markup=menu()
        )

    elif call.data.startswith("ban_") and uid == ADMIN_ID:
        user_id = int(call.data.split("_")[1])
        banned_users.add(user_id)
        await call.message.answer("⛔️ تم حظر المستخدم")

    elif call.data.startswith("unban_") and uid == ADMIN_ID:
        user_id = int(call.data.split("_")[1])
        banned_users.discard(user_id)
        await call.message.answer("✅ تم فك حظر المستخدم")

# ---------------- ADMIN HANDLER ----------------

@dp.message(F.from_user.id == ADMIN_ID)
async def admin_handler(msg: Message):
    uid = msg.from_user.id

    if msg.reply_to_message:
        mid = msg.reply_to_message.message_id

        if mid in msg_map:
            user_id = msg_map[mid]
            await msg.copy_to(user_id)
            await msg.answer("📩 تم الرد على المستخدم بنجاح")
            return

    if uid not in admin_step:
        return

    step = admin_step[uid]

    if step == "add_channel":
        ch = msg.text.strip()

        if not ch.startswith("@"):
            await msg.answer("⚠️ لازم اليوزر يبدأ بـ @")
            return

        try:
            await bot.get_chat(ch)
            member = await bot.get_chat_member(chat_id=ch, user_id=ADMIN_ID)

            if member.status not in ["administrator", "creator"]:
                await msg.answer("❌ البوت مو أدمن بالقناة")
                return

        except:
            await msg.answer("❌ القناة غلط أو غير موجودة")
            return

        REQUIRED_CHANNELS.append(ch)
        await msg.answer("✅ تم إضافة القناة")
        admin_step.pop(uid)

    elif step == "del_channel":
        ch = msg.text.strip()

        if ch in REQUIRED_CHANNELS:
            REQUIRED_CHANNELS.remove(ch)
            await msg.answer("❌ تم حذف القناة")
        else:
            await msg.answer("⚠️ القناة غير موجودة")

        admin_step.pop(uid)

    elif step == "ban":
        try:
            banned_users.add(int(msg.text))
            await msg.answer("⛔️ تم حظر المستخدم")
        except:
            await msg.answer("⚠️ خطأ بالـ ID")

        admin_step.pop(uid)

    elif step == "unban":
        try:
            banned_users.discard(int(msg.text))
            await msg.answer("✅ تم فك الحظر")
        except:
            await msg.answer("⚠️ خطأ بالـ ID")

        admin_step.pop(uid)

# ---------------- USER TO ADMIN ----------------

@dp.message()
async def all_messages(msg: Message):
    uid = msg.from_user.id

    if uid == ADMIN_ID:
        return

    if uid in banned_users:
        return

    if not await is_subscribed(uid):
        await msg.answer("⚠️ يجب الاشتراك")
        return

    section_names = {
        "sub": "🔞 اشتراك في الكلوزات",
        "dev": "💬 تواصل المطور",
        "ads": "📢 قسم الإعلانات",
        "report": "🚨 قسم البلاغات",
        "help": "📮 المساعدة"
    }

    section = user_state.get(uid, "help")

    info_msg = await bot.send_message(
        ADMIN_ID,
        f"👤 الاسم: {msg.from_user.full_name}\n"
        f"🔗 اليوزر: @{msg.from_user.username if msg.from_user.username else 'ماكو'}\n"
        f"🆔 الايدي: {uid}\n"
        f"📌 القسم: {section_names.get(section, section)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⛔️ حظر", callback_data=f"ban_{uid}"),
                InlineKeyboardButton(text="❌ فك الحظر", callback_data=f"unban_{uid}")
            ]
        ])
    )

    sent = await msg.copy_to(ADMIN_ID)

    msg_map[info_msg.message_id] = uid
    msg_map[sent.message_id] = uid

    confirm_texts = {
        "sub": "💬 تم إرسال طلبك إلى قسم الاشتراكات\n📍 يرجى الانتظار لحين الرد من فريق الاشتراكات",
        "dev": "💬 تم إرسال رسالتك إلى قسم المطور\n📍 يرجى الانتظار لحين الرد من فريق التطوير",
        "ads": "💬 تم إرسال طلبك إلى قسم الإعلانات\n📍 يرجى الانتظار لحين الرد من فريق الإعلانات",
        "report": "🚨 تم استلام البلاغ بنجاح\n📩 تم تحويله إلى قسم البلاغات\n📍 سيتم مراجعته من قبل فريق البلاغات قريباً",
        "help": "📩 تم إرسال رسالتك إلى الإدارة بنجاح\n💬 سيتم الرد عليك في أقرب وقت ممكن"
    }

    await msg.answer(confirm_texts.get(section, confirm_texts["help"]))

# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
