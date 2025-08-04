import telebot
from datetime import datetime, timedelta

TOKEN = "7996519892:AAGl1jJS5pbOmJCBiJDiyYmhWqEmRn6ixmM"
ADMIN_GROUP_ID = -1002593269045

bot = telebot.TeleBot(TOKEN)

# Хранилище пользователей
users = {}

# Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {
            "start_date": now,
            "paid": False
        }
        bot.send_message(user_id, "👋 Привет! Тебе доступна *бесплатная неделя* использования бота.\n\nЧтобы продолжить после 7 дней — оплати подписку 99₽.", parse_mode='Markdown')
    else:
        bot.send_message(user_id, "✅ Ты уже активировал бота!")

# Кнопка "Оплатил(а)"
@bot.message_handler(func=lambda m: m.text.lower() == "оплатил" or m.text.lower() == "оплатил(а)")
def handle_paid(message):
    user_id = message.from_user.id
    now = datetime.now()
    msg = f"💸 Пользователь оплатил подписку\nID: {user_id}\nВремя: {now.strftime('%Y-%m-%d %H:%M:%S')}\nСумма: 99₽"
    bot.send_message(ADMIN_GROUP_ID, msg)
    bot.reply_to(message, "⌛ Ожидай подтверждения от админа.")

# Подтверждение оплаты (эмуляция)
@bot.message_handler(commands=['confirm'])
def confirm_payment(message):
    if message.chat.id == ADMIN_GROUP_ID:
        try:
            user_id = int(message.text.split()[1])
            if user_id in users:
                users[user_id]["paid"] = True
                bot.send_message(user_id, "✅ Подписка активирована! Бот работает.")
                bot.send_message(ADMIN_GROUP_ID, f"🔓 Пользователь {user_id} активирован.")
        except:
            bot.send_message(ADMIN_GROUP_ID, "⚠️ Укажи ID после команды /confirm")

# Проверка подписки
def has_access(user_id):
    user = users.get(user_id)
    if not user:
        return False
    if user["paid"]:
        return True
    return (datetime.now() - user["start_date"]) < timedelta(days=7)

# Здесь будет логика сохранения удалённых сообщений (в будущем)

bot.polling()
