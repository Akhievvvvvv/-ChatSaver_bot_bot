import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import CommandStart
from datetime import datetime, timedelta
import asyncio

from config import TOKEN, ADMIN_GROUP_ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}  # user_id: {"start_date": datetime, "paid": bool}


# 👋 Приветствие
@dp.message_handler(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"ID {user_id}"

    if user_id not in user_data:
        user_data[user_id] = {
            "start_date": datetime.now(),
            "paid": False
        }

    text = (
        f"👋 Привет, @{username}!\n\n"
        f"Добро пожаловать в <b>ChatSaver Bot</b> — твой помощник для сохранения удалённых сообщений, "
        f"самоудаляющихся медиа и всего чата.\n\n"
        f"🚀 <b>Что бот умеет?</b>\n"
        f"• Сохраняет удалённые сообщения 📥\n"
        f"• Сохраняет самоудаляющиеся фото, видео и голосовые 📸\n"
        f"• Сохраняет чат, даже если он удалён у всех 🗑️\n\n"
        f"🆓 Тебе доступна бесплатная неделя использования!\n\n"
        f"Нажми кнопку ниже, чтобы активировать бота и получить инструкцию 👇"
    )

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("⚙️ Активировать бота", callback_data="activate")
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


# 📌 Инструкция
@dp.callback_query_handler(lambda c: c.data == "activate")
async def show_instruction(callback_query: types.CallbackQuery):
    await callback_query.answer()
    text = (
        "📌 <b>Как активировать ChatSaver Bot:</b>\n\n"
        "1️⃣ Добавь бота в нужный чат и разреши читать сообщения.\n"
        "2️⃣ Он автоматически сохранит удалённые сообщения и медиа.\n"
        "3️⃣ После 7 дней использования, если кто-то что-то удалит — "
        "тебе придёт сообщение с кнопкой 👀 <b>Посмотреть</b>.\n"
        "4️⃣ После нажатия ты увидишь реквизиты для оплаты:\n"
        "💳 +7 932 222 99 30\n🏦 Ozon Bank\n💰 99₽/мес\n"
        "5️⃣ Отправь сообщение <b>Оплатил(а)</b> — и админ подтвердит активацию.\n\n"
        "🎉 Всё просто и удобно!"
    )
    await callback_query.message.answer(text, parse_mode="HTML")


# ⛔ Удалённое сообщение при окончании пробного периода
@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_deleted_message(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id)

    if not data:
        return

    now = datetime.now()
    start = data["start_date"]
    paid = data["paid"]

    if not paid and now > start + timedelta(days=7):
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("👀 Посмотреть", callback_data="pay_info")
        )
        await message.answer(
            "❗ Кто-то удалил сообщение, но оно скрыто.\n"
            "Для просмотра нужно продлить доступ.",
            reply_markup=keyboard
        )


# 💳 Показать реквизиты
@dp.callback_query_handler(lambda c: c.data == "pay_info")
async def show_payment_info(callback_query: types.CallbackQuery):
    await callback_query.answer()
    text = (
        "💳 <b>Оплата подписки</b>\n\n"
        "+7 932 222 99 30\n"
        "🏦 Ozon Bank\n"
        "💰 99₽ / мес\n\n"
        "После оплаты отправь сообщение: <b>Оплатил(а)</b>."
    )
    await callback_query.message.answer(text, parse_mode="HTML")


# ✅ Подтверждение оплаты
@dp.message_handler(lambda m: m.text.lower() == "оплатил" or m.text.lower() == "оплатил(а)")
async def confirm_payment(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"ID {user_id}"
    text = f"💰 Пользователь {username} отправил сообщение об оплате.\n\n✅ Подтвердить активацию?"

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"approve_{user_id}")
    )

    await bot.send_message(chat_id=ADMIN_GROUP_ID, text=text, reply_markup=keyboard)


# 🔓 Активация подписки админом
@dp.callback_query_handler(lambda c: c.data.startswith("approve_"))
async def approve_payment(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split("_")[1])
    user_data[user_id]["paid"] = True

    await bot.send_message(user_id, "✅ Доступ к боту успешно активирован! Спасибо за оплату. 🤝")
    await callback_query.answer("Подтверждено ✅")


if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
