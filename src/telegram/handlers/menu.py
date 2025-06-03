from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from src.telegram.utils.utils import is_sub
from src.telegram.utils.texts import Text
import src.telegram.keyboards as kb


router = Router()

@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    await callback.answer('')
    chat_id = callback.message.chat.id
    await callback.message.edit_text('ᅠ', reply_markup=await kb.start_menu(chat_id))

@router.callback_query(F.data == 'user_settings')
async def user_info(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    await callback.answer('')
    if await is_sub(callback, chat_id):
        await callback.message.edit_text(Text.SETTINGS_BUTT, reply_markup=await kb.settings_kb(chat_id))



