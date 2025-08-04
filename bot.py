import telebot
from telebot import types
from datetime import datetime, timedelta

TOKEN = "7996519892:AAGl1jJS5pbOmJCBiJDiyYmhWqEmRn6ixmM"
ADMIN_GROUP_ID = -1002593269045

bot = telebot.TeleBot(TOKEN)
users = {}

def has_access(user_id):
    user = users.get(user_id)
    if not user:
        return False
    if user["paid"]:
        return True
    return (datetime.now() - user["start_date"]) < timedelta(days=7)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {"start_date": now, "paid": False}

    name = f"@{username}" if username else f"ID: {user_id}"
    text = f"""👋 Привет, {name}!

Добро пожаловать в *ChatSaver Bot* — твой надёжный помощник для сохранения:
📥 Удалённых сообщений  
📸 Самоудаляющихся медиа  
🗑️ Чатов, даже если они удалены у всех

🆓 У тебя есть *бесплатная неделя* использования!  
После 7 дней потребуется подписка — *99₽ в месяц*.

Нажми на кнопку ниже, чтобы увидеть инструкцию по активации:
"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⚙️ Активировать бота", callback_data="show_instructions"))
    bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=kb)

@bot.callback_query_handler(lambda c: c.data == "show_instructions")
def show_instructions(call):
    instructions = """📌 *Как активировать ChatSaver Bot:*

1️⃣ Добавь бота в нужный чат и разреши читать сообщения.  
2️⃣ Он автоматически сохранит удалённые сообщения и медиа.  
3️⃣ Если удалишь сообщение после окончания бесплатного периода — придёт уведомление с кнопкой 👀 _Посмотреть_.  
4️⃣ После нажатия на неё ты увидишь мои реквизиты:  
💳 +7 932 222 99 30 (Ozon Bank), 99₽/мес  
5️⃣ Отправь текст *Оплатил(а)*, и админ активирует тебе доступ.

🛠 Всё просто, интуитивно и удобно!"""
    bot.send_message(call.from_user.id, instructions, parse_mode='Markdown')

@bot.message_handler(lambda m: not has_access(m.from_user.id))
def blocked_handler(message):
    text = "❗ Бесплатный период закончился, доступ заблокирован.\n\n"
    bot.send_message(message.from_user.id, text)

@bot.message_handler(lambda m: has_access(m.from_user.id) and m.text and "deleted_test:" in m.text)
def simulate_deleted(message):
    # эмуляция: если пришло "deleted_test: <текст>" — показываем уведомление
    deleted_text = message.text.split("deleted_test:",1)[1].strip()
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👀 Посмотреть", callback_data="view_payment"))
    bot.send_message(message.from_user.id,
                     f"⚠️ Кто-то удалил сообщение:\n{deleted_text}\n" +
                     "Сообщение сохранено, но скрыто.",
                     reply_markup=kb)

@bot.callback_query_handler(lambda c: c.data == "view_payment")
def show_payment(call):
    payment_info = """💳 *Реквизиты для оплаты:*

+7 932 222 99 30  
Ozon Bank  
Сумма: 99₽ в месяц

После оплаты отправь сообщение _Оплатил(а)_ — и админ активирует подписку."""
    bot.send_message(call.from_user.id, payment_info, parse_mode='Markdown')

@bot.message_handler(lambda m: m.text and m.text.lower() in ["оплатил", "оплатил(а)"])
def handle_paid(message):
    uid = message.from_user.id
    username = message.from_user.username or str(uid)
    now = datetime.now().strftime("%Y‑%m‑%d %H:%M:%S")
    users.setdefault(uid, {"start_date": now, "paid": False})
    msg = (f"💸 *Пользователь сообщил об оплате!*\n\n"
           f"👤 @{username}\n"
           f"🆔 {uid}\n"
           f"🕒 {now}\n"
           f"Сумма: 99₽")
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_{uid}"))
    bot.send_message(ADMIN_GROUP_ID, msg, parse_mode='Markdown', reply_markup=kb)
    bot.send_message(uid, "⌛ Спасибо! Ждём подтверждения от администратора.")

@bot.callback_query_handler(lambda c: c.data.startswith("confirm_"))
def confirm_call(call):
    uid = int(call.data.split("_")[1])
    users[uid]["paid"] = True
    bot.send_message(uid, "✅ Подписка активирована! Бот работает без ограничений 🎉")
    bot.send_message(ADMIN_GROUP_ID, f"🔓 Подписка для {uid} активирована.")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

print("🤖 Bot is running...")
bot.infinity_polling()
