import json
from fastapi import APIRouter, Request, HTTPException, Header, Response
from fastapi.responses import JSONResponse
from .schemas import YooKassaWebhook
import hmac
import hashlib
import os
import logging

from yookassa.domain.notification import WebhookNotification
from src.telegram.bot import bot
from src.database.database import async_session_maker
from src.database.config import settings
from src.database.queries.orm import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/yookassa", tags=["Webhooks"])

YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

@router.post("/webhook")
async def webhook_handler(request: Request):
    event_json = await request.json()
    payment_status = event_json['event']
    chat_id = int(event_json['object']['metadata']['chat_id'])
    payment_id = event_json['object']['id']
    if payment_status == 'payment.succeeded':
        date_to = (await db.subscribe(chat_id)).strftime("%H:%M %d.%m.%Y")

        await bot.send_message(chat_id, 
                               text=f'✅ Поздравляем, подписка оформлена до {date_to}\n\ID вашей операции: {payment_id}')
    if payment_status == 'payment.canceled':
        await bot.send_message(chat_id, text='❓ Платеж был отменён')
    return JSONResponse(content={"status": "success"}, status_code=200)
