import logging
from aiogram import Bot
from arq import cron
from src.database.config import settings
from src.redis import pool_settings
from src.scheduler.tasks import (send_orders,
                                send_daily_user_stats,
                                send_notf_to_invalid_token)

async def startup(ctx):
    ctx['bot'] = Bot(settings.BOT_TOKEN)

async def shutdown(ctx):
    await ctx['bot'].session.close()



class WorkerSettings:
    redis_settings = pool_settings
    on_startup = startup
    on_shutdown = shutdown
    cron_jobs = [
        cron(send_orders, second=0),
        cron(send_daily_user_stats, hour=20, minute=00),
        cron(send_notf_to_invalid_token, hour=8, minute=0),
    ]