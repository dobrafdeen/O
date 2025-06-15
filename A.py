import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
from datetime import datetime, timedelta
import time
import json
import os

ADMIN_IDS = [7757640905, 6873334348]
PRIMARY_ADMIN_ID = ADMIN_IDS[0]
admins = set(ADMIN_IDS)  # مجموعة المشرفين

BOT_TOKEN = "7632274914:AAFOBZmxLTnvj71QOvILscHESkwHQ6uhJeM"
CHANNEL_ID = -1002567282934

bot = telebot.TeleBot(BOT_TOKEN)
DATA_FILE = "subscriptions.json"

subscriptions = {}
pending_approvals = set()
pending_renewals = set()
last_action_times = {}  # user_id: {"action": last_datetime}

WELCOME_MESSAGE = "🌟 مرحباً بك في القناة!\nنتمنى لك تجربة رائعة ومميزة معنا.\nإذا احتجت أي مساعدة يرجى التواصل مع الدعم الفني. 🤗"

def load_subscriptions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            for user_id in raw:
                sub = raw[user_id]
                sub['start'] = datetime.fromisoformat(sub['start'])
                sub['end'] = datetime.fromisoformat(sub['end'])
            return {int(uid): sub for uid, sub in raw.items()}
    return {}

def save_subscriptions():
    raw = {}
    for user_id, sub in subscriptions.items():
        raw[str(user_id)] = {
            "status": sub["status"],
            "start": sub["start"].isoformat(),
            "end": sub["end"].isoformat(),
            "notified": sub["notified"],
            "notified_expired": sub.get("notified_expired", False),
            "username": sub.get("username", "")
        }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

subscriptions = load_subscriptions()

def main_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("⏳ معرفة الوقت المتبقي", callback_data="mytime"))
    if user_id in subscriptions and subscriptions[user_id]['status'] == 'active':
        keyboard.add(InlineKeyboardButton("🔄 تجديد الاشتراك", callback_data="renew"))
    else:
        keyboard.add(InlineKeyboardButton("🔔 اشترك الآن", callback_data="subscribe"))
    if user_id in admins:
        keyboard.add(InlineKeyboardButton("👥 لوحة المشرف", callback_data="admin_panel"))
    return keyboard

def approve_keyboard(user_id, is_renew=False):
    keyboard = InlineKeyboardMarkup()
    if is_renew:
        keyboard.add(InlineKeyboardButton("✅ موافقة تجديد", callback_data=f"approve_renew_{user_id}"))
    else:
        keyboard.add(InlineKeyboardButton("✅ موافقة اشتراك", callback_data=f"approve_{user_id}"))
    return keyboard

def admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("👥 عرض المشتركين", callback_data="list_users"))
    keyboard.add(InlineKeyboardButton("⏩ زيادة مدة", callback_data="extend_reduce_menu"))
    keyboard.add(InlineKeyboardButton("🚫 حظر مستخدم", callback_data="ban_user_menu"))
    keyboard.add(InlineKeyboardButton("👤 حذف/عرض المشرفين", callback_data="show_remove_admins_menu"))
    keyboard.add(InlineKeyboardButton("💬 إضافة رسالة ترحيب", callback_data="add_welcome_message"))
    return keyboard

