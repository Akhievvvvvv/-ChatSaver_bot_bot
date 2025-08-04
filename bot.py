import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

TOKEN = "7996519892:AAGl1jJS5pbOmJCBiJDiyYmhWqEmRn6ixmM"
ADMIN_GROUP_ID = -1002593269045
PAYMENT_REQUISITES = "Оплата на номер: 89322229930 (Ozon bank)\nСумма: 99₽ в месяц"

bot = telebot.TeleBot(TOKEN)

# Хранилище пользователей (лучше потом заменить на БД)
users = {}

def get_username_or_id(user):
    if user.username:
        return f"@{user.username}"
    return str(user.id)

# Кнопка для подтверждения оплаты
def admin_confirm_button(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_{user_id}"))
    return keyboard

# Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = get_username_or_id(message.from_user)
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {
            "start_date": now,
            "paid": False
        }
        text = (
            f"👋 Привет, {username}!\n\n"
            "Добро пожаловать в *ChatSaver Bot* — твой помощник для сохранения удалённых сообщений, самоудаляющихся медиа и всего чата.\n\n"
            "🚀 *Что бот умеет?*\n"
            "- Сохраняет удалённые сообщения 📥\n"
            "- Сохраняет самоудаляющиеся фото, видео и голосовые 📸\n"
            "- Сохраняет чат, даже если он удалён у всех 🗑️\n\n"
            "🆓 Тебе доступна *бесплатная неделя* использования!\n"
            "После 7 дней потребуется оформить подписку за 99₽ в месяц.\n\n"
            "💳 Чтобы оплатить, отправь сообщение с текстом: *Оплатил(а)*\n"
            "После оплаты администратор проверит и активирует доступ.\n\n"
            "Если возникнут вопросы — пиши сюда.\n\n"
            "Приятного использования! 🤖"
        )
        bot.send_message(user_id, text, parse_mode='Markdown')
    else:
        bot.send_message(user_id, "✅ Ты уже активировал бота!")

# Обработка оплаты пользователем
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ["оплатил", "оплатил(а)"])
def handle_paid(message):
    user_id = message.from_user.id
    username = get_username_or_id(message.from_user)
    now = datetime.now()
    msg = (
        f"💸 *Поступила заявка на оплату!*\n\n"
        f"Пользователь: {username}\n"
        f"ID: {user_id}\n"
        f"Время: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{PAYMENT_REQUISITES}"
    )
    bot.send_message(message.chat.id, "⌛ Ожидай подтверждения от админа.")
    bot.send_message(ADMIN_GROUP_ID, msg, parse_mode='Markdown', reply_markup=admin_confirm_button(user_id))

# Обработка нажатия кнопки подтверждения оплаты в админ-группе
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def callback_confirm_payment(call):
    if call.message.chat.id != ADMIN_GROUP_ID:
        bot.answer_callback_query(call.id, "Это действие доступно только админам.")
        return

    user_id_str = call.data.split("_")[1]
    try:
        user_id = int(user_id_str)
    except ValueError:
        bot.answer_callback_query(call.id, "Некорректный ID пользователя.")
        return

    if user_id in users:
        users[user_id]["paid"] = True
        bot.send_message(user_id, "✅ Ваша подписка активирована! Спасибо за оплату, бот теперь работает без ограничений.")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🔓 Оплата подтверждена пользователем с ID: {user_id}. Подписка активирована.",
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "Подписка активирована!")
    else:
        bot.answer_callback_query(call.id, "Пользователь не найден.")

# Проверка доступа пользователя
def has_access(user_id):
    user = users.get(user_id)
    if not user:
        return False
    if user["paid"]:
        return True
    return (datetime.now() - user["start_date"]) < timedelta(days=7)

# Здесь будет логика для сохранения удалённых сообщений (пока заглушка)
# ...

bot.infinity_polling()
