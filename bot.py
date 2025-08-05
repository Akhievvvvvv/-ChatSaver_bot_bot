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

def keyboard_activate():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("⚙️ Активировать бота", callback_data="activate_bot"))
    return kb

def keyboard_view_payment():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("👀 Посмотреть", callback_data="view_payment"))
    return kb

def keyboard_confirm_payment(user_id: int):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_{user_id}"))
    return kb

@dp.message_handler(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or 'друг'
    users[user_id] = {"start_time": datetime.now(), "active": True}

    text = (
        f"👋 Привет, @{username}!\n\n"
        "Добро пожаловать в <b>ChatSaver Bot</b> — твой помощник для сохранения удалённых сообщений, фото, видео и всего чата 💬✨\n\n"
        "🚀 Что бот умеет?\n"
        "• Сохраняет удалённые сообщения 📥\n"
        "• Сохраняет самоудаляющиеся фото, видео и голосовые 📸\n"
        "• Сохраняет чат, даже если он удалён у всех 🗑️\n\n"
        "🆓 Первая неделя — <b>абсолютно бесплатна!</b>\n\n"
        "Нажми кнопку ниже, чтобы узнать, как его активировать ⤵️"
    )
    await message.answer(text, reply_markup=keyboard_activate(), parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == "activate_bot")
async def activate_bot_handler(callback_query: types.CallbackQuery):
    text = (
        "📌 <b>Как активировать ChatSaver Bot:</b>\n\n"
        "1️⃣ Добавь бота в нужный чат и разреши читать сообщения.\n"
        "2️⃣ Бот автоматически начнёт сохранять удалённые сообщения и медиа.\n"
        "3️⃣ После бесплатной недели бот приостановится.\n"
        "4️⃣ Если кто-то удалит сообщение — ты получишь уведомление с кнопкой 👀 Посмотреть.\n"
        "5️⃣ После нажатия на кнопку ты увидишь мои реквизиты:\n"
        "💳 <code>+7 932 222 99 30</code> (Ozon Bank)\n"
        "💰 <b>99₽/мес</b>\n"
        "6️⃣ Отправь сообщение: <b>Оплатил(а)</b> — и админ активирует бота 🛠️\n\n"
        "Приятного использования! 🤖"
    )
    await callback_query.message.edit_text(text, parse_mode="HTML")

@dp.message_handler(lambda message: message.text.lower() == "оплатил(а)")
async def payment_message_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    text = (
        f"💸 Пользователь <b>@{username}</b> отправил сообщение об оплате.\n"
        f"ID: <code>{user_id}</code>"
    )
    await bot.send_message(ADMIN_GROUP_ID, text, parse_mode="HTML", reply_markup=keyboard_confirm_payment(user_id))
    await message.reply("⏳ Спасибо! Ожидай подтверждение от администратора.", parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
async def confirm_payment_handler(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    if user_id in users:
        users[user_id]["active"] = True
        users[user_id]["start_time"] = datetime.now()
        await bot.send_message(user_id, "✅ Подписка активирована! Спасибо за оплату 💖")
        await callback_query.answer("Пользователь активирован.")
    else:
        await callback_query.answer("Пользователь не найден.", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "view_payment")
async def view_payment_handler(callback_query: types.CallbackQuery):
    text = (
        "💳 <b>Реквизиты для оплаты:</b>\n\n"
        "📱 <code>+7 932 222 99 30</code>\n"
        "🏦 <b>Ozon Bank</b>\n"
        "💰 <b>99₽ / месяц</b>\n\n"
        "После оплаты напиши: <b>Оплатил(а)</b>, и админ активирует подписку 🙌"
    )
    await callback_query.message.edit_text(text, parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