def extend_reduce_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("📅 زيادة شهر", callback_data="add_month"),
        InlineKeyboardButton("📅 زيادة 3 شهور", callback_data="add_3months"),
    )
    keyboard.add(
        InlineKeyboardButton("📅 زيادة 6 شهور", callback_data="add_6months"),
    )
    keyboard.add(InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel"))
    return keyboard

def choose_user_keyboard(action):
    keyboard = InlineKeyboardMarkup()
    now = datetime.now()
    for user_id, sub in subscriptions.items():
        if sub['status'] == 'active' and (sub['end'] - now).total_seconds() > 0:
            username = sub.get("username", "")
            show = f"{username or user_id}"
            keyboard.add(InlineKeyboardButton(show, callback_data=f"{action}_{user_id}"))
    keyboard.add(InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel" if action == "banuser" else "extend_reduce_menu"))
    return keyboard

def can_do_action(user_id, action):
    now = datetime.now()
    user_times = last_action_times.get(user_id, {})
    last_time = user_times.get(action)
    if last_time and (now - last_time).total_seconds() < 60:
        return False
    if user_id not in last_action_times:
        last_action_times[user_id] = {}
    last_action_times[user_id][action] = now
    return True

# ============ المشتركين =============

def users_list_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ إضافة مشترك", callback_data="add_user_menu"))
    keyboard.add(InlineKeyboardButton("🛠️ تعديل مدة المشترك", callback_data="edit_user_duration_menu"))
    keyboard.add(InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel"))
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data == "list_users")
def list_users_button(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    msg = "👥 قائمة المشتركين:\n\n"
    now = datetime.now()
    count = 0
    for user_id, sub in subscriptions.items():
        if sub['status'] == 'active':
            remain = subscriptions[user_id]['end'] - now
            if remain.total_seconds() > 0:
                days = remain.days
                hours, remainder = divmod(remain.seconds, 3600)
                username = sub.get("username", "")
                msg += f"• {username or user_id}: باقي {days} يوم و {hours} ساعة\n"
                count += 1
    if count == 0:
        msg += "لا يوجد مشتركين نشطين حالياً."
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=users_list_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "add_user_menu")
def add_user_menu(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    msg = (
        "أرسل رقم معرف المستخدم (ID) الذي تريد إضافته كعضو مشترك.\n"
        "يمكنك أيضًا كتابة اسم المستخدم (username) في الرسالة إذا أردت."
    )
    bot.send_message(call.from_user.id, msg)
    bot.answer_callback_query(call.id)
    bot.register_next_step_handler_by_chat_id(call.from_user.id, receive_new_user_id)

def receive_new_user_id(message):
    try:
        parts = message.text.split()
        user_id = int(parts[0])
        username = parts[1] if len(parts) > 1 else ""
        now = datetime.now()
        subscriptions[user_id] = {
            'status': 'active',
            'start': now,
            'end': now + timedelta(days=30),
            'notified': False,
            'notified_expired': False,
            'username': username
        }
        save_subscriptions()
        bot.reply_to(message, f"✅ تم إضافة المستخدم {user_id} كعضو مشترك لمدة 30 يوم.")
    except Exception:
        bot.reply_to(message, "يرجى إرسال رقم معرف المستخدم بشكل صحيح (يمكنك إضافة اسم المستخدم بعده اختيارياً).")

@bot.callback_query_handler(func=lambda call: call.data == "edit_user_duration_menu")
def edit_user_duration_menu(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    # قائمة المشتركين النشطين فقط
    keyboard = InlineKeyboardMarkup()
    now = datetime.now()
    for user_id, sub in subscriptions.items():
        if sub['status'] == 'active' and (sub['end'] - now).total_seconds() > 0:
            username = sub.get("username", "")
            show = f"{username or user_id}"
            keyboard.add(InlineKeyboardButton(show, callback_data=f"edit_user_{user_id}"))
    keyboard.add(InlineKeyboardButton("⬅️ رجوع", callback_data="list_users"))
    bot.edit_message_text("اختر المستخدم لتعديل مدة اشتراكه:", call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_user_"))
def edit_user_selected(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    user_id = int(call.data.split("_")[2])
    msg = (
        f"أدخل الآن عدد الأيام الجديدة لاشتراك المستخدم {user_id}.\n"
        "مثال: 45 (لتعيين الاشتراك 45 يوم من الآن)"
    )
    bot.send_message(call.from_user.id, msg)
    bot.answer_callback_query(call.id)
    bot.register_next_step_handler_by_chat_id(call.from_user.id, lambda m: receive_new_duration(m, user_id))

def receive_new_duration(message, user_id):
    try:
        days = int(message.text)
        now = datetime.now()
        if user_id in subscriptions:
            subscriptions[user_id]['start'] = now
            subscriptions[user_id]['end'] = now + timedelta(days=days)
            save_subscriptions()
            bot.reply_to(message, f"✅ تم تعديل مدة اشتراك المستخدم {user_id} إلى {days} يوم من الآن.")
        else:
            bot.reply_to(message, "لم يتم العثور على هذا المستخدم في المشتركين.")
    except Exception:
        bot.reply_to(message, "يرجى إدخال عدد الأيام بشكل صحيح (رقم فقط).")

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bot.send_message(
        user_id,
        WELCOME_MESSAGE + "\n\nاستخدم الأزرار في الأسفل لإدارة اشتراكك:",
        reply_markup=main_keyboard(user_id)
    )

@bot.callback_query_handler(func=lambda call: call.data == "mytime")
def mytime_button(call):
    user_id = call.from_user.id
    now = datetime.now()
    if user_id in subscriptions and subscriptions[user_id]['status'] == 'active':
        remain = subscriptions[user_id]['end'] - now
        if remain.total_seconds() > 0:
            days = remain.days
            hours, remainder = divmod(remain.seconds, 3600)
            msg = f"⏳ متبقي: {days} يوم و {hours} ساعة"
            bot.answer_callback_query(call.id, msg, show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❖ انتهى اشتراكك.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❖ ليس لديك اشتراك نشط.", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel_button(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    bot.edit_message_text("لوحة المشرف:", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_keyboard())
    bot.answer_callback_query(call.id)
    
@bot.callback_query_handler(func=lambda call: call.data == "extend_reduce_menu")
def extend_reduce_menu(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    bot.edit_message_text("اختر الإجراء:", call.message.chat.id, call.message.message_id, reply_markup=extend_reduce_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "ban_user_menu")
def ban_user_menu(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    bot.edit_message_text("اختر المستخدم الذي تريد حظره:", call.message.chat.id, call.message.message_id, reply_markup=choose_user_keyboard("banuser"))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("banuser_"))
def ban_selected_user(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    user_id = int(call.data.split("_")[1])
    try:
        bot.ban_chat_member(CHANNEL_ID, user_id)
        subscriptions[user_id]['status'] = 'banned'
        save_subscriptions()
        bot.edit_message_text(f"🚫 تم حظر المستخدم {subscriptions[user_id].get('username', user_id)} بنجاح.", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_keyboard())
        try:
            bot.send_message(user_id, "🚫 تمت ازالتك من القناة وإنهاء اشتراكك من قبل الإدارة.")
        except Exception:
            pass
    except Exception:
        bot.edit_message_text("حدث خطأ أثناء محاولة الحظر!", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data in ["add_month", "add_3months", "add_6months"])
def choose_user_for_action(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    act = call.data
    act_name = {
        "add_month": "زيادة شهر",
        "add_3months": "زيادة 3 شهور",
        "add_6months": "زيادة 6 شهور",
    }
    bot.edit_message_text(
        f"اختر المستخدم لتطبيق إجراء '{act_name[act]}' عليه:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=choose_user_keyboard(act)
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call:
    call.data.startswith("add_month_") or
    call.data.startswith("add_3months_") or
    call.data.startswith("add_6months_")
)
def extend_reduce_apply(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    parts = call.data.split("_")
    if parts[1] == "month":
        action = "add_month"
        user_id = int(parts[2])
    elif parts[1] == "3months":
        action = "add_3months"
        user_id = int(parts[2])
    elif parts[1] == "6months":
        action = "add_6months"
        user_id = int(parts[2])
    else:
        bot.answer_callback_query(call.id, "حدث خطأ في المعرف.", show_alert=True)
        return
    handle_extend_reduce(user_id, action, call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

def handle_extend_reduce(user_id, action, chat_id, message_id):
    now = datetime.now()
    if user_id not in subscriptions or subscriptions[user_id]['status'] != 'active':
        bot.edit_message_text("✖ المستخدم ليس لديه اشتراك نشط.", chat_id, message_id, reply_markup=admin_panel_keyboard())
        return
    msg = ""
    if action == "add_month":
        subscriptions[user_id]['end'] += timedelta(days=30)
        msg = "✅ تم زيادة شهر للاشتراك."
    elif action == "add_3months":
        subscriptions[user_id]['end'] += timedelta(days=90)
        msg = "✅ تم زيادة 3 شهور للاشتراك."
    elif action == "add_6months":
        subscriptions[user_id]['end'] += timedelta(days=180)
        msg = "✅ تم زيادة 6 شهور للاشتراك."
    save_subscriptions()
    bot.edit_message_text(msg, chat_id, message_id, reply_markup=admin_panel_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "subscribe")
def subscribe_handler(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    if not can_do_action(user_id, "subscribe"):
        bot.send_message(user_id, "تم ارسال طلبك بالفعل يرجى الانتظار..")
        return
    if user_id in subscriptions and subscriptions[user_id]['status'] == 'active':
        bot.send_message(user_id, "أنت بالفعل مشترك!")
        return
    if user_id in pending_approvals:
        bot.send_message(user_id, "طلبك بانتظار موافقة المشرف.")
        return
    bot.send_message(user_id, "جاري المعالجة...")
    time.sleep(1)
    pending_approvals.add(user_id)
    bot.send_message(
        PRIMARY_ADMIN_ID,
        f"طلب جديد للاشتراك من @{call.from_user.username or user_id}.",
        reply_markup=approve_keyboard(user_id)
    )
    try:
        bot.send_message(user_id, "يرجى التواصل مع الدعم الفني على @ArabTradingSupport لإتمام عملية الاشتراك.")
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "renew")
def renew_handler(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    if not can_do_action(user_id, "renew"):
        bot.send_message(user_id, "تم ارسال طلبك بالفعل يرجى الانتظار.")
        return
    if user_id not in subscriptions or subscriptions[user_id]['status'] != 'active':
        bot.send_message(user_id, "أنت غير مشترك حالياً!")
        return
    if user_id in pending_renewals:
        bot.send_message(user_id, "طلبك بانتظار موافقة المشرف.")
        return
    bot.send_message(user_id, "جاري المعالجة...")
    time.sleep(1)
    pending_renewals.add(user_id)
    bot.send_message(
        PRIMARY_ADMIN_ID,
        f"طلب تجديد من @{call.from_user.username or user_id}.",
        reply_markup=approve_keyboard(user_id, is_renew=True)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_handler(call):
    data = call.data
    user_id = int(data.split("_")[-1])
    action_type = "approve_renew" if data.startswith("approve_renew_") else "approve"
    bot.answer_callback_query(call.id)
    if not can_do_action(user_id, action_type):
        bot.send_message(call.from_user.id, "تمت الموافقة بالفعل مؤخراً لهذا المستخدم.")
        return
    time.sleep(1)
    now = datetime.now()
    username = None
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        username = member.user.username
    except Exception:
        username = None
    if data.startswith("approve_renew_"):
        if user_id not in subscriptions or subscriptions[user_id]['status'] != 'active':
            bot.send_message(call.from_user.id, "المستخدم ليس لديه اشتراك نشط.")
            return
        subscriptions[user_id]['end'] = subscriptions[user_id]['end'] + timedelta(days=30)
        subscriptions[user_id]['notified'] = False
        subscriptions[user_id]['notified_expired'] = False
        pending_renewals.discard(user_id)
        save_subscriptions()
        try:
            bot.unban_chat_member(CHANNEL_ID, user_id)
            bot.approve_chat_join_request(CHANNEL_ID, user_id)
        except Exception as e:
            print("Join request error:", e)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_message(user_id, "✅ تم تجديد اشتراكك بنجاح لمدة 30 يوماً. وتمت الموافقة على دخولك القناة إذا كان لديك طلب انضمام معلق.", reply_markup=main_keyboard(user_id))
    else:
        subscriptions[user_id] = {
            'status': 'active',
            'start': now,
            'end': now + timedelta(days=30),
            'notified': False,
            'notified_expired': False,
            'username': username or ""
        }
        pending_approvals.discard(user_id)
        save_subscriptions()
        try:
            bot.unban_chat_member(CHANNEL_ID, user_id)
            bot.approve_chat_join_request(CHANNEL_ID, user_id)
        except Exception as e:
            print("Join request error:", e)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_message(user_id, f"✅ تم تفعيل اشتراكك لمدة 30 يوماً في القناة. وتمت الموافقة على دخولك القناة إذا كان لديك طلب انضمام معلق.", reply_markup=main_keyboard(user_id))

# --------- إدارة المشرفين ---------
@bot.callback_query_handler(func=lambda call: call.data == "show_remove_admins_menu")
def show_remove_admins_menu(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    keyboard = InlineKeyboardMarkup()
    for admin_id in admins:
        if admin_id == PRIMARY_ADMIN_ID:
            continue
        keyboard.add(InlineKeyboardButton(f"❌ حذف مشرف {admin_id}", callback_data=f"remove_admin_{admin_id}"))
    keyboard.add(InlineKeyboardButton("➕ إضافة مشرف", callback_data="add_admin_menu"))
    keyboard.add(InlineKeyboardButton("⬅️ رجوع للوحة المشرف", callback_data="admin_panel"))
    msg = "قائمة المشرفين الحاليين:\n" + "\n".join([str(a) for a in admins])
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_admin_"))
def remove_admin(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    admin_id = int(call.data.split("_")[2])
    if admin_id == PRIMARY_ADMIN_ID:
        bot.answer_callback_query(call.id, "لا يمكن حذف المشرف الأساسي!", show_alert=True)
        return
    if admin_id in admins:
        admins.remove(admin_id)
        bot.answer_callback_query(call.id, f"تم حذف المشرف {admin_id} بنجاح.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "المشرف غير موجود!", show_alert=True)
    show_remove_admins_menu(call)

@bot.callback_query_handler(func=lambda call: call.data == "add_admin_menu")
def add_admin_menu(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    msg = "أرسل الآن رقم معرف المستخدم (ID) الذي تريد منحه صلاحية المشرف:"
    bot.send_message(call.from_user.id, msg)
    bot.answer_callback_query(call.id)
    bot.register_next_step_handler_by_chat_id(call.from_user.id, receive_admin_id)

def receive_admin_id(message):
    try:
        new_admin_id = int(message.text)
        if new_admin_id in admins:
            bot.reply_to(message, "المستخدم بالفعل مشرف.")
        else:
            admins.add(new_admin_id)
            bot.reply_to(message, f"تم إضافة المستخدم {new_admin_id} كمشرف بنجاح!")
    except Exception:
        bot.reply_to(message, "يرجى إرسال رقم المعرف بشكل صحيح (أرقام فقط).")

# --------- رسالة الترحيب ---------
@bot.callback_query_handler(func=lambda call: call.data == "add_welcome_message")
def add_welcome_message(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "غير مصرح!", show_alert=True)
        return
    msg = "أرسل الآن نص رسالة الترحيب الجديدة:"
    bot.send_message(call.from_user.id, msg)
    bot.answer_callback_query(call.id)
    bot.register_next_step_handler_by_chat_id(call.from_user.id, receive_welcome_message)

def receive_welcome_message(message):
    global WELCOME_MESSAGE
    WELCOME_MESSAGE = message.text
    bot.reply_to(message, "تم تحديث رسالة الترحيب بنجاح!")

def subscription_checker():
    while True:
        now = datetime.now()
        for user_id, sub in list(subscriptions.items()):
            if sub['status'] != 'active':
                continue
            seconds_left = int((sub['end'] - now).total_seconds())
            if 0 < seconds_left <= 259200 and not sub['notified']:
                try:
                    subscriptions[user_id]['notified'] = True
                    save_subscriptions()
                    bot.send_message(
                        user_id,
                        "⚠️ بقي على انتهاء اشتراكك 3 أيام! يرجى التجديد لتجنب ازالتك من قبل البوت , مع كامل الإحترام لك",
                        reply_markup=main_keyboard(user_id)
                    )
                except Exception:
                    pass
            if seconds_left <= 0 and not sub.get('notified_expired', False):
                subscriptions[user_id]['status'] = 'expired'
                subscriptions[user_id]['notified_expired'] = True
                save_subscriptions()
                try:
                    bot.ban_chat_member(CHANNEL_ID, user_id)
                except Exception:
                    pass
                try:
                    bot.send_message(user_id, "✖ انتهى اشتراكك وتمت ازالتك من القناة بشكل تلقائي , نعتذر لذلك إذا كنت تريد تجديد اشتراكك يرجى التواصل مع الدعم الفني ", reply_markup=main_keyboard(user_id))
                except Exception:
                    pass
        time.sleep(5)

threading.Thread(target=subscription_checker, daemon=True).start()
print("Bot is running...")
bot.infinity_polling()