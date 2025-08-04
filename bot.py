import telebot
from telebot import types
from datetime import datetime, timedelta

TOKEN = "7996519892:AAGl1jJS5pbOmJCBiJDiyYmhWqEmRn6ixmM"
ADMIN_GROUP_ID = -1002593269045

bot = telebot.TeleBot(TOKEN)

users = {}

def get_username_or_id(user):
    return f"@{user.username}" if user.username else f"ID: {user.id}"

# Клавиатура для пользователей
def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("Активировать бота"))
    kb.add(types.KeyboardButton("Оплатил(а)"))
    return kb

# Клавиатура для админов - подтверждение оплаты
def payment_confirm_keyboard(user_id):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_{user_id}"))
    return kb

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = get_username_or_id(message.from_user)
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {
            "start_date": now,
            "paid": False
        }
        welcome_text = (
            f"👋 Привет, {user_name}!\n\n"
            "Добро пожаловать в ChatSaver Bot — твой надёжный помощник для сохранения удалённых сообщений и самоудаляющихся медиа.\n\n"
            "🎁 Тебе доступна *бесплатная неделя* использования бота.\n\n"
            "Чтобы начать, нажми кнопку ниже и следуй инструкции.\n"
        )
        bot.send_message(user_id, welcome_text, parse_mode='Markdown', reply_markup=main_keyboard())
    else:
        bot.send_message(user_id, "✅ Ты уже активировал бота! Используй меню ниже.", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "Активировать бота")
def send_activation_info(message):
    text = (
        "🚀 *Инструкция по активации ChatSaver Bot*\n\n"
        "1️⃣ Нажми кнопку «Оплатил(а)» после оплаты подписки — 99₽ в месяц.\n"
        "2️⃣ Админ получит уведомление и подтвердит твою оплату.\n"
        "3️⃣ После подтверждения бот активируется и начнёт сохранять удалённые сообщения, фото, видео и голосовые.\n\n"
        "🆓 Бесплатный период — 7 дней! После этого нужно оплачивать подписку.\n\n"
        "Если возникнут вопросы — пиши сюда, мы всегда поможем! 😊"
    )
    bot.send_message(message.from_user.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text.lower() in ["оплатил", "оплатил(а)"])
def handle_paid(message):
    user = message.from_user
    user_id = user.id
    user_name = get_username_or_id(user)
    now = datetime.now()

    # Отправляем уведомление в админ-группу с кнопкой подтверждения оплаты
    msg_text = (
        f"💸 *Пользователь оплатил подписку!*\n\n"
        f"👤 Пользователь: {user_name}\n"
        f"🆔 ID: {user_id}\n"
        f"⏰ Время: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"💰 Сумма: 99₽"
    )
    bot.send_message(ADMIN_GROUP_ID, msg_text, parse_mode='Markdown', reply_markup=payment_confirm_keyboard(user_id))
    bot.reply_to(message, "⌛ Ожидай подтверждения от админа. Спасибо за оплату!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_payment(call):
    if call.message.chat.id != ADMIN_GROUP_ID:
        bot.answer_callback_query(call.id, "⚠️ Эта кнопка только для админов.")
        return

    user_id_str = call.data.split("_")[1]
    try:
        user_id = int(user_id_str)
    except:
        bot.answer_callback_query(call.id, "⚠️ Неверный ID пользователя.")
        return

    if user_id in users:
        users[user_id]["paid"] = True
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        bot.send_message(user_id, "✅ Ваша подписка активирована! Теперь бот работает без ограничений.")
        bot.send_message(ADMIN_GROUP_ID, f"🔓 Пользователь {user_id} успешно активирован.")
        bot.answer_callback_query(call.id, "Подписка подтверждена и активирована.")
    else:
        bot.answer_callback_query(call.id, "⚠️ Пользователь не найден.")

def has_access(user_id):
    user = users.get(user_id)
    if not user:
        return False
    if user["paid"]:
        return True
    return (datetime.now() - user["start_date"]) < timedelta(days=7)

# Здесь добавляйте логику сохранения удалённых сообщений и прочее

bot.infinity_polling()
