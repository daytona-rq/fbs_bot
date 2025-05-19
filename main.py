import asyncio
import logging
from aiogram import Dispatcher, Bot

from arq import create_pool
from src.redis import pool_settings
from src.telegram.bot import bot
from src.telegram.handlers import setup_routers
from src.database.queries.orm import db

dp = Dispatcher()



async def main():
    await db.create_tables()
    redis_pool = await create_pool(pool_settings)
    dp.include_router(setup_routers())
    await dp.start_polling(bot,
                           arqredis=redis_pool)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Session closed')