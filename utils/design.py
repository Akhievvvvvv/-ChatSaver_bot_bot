from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_message():
    return (
        "🌟 <b>Добро пожаловать в ChatSaver!</b>\n\n"
        "🛡️ Этот бот сохраняет удалённые сообщения, исчезающие фото/видео/голосовые, "
        "а также весь чат, если его удалили у всех.\n\n"
        "Нажми кнопку ниже, чтобы активировать бота 👇"
    )

def activate_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Активировать бота", callback_data="activate")]
    ])

def instruction_message():
    return (
        "✅ <b>Бот активирован!</b>\n\n"
        "🔹 Бесплатный пробный период: 7 дней\n"
        "🔹 Когда кто-то удалит сообщение — ты увидишь кнопку «👀 Посмотреть»\n"
        "🔹 После пробного периода — 99₽/мес\n\n"
        "🔥 Наслаждайся и не упусти ни одного удалённого сообщения!"
    )

def payment_info():
    return (
        "💳 <b>Данные для оплаты:</b>\n\n"
        "📱 Номер: <code>+7 932 222 99 30</code>\n"
        "🏦 Банк: Ozon Bank\n"
        "💰 Стоимость: 99₽ в месяц"
    )

def payment_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплатил(а)", callback_data="paid")]
    ])
