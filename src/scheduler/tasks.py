import logging
from aiogram import Bot
import aiohttp
import asyncio
import json
from numbers import Integral, Real
from zoneinfo import ZoneInfo
from datetime import date, timedelta, datetime
from aiogram.enums import ParseMode

from src.telegram.bot import bot
from src.telegram.keyboards import pinned_menu
from src.database.queries.orm import db
from src.wildberries.models import wb_client, Card
from src.redis import redis, redis_for_invalid
from src.telegram.utils.texts import Text

semaphore = asyncio.Semaphore(10)

DAILY_STATS_FIELDS = {
    'daily_count': ("Всего заказов", ''),
    'daily_total': ("Сумма выручки", '₽'),
    'daily_selfcost': ("Сумма себестоимостей", '₽'),
    'daily_commission': ("Общая комиссия Wildberries", '₽'),
    'daily_logistic_cost': ("Общая стоимость логистики", '₽'),
    'daily_cost_tax': ("Общая сумма налога", '₽'),
    'daily_profit': ("Общая прибыль", '₽'),
}

async def yesterday():
    return datetime.now(ZoneInfo("Europe/Moscow")).date() - timedelta(days=1) 

async def daily_report(chat_id: int) -> str:
    yesterday_ = (await yesterday()).isoformat()
    stats_key = f"user_stats:{chat_id}:{yesterday_}"

    pipe = redis.pipeline()
    for field in DAILY_STATS_FIELDS:
        pipe.hget(stats_key, field)
    values = await pipe.execute()

    stats_dict = dict(zip(DAILY_STATS_FIELDS.keys(), values))

    report_lines = [f"Отчёт за {yesterday_}:"]
    for key, (label, suffix) in DAILY_STATS_FIELDS.items():
        val = stats_dict.get(key)
        if val:
            val = round(float(val), 2)
        else:
            val = 0 
        report_lines.append(f"<b>{label}</b>: <code>{val}{suffix}</code>")

    await redis.delete(stats_key)

    return "\n".join(report_lines)

async def collect_stats(chat_id: int, card: Card) -> None:
    today = date.today().isoformat()
    stats_key = f"user_stats:{chat_id}:{today}"

    updates = {
        'daily_count': 1,
        'daily_total': card.price_before_spp,
        'daily_selfcost': card.selfcost,
        'daily_cost_tax': card.cost_tax,
        'daily_logistic_cost': card.logistic_cost,
        'daily_profit': card.profit,
        'daily_commission': card.wb_commission,
    }

    pipe = redis.pipeline()
    
    for key, value in updates.items():
        if isinstance(value, Integral):
            pipe.hincrby(stats_key, key, value)
        elif isinstance(value, Real):
            value = round(float(value), 2)
            pipe.hincrbyfloat(stats_key, key, value)
        else:
            raise TypeError(f"Unsupported value type for {key}: {type(value)}")
    await pipe.execute()

async def reset_daily_stats(chat_id: int) -> None:
    """Удаляет все поля статистики пользователя"""
    date = (await yesterday()).isoformat()
    stats_key = f"user_stats:{chat_id}:{date}"
    await redis.delete(stats_key)

async def user_report(ctx, user: tuple[int, str]):
       
    bot = ctx['bot']
    chat_id, wb_token = user
    try:
        async with semaphore:        
            key_redis = f'orders:{chat_id}'
            headers = {'Authorization': wb_token}
            today = date.today().isoformat()

            async with aiohttp.ClientSession(headers=headers) as session:
                cur_orders = await wb_client.get_new_orders(session)
                for order in cur_orders:
                    order_date = order['createdAt'][:10]
                    order_unique_id = str(order['rid'])
                    if order_date == today:
                        if not await redis.sismember(key_redis, order_unique_id):
                            card = await Card.create(session, order, chat_id)
                            await redis.sadd(key_redis, order_unique_id)
                            await collect_stats(chat_id, card)

                            report_text = await card.create_report(chat_id)
                            await bot.send_message(chat_id, report_text, parse_mode=ParseMode.HTML)
                            logging.info(f"Сообщение отправлено: {chat_id} - {card.article}")

    except aiohttp.ClientResponseError as e:
        if e.status in (401, 403):
            await redis_for_invalid.set(f"ProblemToken:{chat_id}", e.status)
            if e.status == 401:
                msg = Text.STATUS_401
            else:
                msg = Text.STATUS_403
            await bot.send_message(chat_id, msg, reply_markup=pinned_menu)
            await db.set_wb_token_to_invalid(chat_id)
        elif e.status == 429:
            pass

                        

#Задачи

async def send_notf_to_invalid_token(ctx):
    bot = ctx['bot']
    for key in redis_for_invalid.scan_iter("InvalidToken:*"):
        chat_id = int(key.decode().split(":")[1])
        status_value = redis_for_invalid.get(key)
        msg = await Text.text_reminder_invalid_token(status_value)
        if db.check_sub_status(chat_id):
            await bot.send_message(chat_id, msg)

async def send_daily_user_stats(ctx):
    bot = ctx['bot']
    active_users = await db.sub_users_list()
    for user in active_users:
        chat_id = user[0]
        report = await daily_report(chat_id)
        await bot.send_message(chat_id, text=report, parse_mode=ParseMode.HTML)
        await reset_daily_stats(chat_id)

async def send_orders(ctx):
    try:
        active_users = await db.sub_users_list()
        logging.info(f"Выбрано пользователей: {len(active_users)}")
        tasks = [asyncio.create_task(user_report(ctx, user)) for user in active_users]
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.warning(f"Критическая ошибка в send_orders: {e}")
