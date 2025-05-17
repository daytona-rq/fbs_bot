from aiogram.types import CallbackQuery

from src.database.queries.orm import db
from src.telegram.utils.texts import Text
from src.telegram import keyboards as kb

async def is_sub(callback: CallbackQuery, chat_id):
    sub_date = await db.check_sub_status(chat_id)
    if not sub_date:
        await callback.message.edit_text(
                               Text.NOT_SUB,
                               reply_markup=kb.sub_menu)
        return False
    return True