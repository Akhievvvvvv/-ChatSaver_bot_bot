import telebot
from telebot import types
from datetime import datetime, timedelta

TOKEN = "7996519892:AAGl1jJS5pbOmJCBiJDiyYmhWqEmRn6ixmM"
ADMIN_GROUP_ID = -1002593269045

bot = telebot.TeleBot(TOKEN)
users = {}

# 📌 Проверка доступа
def has_access(user_id):
    user = users.get(user_id)
    if not user:
        return False
    if user["paid"]:
        return True
    return (datetime.now() - user["start_date"]) < timedelta(days=7)

# 📍 /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {"start_date": now, "paid": False}

    name = f"@{username}" if username else f"ID: {user_id}"

    welcome_text = f"""👋 Привет, {name}!

Добро пожаловать в *ChatSaver Bot* — твой личный помощник для сохранения:

📥 Удалённых сообщений  
📸 Самоудаляющихся фото, видео и голосовых  
🗑️ Чатов, даже если они удалены у всех

🆓 Тебе доступна *бесплатная неделя* использования!  
После 7 дней потребуется оформить подписку — *99₽ в месяц*.

💳 Для оплаты: *+7 932 222 99 30 (Ozon Bank)*  
После перевода нажми кнопку *Оплатил(а)* (будет доступна после пробного периода).

Если возникнут вопросы — пиши сюда.  
Приятного использования! 🤖"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Активировать бота", callback_data="activate_bot"))
    bot.send_message(user_id, welcome_text, reply_markup=markup, parse_mode='Markdown')

# ▶️ Инструкция
@bot.callback_query_handler(func=lambda call: call.data == "activate_bot")
def send_instructions(call):
    user_id = call.from_user.id
    instructions = """🔧 *Как работает бот:*

1️⃣ Просто добавь бота в свой чат  
2️⃣ Дай ему права администратора  
3️⃣ Готово — он начнёт сохранять удалённые сообщения и медиа!

📅 Первые 7 дней бесплатно  
🕒 После — подписка за 99₽ в месяц

При удалении сообщений после пробного периода ты получишь уведомление с кнопкой 👀 *Посмотреть* — нажав на неё, появятся реквизиты для оплаты.
"""
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=instructions, parse_mode='Markdown')

# 🧾 Обработка "Оплатил(а)"
@bot.message_handler(func=lambda m: m.text.lower() in ["оплатил", "оплатил(а)"])
def handle_paid(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"ID: {user_id}"
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    msg = f"""💸 *Пользователь сообщил об оплате!*

👤 {username}  
🆔 {user_id}  
⏰ {now}  
💰 Сумма: 99₽"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_{user_id}"))
    bot.send_message(ADMIN_GROUP_ID, msg, reply_markup=markup, parse_mode='Markdown')
    bot.reply_to(message, "⌛ Ожидай подтверждения от админа...")

# ✅ Подтверждение админом
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_payment(call):
    if call.message.chat.id != ADMIN_GROUP_ID:
        return

    user_id = int(call.data.split("_")[1])
    users[user_id]["paid"] = True
    bot.send_message(user_id, "✅ Подписка активирована! Спасибо за оплату 🎉")
    bot.send_message(ADMIN_GROUP_ID, f"🔓 Пользователь {user_id} активирован.")

# 📦 Обработка удаления сообщений после окончания пробного
@bot.message_handler(func=lambda m: not has_access(m.from_user.id))
def restricted_content(message):
    user_id = message.from_user.id
    if (datetime.now() - users[user_id]["start_date"]) >= timedelta(days=7):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👀 Посмотреть", callback_data="show_payment_info"))
        bot.send_message(user_id, "❗ Кто-то что-то удалил...\nНо это скрыто, так как пробный период закончился.", reply_markup=markup)

# 💳 Реквизиты
@bot.callback_query_handler(func=lambda call: call.data == "show_payment_info")
def show_payment_info(call):
    user_id = call.from_user.id
    payment_info = """💳 *Оплата подписки*

Переведи *99₽* на номер:  
📱 +7 932 222 99 30  
🏦 Ozon Bank

После перевода отправь сообщение: *Оплатил(а)*"""
    bot.send_message(user_id, payment_info, parse_mode='Markdown')

bot.polling()
