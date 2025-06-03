from decimal import Decimal
from sqlalchemy import DateTime, BigInteger, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from src.database.database import Base


class UsersOrm(Base):
    __tablename__ = 'users'

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    wb_token: Mapped[str | None]
    tax: Mapped[int] = mapped_column(default=0)
    send_notifications: Mapped[bool] = mapped_column(default=False)
    trial: Mapped[bool] = mapped_column(default=True)
    subscription_until: Mapped[datetime] = mapped_column(
        default=lambda: (datetime.now(ZoneInfo("Europe/Moscow"))).replace(tzinfo=None)
    )

class UsersArticles(Base):
    __tablename__ = 'users_articles'
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    article_code: Mapped[str] = mapped_column(unique=True)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00)
