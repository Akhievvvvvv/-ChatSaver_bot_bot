from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from utils import db, design

router = Router()

def register_handlers(dp, bot):
    dp.include_router(router)

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        text=design.start_message(),
        reply_markup=design.activate_button()
    )

@router.callback_query(F.data == "activate")
async def activate_bot(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.start_trial(user_id)
    await callback.message.edit_text(
        design.instruction_message()
    )

@router.message(F.text == "👀 Посмотреть")
async def show_payment_info(message: Message):
    await message.answer(
        design.payment_info(),
        reply_markup=design.payment_buttons()
    )

@router.callback_query(F.data == "paid")
async def confirm_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.activate_subscription(user_id)
    await callback.message.edit_text("✅ Спасибо! Подписка активирована.")
