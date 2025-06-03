from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from src.telegram.utils.texts import Text
import src.telegram.keyboards as kb


router = Router()

@router.callback_query(F.data == 'guide')
async def help_but(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(Text.GUIDE, reply_markup=kb.order_example)
    #await callback.message.edit_text('ᅠ', reply_markup=kb.help_kb)

@router.callback_query(F.data == 'text_guide')
async def text_guide(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Nothing') 

@router.callback_query(F.data == "order_example")
async def send_order_example(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(Text.ORDER_EXAMPLE, reply_markup=kb.to_menu, parse_mode=ParseMode.HTML)