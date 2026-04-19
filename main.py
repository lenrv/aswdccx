# Telegram Bot - Full Support System + Mandatory Subscription

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

API_TOKEN = "8789764033:AAHuULIxUvtOZkD7j2cGuJENZrUu76mVbeI"
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
            m = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if m.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ---------------- FORCE JOIN ----------------
def join_kb():
    kb = []
    for ch in REQUIRED_CHANNELS:
        kb.append([InlineKeyboardButton(text=f"📢 اشتراك {ch}", url=f"https://t.me/{ch.replace('@','')}")])
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

    elif call.data == "sub":
        user_state[uid] = "اشتراك"
        await call.message.answer("💬 ارسل رسالتك للاشتراك")

    elif call.data == "dev":
        user_state[uid] = "مطور"
        await call.message.answer("💬 ارسل رسالتك للمطور")

    elif call.data == "ads":
        user_state[uid] = "إعلانات"
        await call.message.answer("💬 ارسل طلب الإعلان")

    elif call.data == "report":
        user_state[uid] = "بلاغات"
        await call.message.answer("🚨 ارسل بلاغك")

    elif call.data == "help":
        await call.message.answer("📮 المساعدة")

# ---------------- ADMIN STEPS ----------------
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_steps(msg: Message):

    uid = msg.from_user.id

    if uid not in admin_step:
        return

    step = admin_step[uid]

    if step == "add_channel":
        ch = msg.text.strip()

        if not ch.startswith("@"):
            await msg.answer("⚠️ ارسل @ صحيح")
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
            await msg.answer("⚠️ غير موجودة")

        admin_step.pop(uid)

    elif step == "ban":
        try:
            banned_users.add(int(msg.text))
            await msg.answer("⛔️ تم الحظر")
        except:
            await msg.answer("⚠️ خطأ ID")

        admin_step.pop(uid)

    elif step == "unban":
        try:
            banned_users.discard(int(msg.text))
            await msg.answer("✅ تم فك الحظر")
        except:
            await msg.answer("⚠️ خطأ ID")

        admin_step.pop(uid)

# ---------------- USER MESSAGES ----------------
@dp.message()
async def all_messages(msg: Message):

    if msg.from_user.id == ADMIN_ID:
        return

    if msg.from_user.id in banned_users:
        return

    if not await is_subscribed(msg.from_user.id):
        await msg.answer("⚠️ يجب الاشتراك")
        return

    fwd = await msg.forward(ADMIN_ID)
    msg_map[fwd.message_id] = msg.from_user.id

    # 🔥 رسالة التأكيد الجديدة
    await msg.answer(
        "📩 تم إرسال رسالتك إلى الإدارة بنجاح\n\n"
        "💬 سيتم الرد عليك في أقرب وقت ممكن"
    )

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
