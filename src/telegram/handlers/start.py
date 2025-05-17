import os
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

import src.telegram.keyboards as kb
from src.database.queries.orm import db

router = Router()

current_working_dir = os.getcwd()

@router.message(CommandStart())
@router.message(F.text == "🏠 Меню")
async def cmd_start(message: Message):
    chat_id = message.chat.id
    if not await db.user_in_db(chat_id):
        await db.add_user(chat_id)
        file_path = Path(__file__).parent / "start_photo.jpg"
        await message.answer_photo(
            photo=FSInputFile(
                path=file_path
            ),
            caption="Приветсвенный текст",
            reply_markup=kb.pinned_menu
        )
        
    await message.answer('<Меню>', 
                         reply_markup=await kb.start_menu(chat_id))