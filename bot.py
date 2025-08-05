import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import CommandStart

API_TOKEN = '7996519892:AAGl1jJS5pbOmJCBiJDiyYmhWqEmRn6ixmM'
ADMIN_GROUP_ID = -1002593269045
FREE_PERIOD_DAYS = 7

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users = {}

def get_keyboard_start():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("⚙️ Активировать бота", callback_data="activate_bot")
    )

def get_payment_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("👀 Посмотреть", callback_data="view_payment")
    )

def get_confirm_keyboard(user_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_{user_id}")
    )

@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    users[user_id] = {"start_time": datetime.now(), "active": True}

    welcome = f"""
👋 Привет, @{username if username else 'друг'}!

Добро пожаловать в <b>ChatSaver Bot</b> — твой помощник для сохранения удалённых сообщений, фото, видео и всего чата 💬✨

🚀 Что бот умеет?
• Сохраняет удалённые сообщения 📥
• Сохраняет самоудаляющиеся фото, видео и голосовые 📸
• Сохраняет чат, даже если он удалён у всех 🗑️

🆓 Первая неделя — <b>абсолютно бесплатна!</b>

Нажми на кнопку ниже, чтобы узнать, как его активировать ⤵️
"""
    await message.answer(welcome, reply_markup=get_keyboard_start(), parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data == "activate_bot")
async def activate_bot_callback(callback_query: types.CallbackQuery):
    instruction = """
📌 <b>Как активировать ChatSaver Bot:</b>

1️⃣ Добавь бота в нужный чат и разреши читать сообщения  
2️⃣ Он автоматически начнёт сохранять удалённые сообщения и медиа  
3️⃣ После бесплатной недели бот приостановится  
4️⃣ Если кто-то удалит сообщение — ты получишь уведомление с кнопкой 👀 Посмотреть  
5️⃣ После нажатия на неё ты увидишь мои реквизиты:
💳 <code>+7 932 222 99 30</code> (Ozon Bank)  
💰 <b>99₽/мес</b>  
6️⃣ Отправь сообщение: <b>Оплатил(а)</b> — и админ активирует бота 🛠️

Приятного использования! 🤖
"""
    await callback_query.message.edit_text(instruction, parse_mode="HTML")

@dp.message_handler(lambda message: message.text.lower() == "оплатил(а)")
async def paid_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"id: {user_id}"
    text = f"💸 Пользователь <b>@{username}</b> отправил сообщение об оплате.\n\nID: <code>{user_id}</code>"

    await bot.send_message(ADMIN_GROUP_ID, text, parse_mode='HTML', reply_markup=get_confirm_keyboard(user_id))
    await message.reply("⏳ Спасибо! Ожидай подтверждение от администратора.", parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
async def confirm_payment_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    users[user_id]["active"] = True
    users[user_id]["start_time"] = datetime.now()
    await bot.send_message(user_id, "✅ Подписка активирована! Спасибо за оплату 💖")

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def handle_deleted_message(message: types.Message):
    user_id = message.from_user.id
    user_data = users.get(user_id)

    if not user_data:
        return

    start_time = user_data["start_time"]
    is_active = user_data["active"]
    if datetime.now() > start_time + timedelta(days=FREE_PERIOD_DAYS):
        if is_active:
            users[user_id]["active"] = False  # остановить бота
        await message.answer(
            "🔒 Кто-то что-то удалил, но сообщение скрыто.\n\n"
            "Нажми 👇 чтобы получить доступ:",
            reply_markup=get_payment_keyboard()
        )

@dp.callback_query_handler(lambda c: c.data == "view_payment")
async def view_payment_callback(callback_query: types.CallbackQuery):
    text = """
💳 <b>Реквизиты для оплаты:</b>

📱 <code>+7 932 222 99 30</code>  
🏦 <b>Ozon Bank</b>  
💰 <b>99₽ / месяц</b>

После оплаты напиши: <b>Оплатил(а)</b>, и админ активирует подписку 🙌
"""
    await callback_query.message.edit_text(text, parse_mode="HTML")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
