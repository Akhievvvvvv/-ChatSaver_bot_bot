import telebot
from telebot import types
from datetime import datetime, timedelta

TOKEN = "7996519892:AAGl1jJS5pbOmJCBiJDiyYmhWqEmRn6ixmM"
ADMIN_GROUP_ID = -1002593269045

bot = telebot.TeleBot(TOKEN)

# Хранилище пользователей
users = {}

# Создаём главное меню с кнопками
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📖 Инструкция")
    btn2 = types.KeyboardButton("💳 Оплатил(а)")
    btn3 = types.KeyboardButton("📊 Мой статус")
    btn4 = types.KeyboardButton("❓ Помощь")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "друг"
    now = datetime.now()

    if user_id not in users:
        users[user_id] = {
            "start_date": now,
            "paid": False
        }

    welcome_text = (
        f"👋 Привет, *{user_name}*!\n\n"
        "Я — *ChatSaver Bot* 🤖\n"
        "⚡️ Я сохраняю удалённые сообщения и самоудаляющиеся медиа.\n\n"
        "🆓 У тебя есть *бесплатная неделя* использования.\n"
        "💳 Чтобы продолжить после — оформи подписку за *99₽* в месяц.\n\n"
        "Ниже доступно меню для управления ботом."
    )
    bot.send_message(user_id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# Кнопка Инструкция
@bot.message_handler(func=lambda m: m.text == "📖 Инструкция")
def send_instructions(message):
    instructions = (
        "📚 *Инструкция по использованию ChatSaver Bot:*\n\n"
        "1️⃣ Добавь меня в свои чаты или пиши лично.\n"
        "2️⃣ Я автоматически сохраню удалённые сообщения и медиа.\n"
        "3️⃣ Чтобы продолжить использовать после бесплатной недели — оформи подписку.\n"
        "4️⃣ Для оформления нажми кнопку *Оплатил(а)* и оплати 99₽.\n"
        "5️⃣ Админ подтвердит оплату, и ты получишь полный доступ.\n\n"
        "Если нужна помощь, нажми кнопку *Помощь*."
    )
    bot.send_message(message.from_user.id, instructions, parse_mode="Markdown")

# Кнопка Оплатил(а)
@bot.message_handler(func=lambda m: m.text.lower() in ["💳 оплатил(а)", "оплатил", "оплатил(а)"])
def handle_paid(message):
    user_id = message.from_user.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notification = (
        f"💸 *Поступила заявка на оплату!*\n\n"
        f"👤 Пользователь: [{user_id}](tg://user?id={user_id})\n"
        f"🕒 Время: {now}\n"
        f"💰 Сумма: 99₽"
    )
    bot.send_message(ADMIN_GROUP_ID, notification, parse_mode="Markdown")
    bot.reply_to(message, "⌛ Спасибо! Ожидай подтверждения от администратора.")

# Кнопка Мой статус
@bot.message_handler(func=lambda m: m.text == "📊 Мой статус")
def send_status(message):
    user_id = message.from_user.id
    user = users.get(user_id)
    if not user:
        bot.send_message(user_id, "❌ Ты не активировал бота. Нажми /start для начала.")
        return

    now = datetime.now()
    start = user["start_date"]
    paid = user["paid"]

    if paid:
        status_text = "✅ У тебя активная подписка. Пользуйся без ограничений!"
    else:
        days_left = 7 - (now - start).days
        if days_left > 0:
            status_text = f"🆓 Бесплатная неделя активна. Осталось {days_left} день(ей)."
        else:
            status_text = "❌ Бесплатный период закончился. Чтобы продолжить — оформи подписку."

    bot.send_message(user_id, status_text)

# Кнопка Помощь
@bot.message_handler(func=lambda m: m.text == "❓ Помощь")
def send_help(message):
    help_text = (
        "🆘 *Помощь*\n\n"
        "Если у тебя возникли вопросы или проблемы, напиши сюда:\n"
        "📧 support@example.com\n\n"
        "Или попробуй команду /start для перезапуска бота."
    )
    bot.send_message(message.from_user.id, help_text, parse_mode="Markdown")

# Команда для админа подтверждения оплаты
@bot.message_handler(commands=['confirm'])
def confirm_payment(message):
    if message.chat.id != ADMIN_GROUP_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in users:
            users[user_id]["paid"] = True
            bot.send_message(user_id, "🎉 Ваша подписка подтверждена! Бот полностью активирован.")
            bot.send_message(ADMIN_GROUP_ID, f"🔓 Пользователь {user_id} активирован.")
        else:
            bot.send_message(ADMIN_GROUP_ID, "❌ Пользователь с таким ID не найден.")
    except (IndexError, ValueError):
        bot.send_message(ADMIN_GROUP_ID, "⚠️ Укажи ID пользователя после команды /confirm, например:\n/confirm 123456789")

# Проверка доступа пользователя (в коде пока не используется, но будет нужна)
def has_access(user_id):
    user = users.get(user_id)
    if not user:
        return False
    if user["paid"]:
        return True
    return (datetime.now() - user["start_date"]) < timedelta(days=7)

# Запуск бота
print("🤖 Бот запущен и готов к работе!")
bot.polling(none_stop=True)
