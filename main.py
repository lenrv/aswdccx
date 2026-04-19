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

        if call.data == "sub":
    await call.message.answer(
        "💬 **ارسل الان رسالتك للاشتراك في الكلوزات**\n"
        "📍 سيتم تحويلك إلى قسم الاشتراكات",
        reply_markup=cancel_button()
    )

        elif call.data == "dev":
            await call.message.answer("💬 **ارسل الان رسالتك للتواصل مع المطور**

📍 سيتم تحويل رسالتك إلى المطور البوت", reply_markup=cancel_button())

        elif call.data == "ads":
            await call.message.answer("💬 **ارسل الان رسالتك للاشتراك في الإعلانات أو استفسار عن الإعلانات**

📍 سيتم تحويل رسالتك إلى قسم الإعلانات", reply_markup=cancel_button())

        elif call.data == "report":
            await call.message.answer("🚨 **ارسل الان بلاغك أو تقديم بلاغ
👮🏼‍♂️ ارسل مشكلتك بالتفصيل**
📍سيتم تحويل رسالتك إلى قسم البلاغات", reply_markup=cancel_button())

        elif call.data == "help":
            await call.message.answer("⚠️ دليل استخدام البوت

━━━━━━━━━━━━━━

🔞 الاشتراك في الكلوزات (VIP)  
يمكنك الاشتراك في قائمة الاشتراكات المميزة مثل الكلوزات وغيرها من المحتويات المتاحة.  

📍 للإشتراك أو الاستفسار:  
اضغط على زر "الاشتراك في الكلوزات" من القائمة الرئيسية.

بعدها يمكنك:
• طلب الاشتراك في المحتوى المميز  
• الاستفسار عن التفاصيل المتوفرة  

• 🔞 كلوزر VIP  
• 🔞 أطفال  
• 🔞 بلاص  
• 🔞 خليجي  
• 🔞 اشتراك في 5 قنوات VIP  

⚠️ ملاحظة:  
أرسل اسم الاشتراك الذي تريده وسوف نرسل لك جميع التفاصيل الخاصة بالاشتراك والسعر.

━━━━━━━━━━━━━━

📢 الإعلانات  
اضغط على زر "الإعلانات" من القائمة الرئيسية.  

📍 سيتم تحويلك إلى قسم الإعلانات حيث يمكنك:
• طلب إعلان  
• الاستفسار عن الإعلان  
• متابعة طلبك مع الإدارة

━━━━━━━━━━━━━━

💬 تواصل مع المطور  
اضغط على زر "تواصل المطور" من القائمة الرئيسية.  

📍 في قسم التواصل يمكنك:
• إرسال رسالة للمطور  
• إبلاغ عن مشكله أو تقديم بلاغ مباشر  
• طلب دعم أو مساعدة

━━━━━━━━━━━━━━

🚨 قسم البلاغات

📌 يمكنك تقديم بلاغ أو الإبلاغ عن مشكلة بكل سهولة.  

👮🏼‍♂️ في هذا القسم يمكنك:  
• تقديم بلاغ  
• تقديم بلاغ عن مشكلة  
• إرسال أي ملاحظات أو تفاصيل تريد توضيحها  

📍 بعد إرسال البلاغ سيتم تحويله مباشرة إلى الإدارة لمراجعته والرد عليك بأقرب وقت.  

⚠️ تنبيه:  
يرجى كتابة البلاغ بشكل واضح ومفصل لضمان سرعة التعامل معه.

━━━━━━━━━━━━━━

⚠️ تنبيه:  
يمنع إرسال رسائل مزعجة أو بدون سبب.", reply_markup=cancel_button())

    elif call.data == "cancel":
        await call.message.answer("📋 تم إلغاء الإرسال، العودة للقائمة الرئيسية.",
                                  reply_markup=menu())  # العودة للقائمة الرئيسية
        return

# ---------------- ADMIN (REPLY + STEPS) ----------------
@dp.message(F.from_user.id == ADMIN_ID)
async def admin_handler(msg: Message):
    uid = msg.from_user.id

    if msg.reply_to_message:
        mid = msg.reply_to_message.message_id

        if mid in msg_map:
            user_id = msg_map[mid]
            await msg.copy_to(user_id)
            await msg.answer("✅ تم إرسال الرسالة إلى المستخدم")
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
            chat = await bot.get_chat(ch)

            member = await bot.get_chat_member(chat_id=ch, user_id=ADMIN_ID)
            if member.status not in ["administrator", "creator"]:
                await msg.answer("❌ البوت مو أدمن بالقناة")
                return

        except:
            await msg.answer("❌ القناة غلط أو غير موجودة")
            return

        REQUIRED_CHANNELS.append(ch)
        await msg.answer("✅ تم إضافة القناة بنجاح")
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

# ---------------- USER → ADMIN ----------------
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

    info_msg = await bot.send_message(
        ADMIN_ID,
        f"👤 الاسم: {msg.from_user.full_name}\n"
        f"🔗 اليوزر: @{msg.from_user.username if msg.from_user.username else 'ماكو'}\n"
        f"🆔 الايدي: {uid}\n"
        f"📌 الخدمة: {user_state.get(uid, 'غير محدد')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⛔️ حظر", callback_data=f"ban_{uid}")]
        ])
    )

    sent = await msg.copy_to(ADMIN_ID)

    msg_map[info_msg.message_id] = uid
    msg_map[sent.message_id] = uid

    await msg.answer(
        "📩 تم إرسال رسالتك إلى الإدارة بنجاح\n\n"
        "💬 سيتم الرد عليك في أقرب وقت ممكن"
    )

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
