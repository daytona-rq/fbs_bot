from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.queries.orm import db
from src.telegram.keyboards import to_menu, MyCallback
from src.wildberries.upd_articles import update_user_article
from src.redis import redis_for_invalid

class upd_token(StatesGroup):
    wb_token_state = State()

router = Router()

@router.callback_query(MyCallback.filter(F.string == "notification"))
async def toggle_notifications(callback: CallbackQuery, callback_data: MyCallback):
    chat_id = callback.message.chat.id
    status = callback_data.value
    await callback.answer('')
    await db.toggle_notifications(chat_id)
    if status:
        await callback.message.edit_text('Уведомления выключены', reply_markup=to_menu)
    else:
        await callback.message.edit_text('Уведомления включены', reply_markup=to_menu)

@router.callback_query(F.data == 'wb_token')
async def upd_first_step(callback: CallbackQuery, state: FSMContext):
    await state.set_state(upd_token.wb_token_state)
    await callback.answer('')
    await callback.message.answer('Введите ваш токен API Wildberries')

@router.message(upd_token.wb_token_state)
async def upd_second_step(message: Message, state: FSMContext):
    wb_token = message.text
    chat_id = message.chat.id
    await db.upd_wb_token(chat_id, wb_token)
    if redis_for_invalid.exists(f"InvalidToken:{chat_id}"):
        redis_for_invalid.delete(f"InvalidToken:{chat_id}")
    await message.answer('Токен обновлён', reply_markup=to_menu)
    await state.clear()

@router.callback_query(F.data == 'upd_arts')
async def upd_articles(callback: CallbackQuery):
    await callback.answer('')
    chat_id = callback.message.chat.id
    await update_user_article(chat_id)
    await callback.message.answer('Артикулы обновлены')